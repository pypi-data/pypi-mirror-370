#!/usr/bin/env python

import emzed
from emzed_ext_mzmine2 import AdductSearchParameters, adduct_search


def test_adduct_search(data_path, regtest):

    ap = AdductSearchParameters()
    ap.mz_tolerance = (0.0001, 0)
    ap.rt_tolerance = (True, 0.2)
    ap.max_adduct_height = 10

    print(ap, file=regtest)

    peaks = emzed.io.load_table(data_path("peaks.table"))

    annotated = adduct_search(peaks, ap)
    print(annotated, file=regtest)
    print(annotated.filter(annotated.adduct_annotation.is_not_none()), file=regtest)
