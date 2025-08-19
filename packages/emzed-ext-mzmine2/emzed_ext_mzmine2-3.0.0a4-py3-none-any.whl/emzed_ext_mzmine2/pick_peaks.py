#! /usr/bin/env python
# Copyright © 2019 Uwe Schitt <uwe.schmitt@id.ethz.ch>

import json
import os

from emzed import MzType, PeakMap, RtType, Table

from ._exceptions import MzMine2Exception
from ._java_utils import run_java
from ._parameters import ParameterBaseMeta
from ._peak_resolvers import (  # noqa: F401
    ADAPDetector,
    BaselinePeakDetector,
    IntensityWindowsSNParameters,
    MinimumSearchPeakDetector,
    NoiseAmplitudePeakDetector,
    PeakResolver,
    SavitzkyGolayPeakDetector,
    WaveletCoefficientsSNParameters,
)
from ._utils import cleanup_temp_files
from .remove_shoulder_peaks import RemoveShoulderPeaksParameters


class ADAPChromatogramBuilder(metaclass=ParameterBaseMeta):
    _java_class = "ADAPChromatogramBuilderParameters"

    _fields = ["minimumScanSpan", "mzTolerance", "IntensityThresh2", "startIntensity"]
    _defaults = {
        "minimum_scan_span": 3,
        "mz_tolerance": (0, 5),
        "intensity_thresh2": 0,
        "start_intensity": 0,
    }

    def _check_minimum_scan_span(self, value):
        return value >= 1, "must be at least 1"

    def _check_intensity_thresh2(self, value):
        return value >= 0, "must be larger than or equal to 0"

    def _check_start_intensity(self, value):
        return value >= 0, "must be larger than or equal to 0"


@cleanup_temp_files
def pick_peaks(
    peakmap,
    adap_chromatogram_builder,
    peak_resolver,
    rsp_parameters=None,
    verbose=False,
):
    """runs centroid peak picker + ADAPChromatogramBuilder from MZmine2.

    :param peakmap: PeakMap object

    :param adap_chromatogram_builder: ADAPChromatogramBuilder object

    :param rsp_parameters: RemoveShoulderPeaksParameters object,
             optional. If provided also shoulder peaks will be removed.

    :param verbose: print more output from mzmine when ``verbose`` is ``True``.

    :return: emzed.Table with columns mz, rt, mzmin, mzmax, rtmin, rtmax, area,
             and height.
    """

    assert isinstance(peakmap, PeakMap)

    assert isinstance(adap_chromatogram_builder, ADAPChromatogramBuilder)

    assert isinstance(peak_resolver, PeakResolver)

    adap_chromatogram_builder._check_if_all_parameters_are_set()
    peak_resolver._check_if_all_parameters_are_set()

    if rsp_parameters is not None:
        assert isinstance(rsp_parameters, RemoveShoulderPeaksParameters)
        rsp_parameters._check_if_all_parameters_are_set()

    temp_file_in = mktemp(".mzML")  # noqa: F821
    temp_file_out = mktemp(".txt")  # noqa: F821
    peakmap.save(temp_file_in)

    config_file = mktemp(".json")  # noqa: F821

    config_data = dict(
        peak_resolver_class=peak_resolver.__class__.__qualname__,
        peak_resolver_parameters=peak_resolver._to_dict(),
        adap_chromatogram_builder=(adap_chromatogram_builder._to_dict()),
        rsp_parameters=None if rsp_parameters is None else rsp_parameters._to_dict(),
        verbose=verbose,
    )
    with open(config_file, "w") as fh:
        fh.write(json.dumps(config_data, indent=4))

    run_java("PickPeaks", temp_file_in, temp_file_out, config_file)

    if not os.path.exists(temp_file_out):
        raise MzMine2Exception("peak picker failed and did not write output file")

    result = Table.load_csv(
        temp_file_out,
        col_names=[
            "id",
            "parent_id",
            "mz",
            "rt",
            "mzmin",
            "mzmax",
            "rtmin",
            "rtmax",
            "area",
            "height",
        ],
        col_types=[
            int,
            int,
            MzType,
            RtType,
            MzType,
            MzType,
            RtType,
            RtType,
            float,
            float,
        ],
        delimiter=",",
    )
    result.add_column("width", result.rtmax - result.rtmin, RtType)
    result.set_col_format("area", "%7.2e")
    result.set_col_format("height", "%7.2e")
    result.add_column_with_constant_value("peakmap", peakmap, PeakMap, None)
    return result
