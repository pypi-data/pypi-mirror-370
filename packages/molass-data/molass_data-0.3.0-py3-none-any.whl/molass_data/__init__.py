"""
__init__.py
"""

def get_version(toml_only=False):
    """
    Returns the version of the molass_data package.
    """
    from molass import _get_version_impl
    return _get_version_impl(toml_only, __file__, __package__)

def get_data_path(subfolder):
    """
    Returns the path to the tutorial data directory.
    """
    import os
    this_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(this_dir, subfolder)

SAMPLE1 = get_data_path("SAMPLE1")
SAMPLE2 = get_data_path("SAMPLE2")
SAMPLE3 = get_data_path("SAMPLE3")
SAMPLE4 = get_data_path("SAMPLE4")