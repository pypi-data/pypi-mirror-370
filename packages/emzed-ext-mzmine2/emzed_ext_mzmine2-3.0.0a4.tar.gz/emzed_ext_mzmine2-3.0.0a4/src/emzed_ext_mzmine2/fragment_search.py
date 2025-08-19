#!/usr/bin/env python

import json
import os

from emzed import Table

from ._exceptions import MzMine2Exception
from ._java_utils import run_java
from ._parameters import ParameterBaseMeta
from ._utils import cleanup_temp_files


class FragmentSearchParameters(metaclass=ParameterBaseMeta):
    _java_class = "FragmentSearchParameters"
    _fields = ["rtTolerance", "ms2mzTolerance", "maxFragmentHeight", "minMS2peakHeight"]


@cleanup_temp_files
def fragment_search(peaks, parameters):
    assert isinstance(peaks, Table)
    peaks._ensure_col_names(
        "id", "mz", "mzmin", "mzmax", "rt", "rtmin", "rtmax", "height", "peakmap"
    )
    if peaks.supported_postfixes("") != [""]:
        raise ValueError("peaks table has postfixes, please remove them")

    if "fragment_annotation" in peaks.col_names:
        raise ValueError("column name fragment_annotation not allowed")

    parameters._check_if_all_parameters_are_set()

    peakmaps = peaks.peakmap.unique_values()
    if len(peakmaps) == 0:
        raise ValueError("peakmap column does not contain any peakmap")
    if len(peakmaps) > 1:
        raise ValueError("peakmap column contains multiple peakmaps")

    peakmap = peakmaps[0]

    temp_file_in = mktemp(".csv")  # noqa: F821
    temp_file_out = mktemp(".txt")  # noqa: F821
    peakmap_file = mktemp(".mzML")  # noqa: F821

    peakmap.save(peakmap_file)

    peaks.extract_columns(
        "id", "rt", "rtmin", "rtmax", "mz", "mzmin", "mzmax", "height", keep_view=True
    ).save_csv(temp_file_in, delimiter=" ", as_printed=False)

    config_file = mktemp(".json")  # noqa: F821

    config_data = parameters._to_dict()

    with open(config_file, "w") as fh:
        fh.write(json.dumps(config_data, indent=4))

    run_java("FragmentSearch", temp_file_in, temp_file_out, config_file, peakmap_file)

    if not os.path.exists(temp_file_out):
        raise MzMine2Exception("fragment search failed and did not write output file")

    identifications = Table.load_csv(
        temp_file_out,
        col_names=["id", "fragments_annotation"],
        col_types=[int, str],
        delimiter=",",
    )

    result = peaks.left_join(identifications, peaks.id == identifications.id)
    result.drop_columns("id__0")
    result.rename_postfixes(__0="")
    return result
