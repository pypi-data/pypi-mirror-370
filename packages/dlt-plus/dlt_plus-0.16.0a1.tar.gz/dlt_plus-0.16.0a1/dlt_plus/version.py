from importlib.metadata import version as pkg_version

IMPORT_NAME = "dlt_plus"
PKG_NAME = "dlt-plus"
__version__ = pkg_version(PKG_NAME)
PKG_REQUIREMENT = f"{PKG_NAME}=={__version__}"
