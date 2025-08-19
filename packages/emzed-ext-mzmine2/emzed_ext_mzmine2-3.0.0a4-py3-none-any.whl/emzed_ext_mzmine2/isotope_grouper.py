import json
import os

from emzed import Table

from ._exceptions import MzMine2Exception
from ._java_utils import run_java
from ._parameters import ParameterBaseMeta
from ._utils import cleanup_temp_files


class IsotopeGrouperParameters(metaclass=ParameterBaseMeta):
    _java_class = "IsotopeGrouperParameters"

    _fields = [
        "mzTolerance",
        "rtTolerance",
        "monotonicShape",
        "maximumCharge",
        "representativeIsotope",
    ]


@cleanup_temp_files
def isotope_grouper(peaks, parameters):
    assert isinstance(peaks, Table)
    peaks._ensure_col_names("id", "mz", "rt", "height")
    if peaks.supported_postfixes("") != [""]:
        raise ValueError("peaks table has postfixes, please remove them")

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

    peaks.extract_columns("id", "rt", "mz", "height", keep_view=True).save_csv(
        temp_file_in, delimiter=" ", as_printed=False
    )

    config_file = mktemp(".json")  # noqa: F821

    config_data = dict(
        rt_tolerance=parameters.rt_tolerance,
        mz_tolerance=parameters.mz_tolerance,
        monotonic_shape=parameters.monotonic_shape,
        maximum_charge=parameters.maximum_charge,
        representative_isotope=parameters.representative_isotope,
    )
    with open(config_file, "w") as fh:
        fh.write(json.dumps(config_data, indent=4))

    run_java("IsotopeGrouper", temp_file_in, temp_file_out, config_file, peakmap_file)

    if not os.path.exists(temp_file_out):
        raise MzMine2Exception("adduct search failed and did not write output file")

    identifications = Table.load_csv(
        temp_file_out,
        col_names=["isotope_group_id", "peak_id", "other_id", "charge"],
        col_types=[int, int, int, int],
        delimiter=" ",
    )

    result = peaks.left_join(identifications, peaks.id == identifications.other_id)
    result.drop_columns("other_id__0")
    result.rename_columns(peak_id__0="isotope_base_peak", charge__0="isotope_charge")
    result.rename_postfixes(__0="")
    result.add_column(
        "isotope_group_size",
        result.group_by(result.isotope_group_id).count(),
        int,
        insert_before=-1,
    )
    return result
