"""mysharelib utils directory."""
import os
from typing import Tuple
from openbb_core.app.utils import get_user_cache_directory

_project_name = __name__

def get_project_name() -> str:
    """
    Get the project name.

    Returns:
        str: The project name.
    """
    return _project_name

def get_log_path(project: str = _project_name) -> str:
    """
    Get the path of the log file.

    Returns:
        str: The path to the log file.
    """
    log_dir = f"{get_user_cache_directory()}/{project}"
    log_path = f"{log_dir}/{project}.log"

    os.makedirs(log_dir, exist_ok=True)

    return log_path

def get_cache_path(project: str = _project_name) -> str:
    """
    Get the path of the cache database.

    Returns:
        str: The path to the cache database.
    """
    db_dir = f"{get_user_cache_directory()}/{project}"
    db_path = f"{db_dir}/equity.db"

    os.makedirs(db_dir, exist_ok=True)

    return db_path