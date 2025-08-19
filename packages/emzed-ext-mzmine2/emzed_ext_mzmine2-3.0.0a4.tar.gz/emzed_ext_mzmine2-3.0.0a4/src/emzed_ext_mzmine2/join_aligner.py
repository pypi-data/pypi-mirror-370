#!/usr/bin/env python

import json
import os
import warnings
from collections import defaultdict

from emzed import Table

from ._exceptions import MzMine2Exception
from ._java_utils import run_java
from ._parameters import ParameterBaseMeta
from ._utils import cleanup_temp_files


class IsotopePatternScoreParameters(metaclass=ParameterBaseMeta):
    _java_class = "IsotopePatternScoreParameters"

    _fields = ["mzTolerance", "isotopeNoiseLevel", "isotopePatternScoreThreshold"]


class JoinAlignerParameters(metaclass=ParameterBaseMeta):
    _java_class = "JoinAlignerParameters"

    _fields = [
        "MZTolerance",
        "MZWeight",
        "RTTolerance",
        "RTWeight",
        "SameChargeRequired",
    ]


@cleanup_temp_files
def join_aligner(
    peak_tables, join_aligner_parameters, isotope_pattern_score_parameters=None
):
    assert isinstance(peak_tables, (list, tuple))
    assert all(isinstance(peak_table, Table) for peak_table in peak_tables)

    for i, peak_table in enumerate(peak_tables):
        peak_table._ensure_col_names("id", "mz", "rt", "height")
        if "global_peak_id" in peak_table:
            warnings.warn(f"peak table {i} already has column global_peak_id")
        if join_aligner_parameters.same_charge_required:
            peak_table._ensure_col_names("charge")

        if peak_table.supported_postfixes("") != [""]:
            raise ValueError(f"peak table {i} has postfixes, please remove them")

        if len(peak_table) == 0:
            raise ValueError(f"peak table {i} is empty.")

    join_aligner_parameters._check_if_all_parameters_are_set()

    isotope_patterns = defaultdict(list)

    max_peak_id = -1
    if isotope_pattern_score_parameters is not None:
        isotope_pattern_score_parameters._check_if_all_parameters_are_set()
        for peak_table in peak_tables:
            peak_table._ensure_col_names(
                "isotope_group_id", "isotope_base_peak", "isotope_charge"
            )

        max_peak_id = max(peak_table.id.max().eval() for peak_table in peak_tables)
        for i, peak_table in enumerate(peak_tables):
            offset = i * (max_peak_id + 1)
            for row in peak_table:
                if row.isotope_base_peak is None:
                    isotope_patterns[offset + row.id].append((row.mz, row.height))
                else:
                    isotope_patterns[offset + row.isotope_base_peak].append(
                        (row.mz, row.height)
                    )
                    isotope_patterns[offset + row.isotope_base_peak].append(
                        (row.mz, row.height)
                    )
            for row in peak_table:
                if row.isotope_base_peak is not None:
                    isotope_patterns[offset + row.id] = isotope_patterns[
                        offset + row.isotope_base_peak
                    ]

    extracted = []
    for peak_table in peak_tables:
        if join_aligner_parameters.same_charge_required:
            extracted.append(
                peak_table.filter(
                    peak_table.id == peak_table.isotope_base_peak
                ).extract_columns("id", "rt", "mz", "charge")
            )
        else:
            extracted.append(peak_table.extract_columns("id", "rt", "mz"))

    for i, peak_table in enumerate(extracted):
        peak_table.add_column_with_constant_value("_peak_table_id", i, int)

    temp_file_in = mktemp(".csv")  # noqa: F821
    temp_file_out = mktemp(".txt")  # noqa: F821
    config_file = mktemp(".json")  # noqa: F821
    isotope_pattern_file = mktemp(".json")  # noqa: F821

    Table.stack_tables(extracted).save_csv(
        temp_file_in, delimiter=" ", as_printed=False
    )

    config_data = dict(
        mz_tolerance=join_aligner_parameters.mz_tolerance,
        mz_weight=join_aligner_parameters.mz_weight,
        rt_tolerance=join_aligner_parameters.rt_tolerance,
        rt_weight=join_aligner_parameters.rt_weight,
        same_charge_required=join_aligner_parameters.same_charge_required,
    )

    if isotope_pattern_score_parameters is not None:
        config_data["isotope_pattern_score_parameters"] = dict(
            mz_tolerance=isotope_pattern_score_parameters.mz_tolerance,
            isotope_noise_level=isotope_pattern_score_parameters.isotope_noise_level,
            isotope_pattern_score_threshold=(
                isotope_pattern_score_parameters.isotope_pattern_score_threshold
            ),
        )

    with open(config_file, "w") as fh:
        fh.write(json.dumps(config_data, indent=4))
    with open(isotope_pattern_file, "w") as fh:
        fh.write(json.dumps(isotope_patterns, indent=4))

    run_java(
        "JoinAligner",
        temp_file_in,
        temp_file_out,
        config_file,
        isotope_pattern_file,
        max_peak_id,
        len(peak_tables),
    )

    if not os.path.exists(temp_file_out):
        raise MzMine2Exception("join aligner failed and did not write output file")

    mapping = dict()
    for global_peak_id, row in enumerate(open(temp_file_out)):
        fields = list(map(int, row.split()))
        assert len(fields) % 2 == 0
        for i in range(0, len(fields), 2):
            peak_table_id, local_peak_id = fields[i : i + 2]
            mapping[peak_table_id, local_peak_id] = global_peak_id

    result = []
    for peak_table_id, peak_table in enumerate(peak_tables):
        peak_table = peak_table.consolidate()

        def lookup(peak_id):
            return mapping.get((peak_table_id, peak_id))

        peak_table.add_column(
            "global_peak_id", peak_table.apply(lookup, peak_table.id), int
        )
        result.append(peak_table)
    return result
