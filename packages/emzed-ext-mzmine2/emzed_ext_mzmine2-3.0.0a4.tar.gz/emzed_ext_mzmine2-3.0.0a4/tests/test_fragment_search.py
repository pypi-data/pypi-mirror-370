#!/usr/bin/env python


import emzed
from emzed_ext_mzmine2 import FragmentSearchParameters, fragment_search


def test_fragment_search(regtest, data_path):
    peaks = emzed.io.load_table(data_path("peaks_for_fragment_search.table"))
    p = FragmentSearchParameters()
    p.rt_tolerance = (True, 1)
    p.ms2mz_tolerance = (0.01, 0)
    p.min_ms2peak_height = 100
    p.max_fragment_height = 0.5
    print(p, file=regtest)
    peaks_with_fragments = fragment_search(peaks, p)
    print(peaks_with_fragments, file=regtest)
    print(
        peaks_with_fragments.filter(
            peaks_with_fragments.fragments_annotation.is_not_none()
        ),
        file=regtest,
    )
