"""arm_cli package metadata."""

# Expose package version via setuptools-scm only
try:
    from ._version import version as __version__  # type: ignore[attr-defined]
except Exception:  # pragma: no cover - fallback for editable installs
    try:
        from importlib.metadata import version as _get_version
    except Exception:
        try:
            from importlib_metadata import version as _get_version  # type: ignore[no-redef]
        except Exception:
            _get_version = None  # type: ignore[assignment]
    if _get_version is not None:
        try:
            __version__ = _get_version("arm-cli")  # type: ignore[assignment]
        except Exception:
            __version__ = "0+unknown"  # type: ignore[assignment]
    else:
        __version__ = "0+unknown"  # type: ignore[assignment]
