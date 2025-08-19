#!/usr/bin/env python

import json
import os

from emzed import Table

from ._exceptions import MzMine2Exception
from ._java_utils import run_java
from ._parameters import ParameterBaseMeta
from ._utils import cleanup_temp_files

HERE = os.path.dirname(os.path.abspath(__file__))

try:
    default_adducts = json.load(
        open(os.path.join(HERE, "_mzmine2_default_adducts.json"))
    )
    default_adducts = list(map(tuple, default_adducts))
except IOError:
    default_adducts = []


class AdductSearchParameters(metaclass=ParameterBaseMeta):
    _java_class = "AdductSearchParameters"

    _fields = ["RT_TOLERANCE", "MZ_TOLERANCE", "ADDUCTS", "MAX_ADDUCT_HEIGHT"]
    _defaults = {
        "mz_tolerance": (0.001, 0),
        "rt_tolerance": (False, 1.0),
        "adducts": default_adducts,
        "max_adduct_height": 1.0,
    }


@cleanup_temp_files
def adduct_search(peaks, parameters):
    assert isinstance(peaks, Table)
    peaks._ensure_col_names("id", "mz", "rt", "height")
    if peaks.supported_postfixes("") != [""]:
        raise ValueError("peaks table has postfixes, please remove them")

    if "adduct_annotation" in peaks.col_names:
        raise ValueError("column name adduct_annotation not allowed")

    parameters._check_if_all_parameters_are_set()

    temp_file_in = mktemp(".csv")  # noqa: F821
    temp_file_out = mktemp(".txt")  # noqa: F821

    peaks.extract_columns("id", "rt", "mz", "height", keep_view=True).save_csv(
        temp_file_in, delimiter=" ", as_printed=False
    )

    config_file = mktemp(".json")  # noqa: F821

    config_data = dict(
        rt_tolerance=parameters.rt_tolerance,
        mz_tolerance=parameters.mz_tolerance,
        max_adduct_height=parameters.max_adduct_height,
        adducts=parameters.adducts,
    )
    with open(config_file, "w") as fh:
        fh.write(json.dumps(config_data, indent=4))

    run_java("AdductSearch", temp_file_in, temp_file_out, config_file)

    if not os.path.exists(temp_file_out):
        raise MzMine2Exception("adduct search failed and did not write output file")

    identifications = Table.load_csv(
        temp_file_out,
        col_names=["id", "adduct_annotation"],
        col_types=[int, str],
        delimiter=",",
    )

    result = peaks.left_join(identifications, peaks.id == identifications.id)
    result.drop_columns("id__0")
    result.rename_postfixes(__0="")
    return result
