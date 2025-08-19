#! /usr/bin/env python
# Copyright © 2019 Uwe Schitt <uwe.schmitt@id.ethz.ch>


from emzed import PeakMap

from ._java_utils import run_java
from ._parameters import ParameterBaseMeta
from ._utils import cleanup_temp_files


class RemoveShoulderPeaksParameters(metaclass=ParameterBaseMeta):
    _fields = ["peakModel", "resolution"]
    _java_class = "ShoulderPeaksFilterParameters"

    _defaults = {"peak_model": "GAUSS", "resolution": 100_000}

    def _check_resolution(self, value):
        return value > 0, "value must be positive"


@cleanup_temp_files
def remove_shoulder_peaks(peakmap, parameters):
    """runs ShoulderPeaksFilte from MZmine2.

    :param peakmap: PeakMap object

    :param parameters: RemoveShoulderPeaks object

    :return: new PeakMap object withs houlder peaks removed.
    """
    assert isinstance(peakmap, PeakMap)
    assert isinstance(parameters, RemoveShoulderPeaksParameters)

    assert parameters.resolution is not None, "please set resolution"
    assert parameters.peak_model is not None, "please set peak_model"

    temp_file_in = mktemp(".mzML")  # noqa: F821
    temp_file_out = mktemp(".mzML")  # noqa: F821

    # todo: test with mixed ms level file
    # restore order.

    pm_ms_1 = peakmap.extract(mslevelmax=1)
    pm_ms_else = peakmap.extract(mslevelmin=2)

    if not len(pm_ms_1):
        return peakmap

    pm_ms_1.save(temp_file_in)

    run_java(
        "RemoveShoulderPeaks",
        temp_file_in,
        parameters.resolution,
        parameters.peak_model,
        temp_file_out,
    )

    peakmap_back = PeakMap.load(temp_file_out)

    # the mzXML parser of mzmine2 rounds rt values, we fix this here:
    with peakmap_back.spectra_for_modification() as spectra_back:
        for s, s_back in zip(pm_ms_1, spectra_back):
            s_back._set_rt(s.rt)

    peakmap_back.merge(pm_ms_else)

    return peakmap_back
