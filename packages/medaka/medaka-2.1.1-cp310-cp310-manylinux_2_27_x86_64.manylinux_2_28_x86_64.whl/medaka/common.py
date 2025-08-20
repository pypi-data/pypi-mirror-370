"""Commonly used data structures and functions."""
import collections
import concurrent
import enum
import errno
import fileinput
import functools
import importlib.resources
import itertools
import logging
import os
import re
import shutil
import tempfile

import intervaltree
import numpy as np
import pysam


import libmedaka


ComprAlignPos = collections.namedtuple(
    'ComprAlignPos',
    ('qpos', 'qbase', 'qlen', 'rpos', 'rbase', 'rlen'))

# mapping from integers to bases in counts matrix
base2index = {
    chr(c_int): idx for idx, c_int in
    enumerate(np.frombuffer(
        libmedaka.ffi.buffer(libmedaka.lib.plp_bases, libmedaka.lib.featlen),
        dtype=np.uint8
    ))
}


class OverlapException(Exception):
    """Exception class used when examining range overlaps."""

    pass


class Relationship(enum.Enum):
    """Enumeration of types of overlap."""

    different_ref_name = 'Samples come from different reference contigs.'
    forward_overlap = 'The end of s1 overlaps the start of s2.'
    reverse_overlap = 'The end of s2 overlaps the start of s1.'
    forward_abutted = 'The end of s1 abuts the start of s2.'
    reverse_abutted = 'The end of s2 abuts the start of s1.'
    forward_gapped = 's2 follows s1 with a gab inbetween.'
    reverse_gapped = 's1 follows s2 with a gab inbetween.'
    s2_within_s1 = 's2 is fully contained within s1.'
    s1_within_s2 = 's1 is fully contained within s2.'


# provide read only access to key sample attrs
_Sample = collections.namedtuple(
    'Sample',
    ['ref_name', 'features', 'labels', 'ref_seq', 'positions', 'label_probs',
     'depth'])


class Sample(_Sample):
    """Represents a pileup range."""

    def _asdict(self):
        # https://bugs.python.org/issue24931
        return collections.OrderedDict(zip(self._fields, self))

    def amend(self, **kwargs):
        """Create new `Sample` with some attributes changed."""
        d = self._asdict()
        for k, v in kwargs.items():
            if k not in self._fields:
                raise KeyError('Invalid key for Sample: {}'.format(k))
            d[k] = v
        return Sample(**d)

    def _get_pos(self, index):
        p = self.positions
        return p['major'][index], p['minor'][index]

    def depth_filter(self, min_depth=5):
        """Remove regions with depth < min_depth, chunking sample as needed."""
        is_enough_depth = self.depth >= min_depth
        chunks = rle(is_enough_depth)
        # discard runs with low depth.
        # we don't need to worry about creating chunk boundaries between minor
        # columns of the same major, as depth at minor positions is derived
        # from depth at last major pos.
        chunks = chunks[chunks['value']]
        for chunk in chunks:
            start = chunk['start']
            end = start + chunk['length']
            c = self.slice(slice(start, end))
            yield c

    @property
    def first_pos(self):
        """Zero-based first reference co-ordinate."""
        return self._get_pos(0)

    @property
    def last_pos(self):
        """Zero-based (end inclusive) last reference co-ordinate."""
        return self._get_pos(-1)

    @property
    def span(self):
        """Size of sample in terms of reference positions."""
        return self.last_pos[0] - self.first_pos[0]

    @property
    def is_empty(self):
        """Is pileup empty, synomymous to `sample.size == 0`."""
        return self.size == 0

    @property
    def size(self):
        """Return number of columns of pileup."""
        return len(self.positions)

    @property
    def name(self):
        """Create zero-based (end inclusive) samtools-style region string."""
        fmaj, fmin = self.first_pos
        lmaj, lmin = self.last_pos
        return '{}:{}.{}-{}.{}'.format(
            self.ref_name, fmaj, fmin, lmaj, lmin)

    @functools.cached_property
    def counts_matrix(self):
        """Create a counts matrix representation of the pileup.

        If the features are 2d, assume already a counts matrix, else calculate
        from the 3d full-alignment features
        """
        if self.features.ndim == 2:
            # if features are saved as counts matrices, simply return them
            return self.features

        # otherwise, if features have been saved as full alignment matrices
        # calculate the counts matrix from them.
        else:
            x = self.features
            positions = self.positions
            y = np.zeros((x.shape[0], 10))
            minor_inds = np.where(positions['minor'] > 0)
            major_pos_at_minor_inds = positions['major'][minor_inds]
            major_ind_at_minor_inds = np.searchsorted(
                positions['major'], major_pos_at_minor_inds, side='left')

            depth = np.sum(x[:, :, 0] != 0, axis=1)
            depth[minor_inds] = depth[major_ind_at_minor_inds]
            depth[depth == 0] = 1
            # get forward and reverse read masks by looking at strand channel
            # of features
            forward_mask = x[:, :, 2] == 1
            reverse_mask = ~forward_mask
            for base_idx, base in enumerate('pacgtd'):
                if base == 'p':
                    # ignore pad token in counts matrix
                    continue
                cur_for = np.sum(forward_mask*(x[:, :, 0] == base_idx), axis=1)
                cur_rev = np.sum(reverse_mask*(x[:, :, 0] == base_idx), axis=1)
                y[:, base2index[base]] = cur_for/depth
                y[:, base2index[base.upper()]] = cur_rev/depth
        return y

    @functools.cached_property
    def majority_vote_probs(self):
        """Calculate the base vote probabilities from the pileup."""
        b2i = base2index
        pileup = self.counts_matrix
        b = pileup[:, b2i['a']:b2i['t']+1] + pileup[:, b2i['A']:b2i['T']+1]
        # sum deletion counts (indexing in this way retains correct shape)
        d = pileup[:, b2i['d']:b2i['d']+1] + pileup[:, b2i['D']:b2i['D']+1]
        # d first as it is the deletion class, labelled 0 in training data
        out = np.concatenate([d, b], axis=-1)
        out[:, 0] += (1-out.sum(axis=-1))
        return out

    @staticmethod
    def decode_sample_name(name):
        """Decode a the result of Sample.name into a dict.

        :param key: `Sample` object.
        :returns: dict.
        """
        d = None
        name_decoder = re.compile(
            r"(?P<ref_name>.+):(?P<start>\d+\.\d+)-(?P<end>\d+\.\d+)")
        m = re.match(name_decoder, name)
        if m is not None:
            d = m.groupdict()
        return d

    @staticmethod
    def from_samples(samples):
        """Create a sample by concatenating an iterable of `Sample` objects.

        :param samples: iterable of `Sample` objects.
        :returns: `Sample` obj
        """
        samples = list(samples)
        for s1, s2 in zip(samples[0:-1], samples[1:]):
            rel = Sample.relative_position(s1, s2)
            if rel is not Relationship.forward_abutted:
                msg = (
                    'Refusing to concatenate unordered/non-abutting '
                    'samples {} and {} with relationship {}.')
                raise ValueError(msg.format(s1.name, s2.name, repr(rel)))

        # Relationship.forward_abutted guarantees all samples have the
        # same ref_name
        non_concat_fields = {'ref_name'}

        def concat_attr(attr):
            vals = [getattr(s, attr) for s in samples]
            if attr not in non_concat_fields:
                all_none = all([v is None for v in vals])
                c = np.concatenate(vals) if not all_none else None
            else:
                assert len(set(vals)) == 1
                c = vals[0]
            return c

        return Sample(**{attr:  concat_attr(attr) for attr in Sample._fields})

    @staticmethod
    def relative_position(s1, s2):
        """Check the relative position of two samples in genomic coordinates.

        :param s1, s2: `medaka.common.Sample` objs.

        :returns: `Relationship` enum member.
        """
        def ordered_abuts(s1, s2):
            """Check if end of s1 abuts the start of s2.

            i.e. is adjacent but not overlapping
            """
            s1_end_maj, s1_end_min = s1.last_pos
            s2_start_maj, s2_start_min = s2.first_pos
            if s2_start_maj == s1_end_maj + 1 and s2_start_min == 0:
                abuts = True
            elif s2_start_maj == s1_end_maj and s2_start_min == s1_end_min + 1:
                abuts = True
            else:
                abuts = False
            return abuts

        def ordered_contained(s1, s2):
            """Check if s2 is contained within s1."""
            return s2.first_pos >= s1.first_pos and s2.last_pos <= s1.last_pos

        def ordered_overlaps(s1, s2):
            """Check if end of s1 overlaps start of s2."""
            s1_end_maj, s1_end_min = s1.last_pos
            s2_start_maj, s2_start_min = s2.first_pos
            if s2_start_maj < s1_end_maj:  # overlap of major coordinates
                overlaps = True
            elif s2_start_maj == s1_end_maj and s2_start_min < s1_end_min + 1:
                # we have overlap of minor coordinates
                overlaps = True
            else:
                overlaps = False
            return overlaps

        def ordered_gapped(s1, s2):
            """Check for grap between end of s1 and start of s2."""
            s1_end_maj, s1_end_min = s1.last_pos
            s2_start_maj, s2_start_min = s2.first_pos
            gapped = False
            if s2_start_maj > s1_end_maj + 1:  # gap in major
                gapped = True
            elif (s2_start_maj > s1_end_maj and
                    s2_start_min > 0):  # missing minors
                gapped = True
            elif (s2_start_maj == s1_end_maj and
                    s2_start_min > s1_end_min + 1):  # missing minors
                gapped = True
            return gapped

        if s1.ref_name != s2.ref_name:  # different ref_names
            return Relationship.different_ref_name

        s1_ord, s2_ord = sorted((s1, s2), key=lambda x: (x.first_pos, -x.size))
        is_ordered = s1_ord.name == s1.name

        # is one sample within the other?
        if ordered_contained(s1_ord, s2_ord):
            if is_ordered:
                return Relationship.s2_within_s1
            else:
                return Relationship.s1_within_s2

        # do samples abut?
        elif ordered_abuts(s1_ord, s2_ord):
            if is_ordered:
                return Relationship.forward_abutted
            else:
                return Relationship.reverse_abutted

        # do samples overlap?
        elif ordered_overlaps(s1_ord, s2_ord):
            if is_ordered:
                return Relationship.forward_overlap
            else:
                return Relationship.reverse_overlap

        # if we got this far there should be a gap between s1_ord and s2_ord
        elif ordered_gapped(s1_ord, s2_ord):
            if is_ordered:
                return Relationship.forward_gapped
            else:
                return Relationship.reverse_gapped

        else:
            raise RuntimeError(
                'Could not calculate relative position of {} and {}'.format(
                    s1.name, s2.name))

    @staticmethod
    def overlap_indices(s1, s2):
        """Find indices by which to trim samples to allow concatenation.

        ::
            #          | end1
            s1 ............
            s2      ...............
            #          | start2


        For example:

        .. code: python

            Sample.from_samples([
                s1.slice(slice(0, end1)),
                s2.slice(slice(start2, None))])

        would join the samples without gaps or overlap.

        :param s1: First `Sample` object.
        :param s2: Second `Sample` object.

        :returns: (end1, start2
        :raises: `OverlapException` if samples do not overlap nor abut.

        """
        heuristic = False
        rel = Sample.relative_position(s1, s2)

        # trivial case
        if rel is Relationship.forward_abutted:
            return None, None, heuristic

        if rel is not Relationship.forward_overlap:
            msg = 'Cannot overlap samples {} and {} with relationhip {}'
            raise OverlapException(msg.format(s1.name, s2.name, repr(rel)))

        # find where the overlap starts (ends) in s1 (s2) indices
        ovl_start_ind1 = np.searchsorted(s1.positions, s2.positions[0])
        ovl_end_ind2 = np.searchsorted(
            s2.positions, s1.positions[-1], side='right')

        end_1_ind, start_2_ind = None, None
        pos1_ovl = s1.positions[ovl_start_ind1:]
        pos2_ovl = s2.positions[0:ovl_end_ind2]
        try:
            # the nice case where everything lines up
            if not np.array_equal(pos1_ovl['minor'], pos2_ovl['minor']):
                raise OverlapException("Overlaps are not equal in structure")
            overlap_len = len(pos1_ovl)
            # take mid point as break point
            pad_1 = overlap_len // 2
            pad_2 = overlap_len - pad_1
            end_1_ind = ovl_start_ind1 + pad_1
            start_2_ind = ovl_end_ind2 - pad_2

            contr_1 = s1.positions[ovl_start_ind1:end_1_ind]
            contr_2 = s2.positions[start_2_ind:ovl_end_ind2]
            if len(contr_1) + len(contr_2) != overlap_len:
                raise OverlapException(
                    "Resultant is not same length as overlap.")
        except OverlapException:
            heuristic = True
            # Some sample producing methods will not create 1-to-1 mappings
            # in their sets of columns, e.g. where chunking has affected the
            # reads used. Here we find a split point near the middle where
            # the two halfs have the same number of minor positions
            # (i.e. look similar).
            # Require seeing a number of major positions
            UNIQ_MAJ = 3
            end_1_ind, start_2_ind = None, None
            if (len(np.unique(pos1_ovl['major'])) > UNIQ_MAJ and
                    len(np.unique(pos2_ovl['major'])) > UNIQ_MAJ):

                start, end = pos1_ovl['major'][0], pos1_ovl['major'][-1]
                mid = start + (end - start) // 2
                offset = 1
                while end_1_ind is None:

                    if (mid + offset > max(s1.positions['major']) and
                            mid - offset < min(s2.positions['major'])):
                        # run off the edge
                        break
                    for test in (+offset, -offset):
                        left = np.where(
                            s1.positions['major'] == mid + test)[0]
                        right = np.where(
                            s2.positions['major'] == mid + test)[0]
                        if len(left) == len(right):
                            # found a nice junction
                            end_1_ind = left[0]
                            start_2_ind = right[0]
                            break
                    offset += 1
            if end_1_ind is None or start_2_ind is None:
                raise OverlapException(
                    "Could not find viable junction for {} and {}".format(
                        s1.name, s2.name))

        return end_1_ind, start_2_ind, heuristic

    def chunks(self, chunk_len=1000, overlap=200):
        """Create overlapping chunks of self.

        :param chunk_len: chunk length (number of columns)
        :param overlap: overlap length.

        :yields: chunked `Sample` instances.
        """
        # TODO - could refactor this to use Sample.slice?
        chunker = functools.partial(
            sliding_window,
            window=chunk_len, step=chunk_len - overlap, axis=0)
        chunkers = {
            field: chunker(getattr(self, field))
            if getattr(self, field) is not None else itertools.repeat(None)
            for field in self._fields
        }

        for pos in chunkers['positions']:
            fields = set(self._fields) - set(['positions', 'ref_name'])
            new_sample = {
                'positions': pos, 'ref_name': self.ref_name}
            for field in fields:
                new_sample[field] = next(chunkers[field])
            yield Sample(**new_sample)

    def slice(self, key):
        """Slice fields along the genomic axis.

        :param key: slice or index (on array indices)
        :returns: `Sample` obj with views of slices of the original `Sample`.

        >>> pos = np.array(
        ...     [(0, 0), (1, 0), (1, 1), (2, 0)],
        ...     dtype=[('major', int), ('minor', int)])
        >>> feat = np.arange(len(pos))
        >>> s = Sample('contig1', feat , None, None, pos, None, None)
        >>> s.slice(2)  #doctest: +ELLIPSIS
        Sample(...features=2, ..., positions=(1, 1), label_probs=None,...)
        >>> s.slice(slice(1,3)) #doctest: +ELLIPSIS
        Sample(..., features=array([1, 2]),...)
        """
        non_slice_fields = {'ref_name'}

        def slice_attr(attr):
            a = getattr(self, attr)
            if attr not in non_slice_fields:
                a = a[key] if a is not None else None
            return a
        return Sample(**{attr: slice_attr(attr) for attr in self._fields})

    def __eq__(self, other):
        """Test equality."""
        for field in self._fields:
            s = getattr(self, field)
            o = getattr(other, field)
            if type(s) is not type(o):
                return False
            elif isinstance(s, np.ndarray):
                if (s.shape != o.shape or np.any(s != o)):
                    return False
            elif s != o:
                return False
        return True

    @staticmethod
    def trim_samples(sample_gen, logger_name='TrimOlap', quiet=False):
        """Generate trimmed samples.

        Samples are trimmed to remove overlap between adjacent samples.

        :param sample_gen: generator yielding `medaka.common.Sample` s

        :yields: (`medaka.common.Sample` view, bool is_last_in_contig,
            bool heuristic)
        """
        logger = get_named_logger(logger_name)
        log_func = logger.debug if quiet else logger.info

        try:
            s1 = next(sample_gen)
        except StopIteration:
            # there were no samples to process
            return
        # do not trim beginning of s1
        start_1 = None
        # initialise in case we have one sample
        start_2 = None
        for s2 in itertools.chain(sample_gen, (None,)):
            heuristic = False

            is_last_in_contig = False
            # s1 is last chunk
            if s2 is None:
                # go to end of s1
                end_1 = None
                is_last_in_contig = True
            else:
                rel = Sample.relative_position(s1, s2)
                # skip s2 if it is contained within s1
                if rel is Relationship.s2_within_s1:
                    log_func('{} is contained within {}, skipping.'.format(
                        s2.name, s1.name))
                    continue
                elif rel is Relationship.forward_overlap:
                    end_1, start_2, _ = Sample.overlap_indices(
                        s1, s2)
                elif rel is Relationship.forward_gapped:
                    is_last_in_contig = True
                    end_1, start_2 = (None, None)
                    msg = '{} and {} cannot be concatenated as there is ' + \
                        'no overlap and they do not abut.'
                    log_func(msg.format(s1.name, s2.name))
                else:
                    try:
                        end_1, start_2, heuristic = \
                            Sample.overlap_indices(s1, s2)
                        if heuristic:
                            logger.debug(
                                "Used heuristic to stitch {} and {}.".format(
                                    s1.name, s2.name))
                    except OverlapException as e:
                        log_func(
                            "Unhandled overlap type whilst stitching chunks.")
                        raise e

            yield s1.slice(slice(start_1, end_1)), is_last_in_contig, heuristic
            s1 = s2
            start_1 = start_2

    @staticmethod
    def trim_samples_to_region(samples, start=None, end=None):
        """Trim a stream of samples from to overlap exactly co-ordinates.

        :param samples: stream of (`medaka.common.Sample`,
            bool is_last_in_contig, bool heuristic)
        :param start: start co-ordinate.
        :param end: (exclusive) end co-ordinate.
        :yields: stream of (`medaka.common.Sample`, bool is_last_in_contig,
            bool heuristic)

        .. note:: the input samples are expected to be derived from the
            same reference sequence. The `start` and `end` parameters
            are positions in this single sequence.
        """
        def _trim_starts(samples):
            if start is None:
                yield from samples
            # trim all samples in a stream to start on or after start
            # remove from the stream samples that end before start
            for sample, last, heuristic in samples:
                if sample.positions['major'][-1] < start:
                    continue  # don't need sample that ends before target
                if sample.positions['major'][0] < start:
                    query = np.array(
                        [(start, 0)], dtype=sample.positions.dtype)
                    samp_start = np.searchsorted(sample.positions, query[0])
                    sample = sample.slice(slice(samp_start, None))
                if len(sample.positions) > 0:
                    yield sample, last, heuristic

        def _trim_ends(samples):
            if end is None:
                yield from samples
            # trim all samples in a stream to end before end
            # remove from the stream samples that end after end
            for sample, last, heuristic in samples:
                if sample.positions['major'][0] >= end:
                    return  # don't need any samples that start after end
                if sample.positions['major'][-1] >= end:
                    samp_end = np.searchsorted(sample.positions['major'], end)
                    sample = sample.slice(slice(None, samp_end))
                if len(sample.positions) > 0:
                    yield sample, last, heuristic

        # this multistage filtering is a bit gratuitous but at least its
        # transparent and clear: trim overlaps->trim_starts->trim_ends
        # note: we cannot do overlapping last as that can run into
        # "s1 is contained in s2", but s1 will already have been yielded
        samples = _trim_ends(_trim_starts(Sample.trim_samples(samples)))
        yield from samples

    @staticmethod
    def filter_samples(samples, min_depth=10):
        """Generate filtered samples.

        Sections of sample not passing filters are trimmed out.

        :param samples: stream of (`medaka.common.Sample`,
            bool is_last_in_contig, bool heuristc)
        :param min_depth: Sample columns below this depth will be filtered out.
        :yields: (`medaka.common.Sample` view, bool is_last_in_contig,
            bool heuristic)
        """
        # Overlaps should be trimmed before filtering to maintain trimming to
        # half the overlap between chunks and avoid having to reorder stream
        # in situations where overlap regions contain gaps in sufficient depth
        # (marked as x below).
        #           S1'                  S2'      S3'
        # S1 -----------------------x----------x------
        # S2                    ----x----------x------------------------------
        #                        S4'     S5'      S6'
        # By trimming before filtering, we avoid this:
        #           S1'               S2'
        # S1 -----------------------x-----
        # S2                              -----x------------------------------
        #                                  S3'      S4'
        def filtered_stream(samples):
            for s, *_ in samples:
                yield from s.depth_filter(min_depth)
        # Run trim_sample again to avoid reproducing logic in trim_sample that
        # we also need here
        yield from Sample.trim_samples(
            filtered_stream(samples), logger_name='DepthFilt')


# provide read only access to key region attrs
_Region = collections.namedtuple('Region', 'ref_name start end')


class Region(_Region):
    """Represents a genomic region."""

    @property
    def name(self):
        """Samtools-style region string, zero-base end exclusive."""
        return self.__str__()

    def __str__(self):
        """Return string representation of region."""
        # This will be zero-based, end exclusive
        start = 0 if self.start is None else self.start
        end = '' if self.end is None else self.end
        return '{}:{}-{}'.format(self.ref_name, start, end)

    @property
    def size(self):
        """Return size of region."""
        return self.end - self.start

    @classmethod
    def from_string(cls, region):
        """Parse region string into `Region` objects.

        :param region: region str

        >>> Region.from_string('Ecoli') == Region(
        ...     ref_name='Ecoli', start=None, end=None)
        True
        >>> Region.from_string('Ecoli:1000-2000') == Region(
        ...     ref_name='Ecoli', start=1000, end=2000)
        True
        >>> Region.from_string('Ecoli:1000') == Region(
        ...     ref_name='Ecoli', start=1000, end=None)
        True
        >>> Region.from_string('Ecoli:-1000') == Region(
        ...     ref_name='Ecoli', start=0, end=1000)
        True
        >>> Region.from_string('Ecoli:500-') == Region(
        ...     ref_name='Ecoli', start=500, end=None)
        True
        >>> Region.from_string('A:B:c:500-') == Region(
        ...     ref_name='A:B:c', start=500, end=None)
        True
        """
        if ':' not in region:
            ref_name, start, end = region, None, None
        else:
            start, end = None, None
            ref_name, bounds = region.rsplit(':', 1)
            if bounds[0] == '-':
                start = 0
                end = int(bounds.replace('-', ''))
            elif '-' not in bounds:
                start = int(bounds)
                end = None
            elif bounds[-1] == '-':
                start = int(bounds[:-1])
                end = None
            else:
                start, end = [int(b) for b in bounds.split('-')]
        return cls(ref_name, start, end)

    def split(region, size, overlap=0, fixed_size=True):
        """Split region into sub-regions of a given length.

        :param size: size of sub-regions.
        :param overlap: overlap between ends of sub-regions.
        :param fixed_size: ensure all sub-regions are equal in size. If `False`
            then the final chunk will be created as the smallest size to
            conform with `overlap`.

        :returns: a list of sub-regions.

        """
        regions = list()
        if size >= region.size:
            return [region]
        for start in range(region.start, region.end, size - overlap):
            end = min(start + size, region.end)
            regions.append(Region(region.ref_name, start, end))
        if len(regions) > 1:
            if fixed_size and regions[-1].size < size:
                del regions[-1]
                end = region.end
                start = end - size
                if start > regions[-1].start:
                    regions.append(Region(region.ref_name, start, end))
        return regions

    def overlaps(self, other):
        """Determine if a region overlaps another.

        :param other: a second Region to test overlap.

        :returns: True if regions overlap.

        """
        if self.ref_name != other.ref_name:
            return False

        def _limits(x):
            x0 = x.start if x.start is not None else -1
            x1 = x.end if x.end is not None else float('inf')
            return x0, x1

        a0, a1 = _limits(self)
        b0, b1 = _limits(other)
        return (
            (a0 < b1 and a1 > b0) or
            (b0 < a1 and b1 > a0))


def get_bam_regions(bam, regions=None):
    """Get regions from a bam.

    Region start and end will be set to an integer value.

    :param bam: `.bam` file.
    :param regions: iterable of `medaka.common.Region` objs

    :returns: list of `Region` objects.
    """
    with pysam.AlignmentFile(bam) as bam_fh:
        ref_lengths = dict(zip(bam_fh.references, bam_fh.lengths))
    if regions is not None:
        new_regions = []
        for r in regions:
            if r.ref_name not in ref_lengths:
                msg = 'Contig {} is not one of the bam references.'
                raise KeyError(msg.format(r.ref_name))
            start = max(0, r.start) if r.start is not None else 0
            rl = ref_lengths[r.ref_name]
            end = min(r.end, rl) if r.end is not None else rl
            new_regions.append(Region(r.ref_name, start, end))
    else:
        new_regions = [
            Region(ref_name, 0, end)
            for ref_name, end in ref_lengths.items()]

    return new_regions


def ref_name_from_region_str(region_str):
    """Parse region strings, returning a list of reference names.

    :param regions: iterable of region strings.

    :returns: tuple of reference name str.
    """
    ref_names = [Region.from_string(r).ref_name for r in region_str]
    return tuple(set(ref_names))


def sliding_window(a, window=3, step=1, axis=0):
    """Sliding window across an array.

    :param a: input array.
    :param window: window length.
    :param step: step length between consecutive windows.
    :param axis: axis over which to apply window.

    :yields: windows of the input array.
    """
    slicee = [slice(None)] * a.ndim
    end = 0
    for start in range(0, a.shape[axis] - window + 1, step):
        end = start + window
        slicee[axis] = slice(start, end)
        yield a[tuple(slicee)]
    # yield the remainder with the same window size
    if a.shape[axis] > end:
        start = a.shape[axis] - window
        slicee[axis] = slice(start, a.shape[axis])
        yield a[tuple(slicee)]


def mkdir_p(path, info=None):
    """Make a directory if it doesn't exist."""
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            if info is not None:
                info = " {}".format(info)
            logging.warning("The path {} exists.{}".format(path, info))
            pass
        else:
            raise


def is_file_empty(file_path):
    """
    Check if a file is empty.

    Args:
        file_path (str): The path to the file.

    Returns:
        bool: True if the file is empty, False otherwise.
        None: If the file is not found or cannot be accessed.

    """
    try:
        return os.path.getsize(file_path) == 0
    except OSError:
        print("File not found or cannot be accessed.")
        return None


def remove_if_exist(path):
    """
    Remove a file if it exists.

    Parameters:
    path (str): The path to the file to be removed.

    Returns:
    None

    """
    if os.path.exists(path):
        os.remove(path)


def remove_directory(path):
    """
    Remove a directory and its contents.

    Args:
        path (str): The path of the directory to be removed.

    Returns:
        None

    """
    if os.path.exists(path):
        shutil.rmtree(path, ignore_errors=True)


def concat_files(input_paths, output_path, has_header=False):
    """Concatenate a list of files into one file."""
    if not input_paths:
        open(output_path, 'w').close()
        return
    header_printed = False
    with open(output_path, 'w') as fout, fileinput.input(input_paths) as fin:
        for line in fin:
            if has_header and header_printed and fin.isfirstline():
                continue
            fout.write(line)
            header_printed = True


def grouper(gen, batch_size=4):
    """Group together elements of an iterable without padding remainder."""
    if not isinstance(gen, collections.abc.Iterator):
        gen = iter(gen)
    while True:
        batch = []
        for i in range(batch_size):
            try:
                batch.append(next(gen))
            except StopIteration:
                if len(batch) > 0:
                    yield batch
                return
        yield batch


def roundrobin(*iterables):
    """Take items from iterables in a round-robin."""
    pending = len(iterables)
    nexts = itertools.cycle(iter(it).__next__ for it in iterables)
    while pending:
        try:
            for next in nexts:
                yield next()
        except StopIteration:
            pending -= 1
            nexts = itertools.cycle(itertools.islice(nexts, pending))


def print_data_path():
    """Print data directory containing models."""
    print(importlib.resources.files(__package__) / 'data')


def get_named_logger(name):
    """Create a logger with a name."""
    logger = logging.getLogger('{}.{}'.format(__package__, name))
    logger.name = name
    return logger


def loose_version_sort(it, key=None):
    """Sort an iterable.

    This is a reimplementation of `distutils.version.LooseVersion` sort;
    strings are split into alphanumeric parts, which are then
    converted to integers or left as strings. Tuple comparison is used
    to sort such parts.

    >>> loose_version_sort(['chr10', 'chr2', 'chr1'])
    ['chr1', 'chr2', 'chr10']
    >>> sorted(['chr10', 'chr2', 'chr1'])
    ['chr1', 'chr10', 'chr2']
    >>> loose_version_sort([
    ...     'chr{}c{}'.format(i,j)
    ...     for i,j in itertools.product(
    ...        [1, 10, 2], [1,10,2])])  # doctest: +ELLIPSIS
    ['chr1c1', 'chr1c2', 'chr1c10', 'chr2c1', ..., 'chr10c2', 'chr10c10']
    """
    def version_sorter(x):
        # rough reimplementation of distutils.version.LooseVersion
        # to avoid dependency on distutils
        if key is not None:
            x = key(x)

        find_parts_re = re.compile(r'([a-zA-Z]+|\d+|.)')
        parts = [part for part in find_parts_re.split(x) if part.isalnum()]
        # turn parts into integers or strings
        parts = [int(p) if p.isdigit() else p for p in parts]
        return tuple(parts)

    it = list(it)
    try:
        result = sorted(it, key=version_sorter)
    except Exception:
        logger = get_named_logger("VariantSort")
        logger.debug("Could not sort with packaging.version.Version")
        result = sorted(it, key=key)
    return result


comp = {
    'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C', 'X': 'X', 'N': 'N',
    'a': 't', 't': 'a', 'c': 'g', 'g': 'c', 'x': 'x', 'n': 'n',
    # '-': '-'
}
comp_trans = str.maketrans(''.join(comp.keys()), ''.join(comp.values()))


def reverse_complement(seq):
    """Reverse complement sequence.

    :param: input sequence string.

    :returns: reverse-complemented string.

    """
    return seq.translate(comp_trans)[::-1]


def read_key_value_tsv(fname):
    """Read a dictionary from a .tsv file.

    :param fname: a .tsv file with two columns: keys and values.

    :returns: a dictionary.

    """
    try:
        as_string = libmedaka.ffi.string
        text = libmedaka.lib.read_key_value(fname.encode())
        data = dict()
        for i in range(0, text.n, 2):
            key = as_string(text.strings[i]).decode()
            value = as_string(text.strings[i+1]).decode()
            data[key] = value
        libmedaka.lib.destroy_string_set(text)
    except Exception:
        raise RuntimeError(
            'Failed to parse {} as two-column .tsv file.'.format(fname))
    return data


def initialise_alignment(
        query_name, reference_id, reference_start,
        query_sequence, cigarstring, flag, mapping_quality=60,
        query_qualities=None, tags=None):
    """Create a `Pysam.AlignedSegment` object.

    :param query_name: name of the query sequence
    :param reference_id: index to the reference name
    :param reference_start: 0-based index of first leftmost reference
        coordinate
    :param query_sequence: read sequence bases, including those soft clipped
    :param cigarstring: cigar string representing the alignment of query
        and reference
    :param flag: bitwise flag representing some properties of the alignment
        (see SAM format)
    :param mapping_quality: optional quality of the mapping or query to
        reference
    :param query_qualities: optional base qualities of the query, including
        soft-clipped ones!

    :returns: `pysam.AlignedSegment` object
    """
    if tags is None:
        tags = dict()

    a = pysam.AlignedSegment()
    a.query_name = query_name
    a.reference_id = reference_id
    a.reference_start = reference_start
    a.query_sequence = query_sequence
    a.cigarstring = cigarstring
    a.flag = flag
    a.mapping_quality = mapping_quality
    if query_qualities is not None:
        a.query_qualities = query_qualities

    for tag_name, tag_value in tags.items():
        a.set_tag(tag_name, tag_value)

    return a


def yield_from_bed(bedfile):
    """Yield chrom, start, stop tuples from a bed file.

    :param bedfile: str, filepath.
    :yields: (str chrom, int start, int stop).
    """
    with open(bedfile) as fh:
        for line in fh:
            split_line = line.split()
            if split_line[0] in {'browser', 'track'} or len(split_line) < 3:
                continue
            chrom = split_line[0]
            start = int(split_line[1])
            stop = int(split_line[2])
            yield chrom, start, stop


def complement_intervaltrees(trees, contig_lengths):
    """Complement intervals, return intervals not present in the input trees.

    :param trees: {str contig: `intervaltree.IntervalTree` objs}
    :param contig_lengths: {str contig: int contig length}
    :returns: {str contig: `intervaltree.IntervalTree` objs}
    """
    comp = collections.defaultdict(intervaltree.IntervalTree)
    for contig, length in contig_lengths.items():
        comp[contig].add(intervaltree.Interval(0, length))
    for contig, tree in trees.items():
        for interval in tree:
            comp[contig].chop(interval.begin, interval.end)
    return comp


def write_intervaltrees_to_bed(trees, outfile):
    """Write contig intervaltrees to bed file.

    :param trees: {str contig: `intervaltree.IntervalTree` objs}
    :param outfile: str, filepath.
    """
    with open(outfile, 'w') as fh:
        for contig in sorted(trees):
            tree = trees[contig]
            for i in sorted(tree.all_intervals):
                fh.write("{}\t{}\t{}\n".format(contig, i.begin, i.end))


def common_fasta_contigs(fastas, contigs=None):
    """Get common contig names from multiple fasta files.

    :param fastas: iterable of str of fasta filepaths.
    :param contigs: iterable of str, check all fastas contain these contigs
        raising a KeyError if they are not all present.

    :returns: tuple of str, contig names.
    """
    fasta_contigs = {f: pysam.FastaFile(f).references for f in fastas}
    common = set(fasta_contigs[fastas[0]])
    for f in fastas[1:]:
        common = common.intersection(fasta_contigs[f])
    if contigs is not None:
        if not common.issuperset(contigs):
            msg = 'Contigs {} are not present in all fastas.'
            raise KeyError(msg.format(set(contigs) - common))
        else:
            common = contigs
    # return contigs in same order as in first fasta
    return tuple([c for c in fasta_contigs[fastas[0]] if c in common])


def rle(iterable):
    """Calculate a run length encoding (rle), of an input iterable.

    :param iterable: input iterable.

    :returns: structured array with fields `start`, `length`, and `value`.
    """
    if not isinstance(iterable, np.ndarray):
        array = np.fromiter(iterable, dtype='U1', count=len(iterable))
    else:
        array = iterable

    if len(array.shape) != 1:
        raise TypeError("Input array must be one dimensional.")
    dtype = [('length', int), ('start', int), ('value', array.dtype)]

    n = len(array)
    starts = np.r_[0, np.flatnonzero(array[1:] != array[:-1]) + 1]
    rle = np.empty(len(starts), dtype=dtype)
    rle['start'] = starts
    rle['length'] = np.diff(np.r_[starts, n])
    rle['value'] = array[starts]
    return rle


def cuda_visible_devices(devices=""):
    """Set CUDA devices.

    :param: comma separated string of device IDs.

    The default use case is to be able to hide all
    devices. It can be used with PoolExecutors to
    disable child access to CUDA devices.
    """
    os.environ["CUDA_VISIBLE_DEVICES"] = devices


def tag_merge_bams(args):
    """Add tags to and merge one or more bam files."""
    n_bams = len(args.input_bams)
    n_values = len(args.values)
    if not n_bams == n_values:
        raise ValueError(
            f"Number of input files ({n_bams}) and "
            f"values ({n_values}) must match.")

    if os.path.exists(args.output):
        raise ValueError("Output file exists.")

    tmp_files = []
    outdir = os.path.dirname(args.output)
    logger = get_named_logger("Tag")

    def _process_input_bam(proc_args, io_threads=1):
        path, value = proc_args
        logger.info(f"Adding tag '{value}' to {path}")
        with pysam.AlignmentFile(
                path, 'r', check_sq=False, threads=io_threads) as in_bam:
            tmp_file = tempfile.NamedTemporaryFile(dir=outdir)
            with pysam.AlignmentFile(
                    tmp_file.name, "wb", header=in_bam.header,
                    threads=io_threads) as out_bam:
                for r in in_bam.fetch(until_eof=True):
                    r.set_tag(args.tag, value)
                    out_bam.write(r)
        return tmp_file

    with concurrent.futures.ThreadPoolExecutor(
            max_workers=min(args.threads, len(args.input_bams))
    ) as executor:
        process = functools.partial(
            _process_input_bam,
            io_threads=max(1, args.threads // (2 * len(args.input_bams))))
        tmp_files = list(executor.map(
                process, zip(args.input_bams, args.values)))

    logger.info(f"Merging from {len(tmp_files)} temporary files")
    pysam.merge(
        "-o", str(args.output), *[fh.name for fh in tmp_files], "-O", "BAM",
        "-@", str(args.threads), '-c', '-p'
    )

    for fh in tmp_files:
        fh.close()

    pysam.index(str(args.output), "-@", str(args.threads))
