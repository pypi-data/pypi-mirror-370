from importlib.metadata import version as _version

from ._installers import get_jre_home, get_mzmine2_home

__version__ = _version(__package__)

if get_mzmine2_home() is None or get_jre_home() is None:

    def init():
        from ._installers import (
            get_jre_home,
            get_mzmine2_home,
            install_example_files,
            install_jre,
            install_mzmine2,
        )

        if get_mzmine2_home() is not None and get_jre_home() is not None:
            print("you ran init() already")
            return

        install_jre()
        print()
        install_mzmine2()
        print()
        install_example_files()

        import importlib

        importlib.import_module(__name__)

        print()
        print("init done, please create new session to use emzed.ext.mzmine2")

    # cleanup ns
    del get_jre_home
    del get_mzmine2_home

    print("please execute:")
    print()
    print(f"import {__package__}")
    print(f"{__package__}.init()")
    print()

    def __getattr__(name):
        raise ImportError(
            f"\n{__package__}.{name} not available,"
            f" please call {__package__}.init() first"
        )

    def __dir__():
        return ["init"]


else:
    # cleanup ns
    del get_jre_home
    del get_mzmine2_home

    def init():
        print("nothing to do")

    from .adduct_search import AdductSearchParameters, adduct_search
    from .fragment_search import FragmentSearchParameters, fragment_search
    from .isotope_grouper import IsotopeGrouperParameters, isotope_grouper
    from .join_aligner import (
        IsotopePatternScoreParameters,
        JoinAlignerParameters,
        join_aligner,
    )
    from .pick_peaks import (
        ADAPChromatogramBuilder,
        ADAPDetector,
        BaselinePeakDetector,
        IntensityWindowsSNParameters,
        MinimumSearchPeakDetector,
        NoiseAmplitudePeakDetector,
        RemoveShoulderPeaksParameters,
        SavitzkyGolayPeakDetector,
        WaveletCoefficientsSNParameters,
        pick_peaks,
    )
    from .remove_shoulder_peaks import remove_shoulder_peaks

    __all__ = [
        "ADAPChromatogramBuilder",
        "ADAPDetector",
        "AdductSearchParameters",
        "BaselinePeakDetector",
        "FragmentSearchParameters",
        "IntensityWindowsSNParameters",
        "IsotopeGrouperParameters",
        "IsotopeGrouperParameters",
        "IsotopePatternScoreParameters",
        "JoinAlignerParameters",
        "MinimumSearchPeakDetector",
        "NoiseAmplitudePeakDetector",
        "RemoveShoulderPeaksParameters",
        "RemoveShoulderPeaksParameters",
        "SavitzkyGolayPeakDetector",
        "WaveletCoefficientsSNParameters",
        "adduct_search",
        "fragment_search",
        "isotope_grouper",
        "join_aligner",
        "pick_peaks",
        "remove_shoulder_peaks",
    ]
