"""Creation of consensus sequences from repetitive reads."""
from collections import namedtuple
from concurrent.futures import ProcessPoolExecutor
import functools
import os
from timeit import default_timer as now
import warnings

import mappy
import numpy as np
import parasail
import pysam
import spoa

import medaka.align
import medaka.common
import medaka.medaka

Subread = namedtuple('Subread', 'name seq')
Alignment = namedtuple('Alignment', 'rname qname flag rstart seq cigar')


class Read(object):
    """Functionality to extract information from a read with subreads."""

    def __init__(self, name, subreads):
        """Initialize repeat read analysis.

        :param name: read name.
        :param subreads: list of subreads.

        """
        self.name = name
        self.subreads = subreads
        if len(self.subreads) == 0:
            raise ValueError(
                "Cannot create a read with fewer than 0 subreads.")
        self.consensus = self.subreads[0].seq
        # SW alignments of subreads to consensus
        self._alignments = None
        self._alignments_valid = False
        # orientation of subreads wrt consensus
        self._orient = None
        # has initialize() been run (i.e. are the above filled in)
        self._initialized = False
        # has a consensus been run
        self.consensus_run = False
        # enable use of alternative aligners by changing name.
        # parasail align functions not pickleable so cause issues with
        # multiprocessing if set as a direct attribute.
        # instead, create the aligner on demand.
        self.parasail_aligner_name = 'sw_trace_striped_16'

    @property
    def parasail_aligner_name(self):
        """Return parasail alignment function name (str)."""
        return self._parasail_aligner_name

    @parasail_aligner_name.setter
    def parasail_aligner_name(self, value):
        if hasattr(parasail, value) and callable(getattr(parasail, value)):
            self._parasail_aligner_name = value
        else:
            raise ValueError(f'{value} is not a valid parasail function.')

    @property
    def parasail_aligner(self):
        """Return functools.partial-wrapped parasail alignment function."""
        return functools.partial(
            getattr(parasail, self.parasail_aligner_name),
            open=8, extend=4, matrix=parasail.dnafull
        )

    def initialize(self):
        """Calculate initial alignments of subreads to scaffold read."""
        # we find initial alignments with parasail as mappy may not find some
        if not self._initialized:
            self._alignments = self.orient_subreads()
            self._alignments_valid = True
            self._initialized = True
        return None

    @classmethod
    def from_fastx(cls, fastx, name=None):
        """Create a Read from a fasta/q file.

        :param fastx: input file path.
        :param name: name of Read. If not given the filename will be used.

        """
        try:
            read = next(cls.multi_from_fastx(fastx, take_all=True))
        except Exception:
            raise IOError("Could not create Read from file {}.".format(fastx))
        return read

    @classmethod
    def multi_from_fastx(
            cls, fastx,
            take_all=False, read_id=None, depth_filter=1, length_filter=0):
        """Create multiple `Read` s from a fasta/q file.

        It is assumed that subreads are grouped by read and named with
        <read_id>_<subread_id>.

        :param fastx: input file path.
        :param take_all: skip check on subread_ids, take all subreads in one
            `Read`.
        :param read_id: name of `Read`. Only used for `take_all == True`. If
            not given the basename of the input file is used.
        :param depth_filter: require reads to have at least this many subreads.
        :param length_filter: require reads to have a median subread length
            above this value.

        """
        logger = medaka.common.get_named_logger("FastReader")
        depth_filter = max(1, depth_filter)
        if take_all and read_id is None:
            read_id = os.path.splitext(os.path.basename(fastx))[0]
        else:
            read_id = None
        subreads = []
        with pysam.FastxFile(fastx) as fh:
            for entry in fh:
                if not take_all:
                    cur_read_id = entry.name.split("_")[0]
                    if read_id is None:
                        read_id = cur_read_id
                    if cur_read_id != read_id:
                        if len(subreads) >= depth_filter:
                            med_length = np.median(
                                [len(x.seq) for x in subreads])
                            if med_length > length_filter:
                                yield cls(read_id, subreads)
                            else:
                                logger.debug(
                                    "Read {} has too short subreads.".format(
                                        read_id))
                        else:
                            logger.debug(
                                "Read {} has too few subreads.".format(
                                    read_id))
                        read_id = cur_read_id
                        subreads = []

                if len(entry.sequence) > 0:
                    subreads.append(Subread(entry.name, entry.sequence))

            if len(subreads) >= depth_filter:
                med_length = np.median([len(x.seq) for x in subreads])
                if med_length > length_filter:
                    yield cls(read_id, subreads)
                else:
                    logger.debug(
                        "Read {} has too short subreads.".format(read_id))
            else:
                logger.debug("Read {} has too few subreads.".format(read_id))

    @property
    def seqs(self):
        """Return a list of the subread sequences."""
        return [x.seq for x in self.subreads]

    @property
    def interleaved_subreads(self):
        """Return a list of subreads with + and - reads interleaved.

        :returns: orientations, subreads.

        The ordering may not be strictly +-+-+-..., the subreads
        are positioned such that + and - reads are both distributed
        uniformally through the list (according to their overall
        frequency).
        """
        self.initialize()
        fwd, rev = list(), list()
        for orient, subread in zip(self._orient, self.subreads):
            if orient:
                fwd.append([subread, True, 0])
            else:
                rev.append([subread, False, 0])
        for reads in fwd, rev:
            if len(reads) > 0:
                rate = 1.0 / len(reads)
                for i in range(len(reads)):
                    reads[i][2] = rate * i
        reads = sorted(fwd + rev, key=lambda x: x[2])
        reads, orients, garbage = zip(*reads)
        return orients, reads

    @property
    def nseqs(self):
        """Return the number of subreads contained in the read."""
        return len(self.subreads)

    def poa_consensus(self, method='spoa', spoa_min_coverage=None):
        """Create a consensus sequence for the read."""
        self.initialize()
        seqs = list()
        if self.consensus_run:
            # running POA for the second time: use the output from
            # the previous run as first read in the list
            seqs.append(self.consensus)
        for orient, subread in zip(*self.interleaved_subreads):
            if orient:
                seq = subread.seq
            else:
                seq = medaka.common.reverse_complement(subread.seq)
            seqs.append(seq)
        if method == 'spoa':
            consensus_seq, _ = spoa.poa(
                seqs,
                genmsa=False,
                min_coverage=spoa_min_coverage
            )
        elif method == 'abpoa':
            import pyabpoa as pa
            abpoa_aligner = pa.msa_aligner(aln_mode='g')
            result = abpoa_aligner.msa(seqs, out_cons=True, out_msa=False)
            consensus_seq = result.cons_seq[0]
        else:
            raise ValueError('Unrecognised method: {}.'.format(method))
        self.consensus = consensus_seq
        self._alignments_valid = False
        self.consensus_run = True
        return consensus_seq

    def orient_subreads(self):
        """Find orientation of subreads with respect to consensus sequence.

        :returns: `medaka.align.Alignment` s of subreads to consensus.

        """
        # TODO: use a profile here
        # TODO: refactor with align_to_template
        self._orient = []
        alignments = []
        for sr in self.subreads:
            rc_seq = medaka.common.reverse_complement(sr.seq)
            result_fwd = self.parasail_aligner(sr.seq, self.consensus)
            result_rev = self.parasail_aligner(rc_seq, self.consensus)
            is_fwd = result_fwd.score > result_rev.score
            self._orient.append(is_fwd)
            result = result_fwd if is_fwd else result_rev
            seq = sr.seq if is_fwd else rc_seq
            if result.cigar.beg_ref >= result.end_ref or \
                    result.cigar.beg_query >= result.end_query:
                # unsure why this can happen
                continue
            rstart, cigar = medaka.align.parasail_to_sam(result, seq)
            flag = 0 if is_fwd else 16
            aln = Alignment(
                'consensus_{}'.format(self.name), sr.name,
                flag, rstart, seq, cigar)
            alignments.append(aln)
        return alignments

    def align_to_template(self, template, template_name):
        """Align subreads to a template sequence using Smith-Waterman.

        :param template: sequence to which to align subreads.
        :param template_name: name of template sequence.

        :returns: `Alignment` tuples.

        """
        self.initialize()
        alignments = []
        for orient, sr in zip(self._orient, self.subreads):
            if orient:
                seq = sr.seq
            else:
                seq = medaka.common.reverse_complement(sr.seq)
            result = self.parasail_aligner(seq, template)

            if result.cigar.beg_ref >= result.end_ref or \
                    result.cigar.beg_query >= result.end_query:
                # unsure why this can happen
                continue
            rstart, cigar = medaka.align.parasail_to_sam(result, seq)
            flag = 0 if orient else 16
            aln = Alignment(template_name, sr.name, flag, rstart, seq, cigar)
            alignments.append(aln)
        return alignments

    def mappy_to_template(self, template, template_name, align=True):
        """Align subreads to a template sequence using minimap.

        :param template: sequence to which to align subreads.
        :param template_name: name of template sequence.
        :param align: retrieve cigar string (else produce paf)

        :returns: `Alignment` tuples.

        """
        if not align:
            # align False requires forked minimap2, and isn't much faster for
            # a small number of sequences due to index construction time.
            warnings.warn("`align` is ignored", DeprecationWarning)
        alignments = []
        aligner = mappy.Aligner(seq=template, preset='map-ont')
        for sr in self.subreads:
            try:
                hit = next(aligner.map(sr.seq))
            except StopIteration:
                continue
            else:
                flag = 0 if hit.strand == 1 else 16
                if hit.strand == 1:
                    seq = sr.seq
                else:
                    seq = medaka.common.reverse_complement(sr.seq)
                clip = [
                    '' if x == 0 else '{}S'.format(x)
                    for x in (hit.q_st, len(sr.seq) - hit.q_en)]
                if hit.strand == -1:
                    clip = clip[::-1]
                cigstr = ''.join((clip[0], hit.cigar_str, clip[1]))
                aln = Alignment(
                    template_name, sr.name, flag, hit.r_st, seq, cigstr)
                alignments.append(aln)
                hit = None
        return alignments


def write_bam(fname, alignments, header, bam=True):
    """Write a `.bam` file for a set of alignments.

    :param fname: output filename.
    :param alignments: a list of `Alignment` tuples.
    :param header: bam header
    :param bam: write bam, else sam

    """
    mode = 'wb' if bam else 'w'
    if isinstance(header, dict):
        header = pysam.AlignmentHeader.from_dict(header)
    with pysam.AlignmentFile(fname, mode, header=header) as fh:
        for subreads in alignments:
            for aln in sorted(subreads, key=lambda x: x.rstart):
                a = medaka.align.initialise_alignment(
                    aln.qname, header.get_tid(aln.rname),
                    aln.rstart, aln.seq,
                    aln.cigar, aln.flag)
                fh.write(a)
    if mode == 'wb':
        pysam.index(fname)


def _read_worker(read, align=True, method='spoa', spoa_min_coverage=None):
    read.initialize()
    if read.nseqs > 2:  # skip if there is only one subread
        for it in range(2):
            read.poa_consensus(
                method=method, spoa_min_coverage=spoa_min_coverage
            )
    aligns = None
    if align:
        aligns = read.mappy_to_template(
            template=read.consensus, template_name=read.name)
    return read.name, read.consensus, aligns


def ignore_exception(func, *args, **kwargs):
    """Call a function ignoring any exceptions."""
    logger = medaka.common.get_named_logger('Smolecule')
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.warning(e)
    return None


def poa_workflow(reads, threads, method='spoa', spoa_min_coverage=None):
    """Worker function for processing repetitive reads.

    :param reads: list of `Read` s.
    :param threads: number of threads to use for processing.

    """
    # TODO: this is quite memory inefficient, but we can only build the header
    #       by seeing everything.
    logger = medaka.common.get_named_logger('POAManager')
    header = {'HD': {'VN': 1.0}, 'SQ': []}
    consensuses = []
    alignments = []

    worker = functools.partial(
        ignore_exception,
        _read_worker,
        method=method,
        spoa_min_coverage=spoa_min_coverage,
    )
    with ProcessPoolExecutor(max_workers=threads) as executor:
        for res in executor.map(worker, reads):
            if res is None:
                continue
            rname, consensus, aligns = res
            logger.debug('Finished {}.'.format(rname))
            if consensus is not None:
                header['SQ'].append({
                    'LN': len(consensus),
                    'SN': rname})
                consensuses.append([rname, consensus])
                alignments.append(aligns)
        logger.info(
            "Created {} consensus with {} alignments.".format(
                len(consensuses), len(alignments)))
    return header, consensuses, alignments


class MyArgs:
    """Wrap the given args with defaults for prediction function."""

    # these need to be class attrs
    args = None
    defaults = None

    def __init__(self, args, defaults):
        """Initialize the class."""
        self.args = args
        self.defaults = defaults

    def __getattr__(self, attr):
        """Get the standard argument, or default if not present."""
        try:
            return getattr(self.args, attr)
        except AttributeError:
            return getattr(self.defaults, attr)


def main(args):
    """Entry point for repeat read consensus creation."""
    print(args)
    parser = medaka.medaka.medaka_parser()
    defaults = parser.parse_args([
        "inference", medaka.medaka.CheckBam.fake_sentinel,
        "fake_out"])

    args = MyArgs(args, defaults)

    logger = medaka.common.get_named_logger('Smolecule')
    if args.chunk_ovlp >= args.chunk_len:
        raise ValueError(
            'chunk_ovlp {} must be smaller than chunk_len {}'.format(
                args.chunk_ovlp, args.chunk_len))
    medaka.common.mkdir_p(args.output, info='Results will be overwritten.')

    def _multi_file_reader():
        for fname in args.fasta:
            try:
                yield Read.from_fastx(fname)
            except Exception:
                pass

    if len(args.fasta) > 1:
        logger.info(
            "Given {} input files, assuming one read per file.".format(
                len(args.fasta)))
        reads = _multi_file_reader()
    else:
        logger.info(
            "Given one input file, subreads are assumed "
            "to be grouped by read.")
        reads = Read.multi_from_fastx(
            args.fasta[0], depth_filter=args.depth, length_filter=args.length)

    logger.info(
        "Running {} pre-medaka consensus for all reads.".format(args.method))
    t0 = now()
    header, consensuses, alignments = poa_workflow(
        reads,
        args.threads,
        method=args.method,
        spoa_min_coverage=args.spoa_min_coverage,
    )
    t1 = now()

    logger.info(
        "Writing medaka input bam for {} reads.".format(len(alignments)))
    bam_file = os.path.join(args.output, 'subreads_to_spoa.bam')
    write_bam(bam_file, alignments, header)

    spoa_file = os.path.join(args.output, 'poa.fasta')
    with open(spoa_file, 'w') as fh:
        for rname, cons in consensuses:
            fh.write('>{}\n{}\n'.format(rname, cons))

    logger.info("Running medaka consensus.")
    t2 = now()
    args.bam = bam_file
    out_dir = args.output
    args.output = os.path.join(out_dir, 'consensus.hdf')
    # we run this in a subprocess so GPU resources are all cleaned
    # up when things are finished
    with ProcessPoolExecutor() as executor:
        fut = executor.submit(medaka.prediction.predict, args)
        _ = fut.result()
    t3 = now()

    logger.info("Running medaka stitch.")
    args.draft = spoa_file
    args.inputs = [args.output]
    out_ext = 'fasta'
    if args.qualities:
        out_ext = 'fastq'
    args.output = os.path.join(out_dir, 'consensus.{}'.format(out_ext))
    args.regions = None  # medaka consensus changes args.regions
    args.fillgaps = False
    medaka.stitch.stitch(args)
    logger.info(
        "Single-molecule consensus sequences written to {}.".format(
            args.output))
    logger.info(
        "POA time: {:.0f}s, medaka time: {:.0f}s".format(
            t1 - t0, t3 - t2))
