import warnings


class TrueFoundryDeprecationWarning(DeprecationWarning):
    pass


def surface_truefoundry_deprecation_warnings() -> None:
    """Unmute TrueFoundry deprecation warnings."""
    warnings.filterwarnings(
        "default",
        category=TrueFoundryDeprecationWarning,
    )


def suppress_truefoundry_deprecation_warnings() -> None:
    """Mute TrueFoundry deprecation warnings."""
    warnings.filterwarnings(
        "ignore",
        category=TrueFoundryDeprecationWarning,
    )


def suppress_truefoundry_ml_autogen_warnings() -> None:
    """Mute TrueFoundry ML autogen warnings."""
    warnings.filterwarnings(
        "ignore",
        module="truefoundry.ml._autogen",
    )
