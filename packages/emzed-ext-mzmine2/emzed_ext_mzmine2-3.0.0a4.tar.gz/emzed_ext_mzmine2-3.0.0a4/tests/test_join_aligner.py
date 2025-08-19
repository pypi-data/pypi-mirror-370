#!/usr/bin/env python

import emzed
from emzed_ext_mzmine2 import (
    IsotopePatternScoreParameters,
    JoinAlignerParameters,
    join_aligner,
)


def test_isotope_grouper_0(data_path, regtest):

    peaks = emzed.io.load_table(data_path("peaks_with_isotope_patterns.table"))

    join_aligner_parameters = JoinAlignerParameters(
        mz_tolerance=(0.01, 0),
        mz_weight=0.5,
        rt_tolerance=(True, 3),
        rt_weight=0.5,
        same_charge_required=False,
    )

    isotope_pattern_score_parameters = IsotopePatternScoreParameters(
        mz_tolerance=(0.001, 0),
        isotope_noise_level=100,
        isotope_pattern_score_threshold=0.1,
    )

    n_skip_peaks = 100

    aligend_peak_tables = join_aligner(
        [peaks[n_skip_peaks:], peaks[:-n_skip_peaks], peaks],
        join_aligner_parameters,
        isotope_pattern_score_parameters,
    )

    number_of_common_peaks = len(
        (
            set(aligend_peak_tables[0].global_peak_id)
            & set(aligend_peak_tables[1].global_peak_id)
            & set(aligend_peak_tables[2].global_peak_id)
        )
    )

    assert number_of_common_peaks == len(peaks) - 2 * n_skip_peaks

    print(aligend_peak_tables[0], file=regtest)
    print(aligend_peak_tables[1], file=regtest)


def test_isotope_grouper_1(data_path, regtest):

    peaks = emzed.io.load_table(data_path("peaks_with_isotope_patterns.table"))

    join_aligner_parameters = JoinAlignerParameters(
        mz_tolerance=(0.01, 0),
        mz_weight=0.5,
        rt_tolerance=(True, 3),
        rt_weight=0.5,
        same_charge_required=False,
    )

    n_skip_peaks = 100

    aligend_peak_tables = join_aligner(
        [peaks[n_skip_peaks:], peaks[:-n_skip_peaks], peaks], join_aligner_parameters
    )

    number_of_common_peaks = len(
        (
            set(aligend_peak_tables[0].global_peak_id)
            & set(aligend_peak_tables[1].global_peak_id)
            & set(aligend_peak_tables[2].global_peak_id)
        )
    )

    assert number_of_common_peaks == len(peaks) - 2 * n_skip_peaks


def test_isotope_grouper_2(data_path, regtest):

    peaks = emzed.io.load_table(data_path("peaks_with_isotope_patterns.table"))

    peaks = peaks.filter(peaks.isotope_group_id.is_not_none())

    join_aligner_parameters = JoinAlignerParameters(
        mz_tolerance=(0.01, 0),
        mz_weight=0.5,
        rt_tolerance=(True, 3),
        rt_weight=0.5,
        same_charge_required=False,
    )

    isotope_pattern_score_parameters = IsotopePatternScoreParameters(
        mz_tolerance=(0.001, 0),
        isotope_noise_level=100,
        isotope_pattern_score_threshold=0.1,
    )

    n_skip_peaks = 10

    aligend_peak_tables = join_aligner(
        [peaks[n_skip_peaks:], peaks[:-n_skip_peaks], peaks],
        join_aligner_parameters,
        isotope_pattern_score_parameters,
    )

    all_peaks = emzed.Table.stack_tables(aligend_peak_tables)

    for group in all_peaks.split_by("isotope_group_id"):
        print(group, file=regtest)
