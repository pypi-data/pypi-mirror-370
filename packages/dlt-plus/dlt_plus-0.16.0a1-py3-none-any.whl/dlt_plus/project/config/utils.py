import os
import tempfile
from typing import Mapping, Any, Callable, cast

from dlt.common.typing import TypeVar
from dlt.common.utils import (
    update_dict_nested as _update_dict_nested,
    clone_dict_nested as _clone_dict_nested,
)
from dlt.common.runtime.run_context import is_folder_writable
from dlt_plus.common.constants import DEFAULT_DATA_DIR

TMapping = TypeVar("TMapping", bound=Mapping[str, Any])

# TODO: maybe move to OSS, cast so TypedDict could be cloned
clone_dict_nested = cast(Callable[[TMapping], TMapping], _clone_dict_nested)
update_dict_nested = cast(Callable[[TMapping, Mapping[str, Any]], TMapping], _update_dict_nested)


def default_data_dir(project_dir: str, project_name: str, profile_name: str) -> str:
    """Computes default data dir which is relative to `project_dir` and separated by `profile_name`
    If `project_dir` is not writable, we fall back to temp dir.
    """
    data_dir = os.path.join(project_dir, DEFAULT_DATA_DIR)
    if not is_folder_writable(project_dir):
        # fallback to temp dir which should be writable, project name is used to separate projects
        data_dir = os.path.join(tempfile.gettempdir(), "dlt", DEFAULT_DATA_DIR, project_name)
    return os.path.join(data_dir, profile_name)
