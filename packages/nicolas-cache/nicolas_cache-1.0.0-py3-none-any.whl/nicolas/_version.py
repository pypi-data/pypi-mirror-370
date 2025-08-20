# type: ignore
"""Version information for nicolas-cache."""

try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    # Python < 3.8
    from importlib_metadata import version, PackageNotFoundError

try:
    __version__ = version("nicolas")
except PackageNotFoundError:
    # Package not installed, try to get version from setuptools-scm
    try:
        from setuptools_scm import get_version
        import os

        # Get the root directory (two levels up from this file)
        root_dir = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        __version__ = get_version(root=root_dir)
    except (ImportError, OSError, LookupError):
        # Fallback version in CalVer format (YY.MM.DD)
        __version__ = "25.07.16-dev"

__all__ = ["__version__"]
