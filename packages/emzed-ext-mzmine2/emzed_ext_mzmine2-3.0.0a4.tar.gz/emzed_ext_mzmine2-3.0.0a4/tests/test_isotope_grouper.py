#!/usr/bin/env python

import emzed
from emzed_ext_mzmine2 import IsotopeGrouperParameters, isotope_grouper


def test_isotope_grouper(data_path, regtest):

    ap = IsotopeGrouperParameters()
    ap.mz_tolerance = (0.001, 0)
    ap.rt_tolerance = (True, 1)
    ap.monotonic_shape = False
    ap.maximum_charge = 3

    print(ap, file=regtest)

    peaks = emzed.io.load_table(data_path("peaks.table"))

    grouped = isotope_grouper(peaks, ap)
    print(grouped, file=regtest)
    print(grouped.filter(grouped.isotope_group_id.is_not_none()), file=regtest)
