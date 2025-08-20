"""
Migrate all files from legacy config directories to the new config directory. Any migration of the content is handled by specific migration
scripts later in the migration process.
"""

import shutil
import sys
from pathlib import Path

INCORRECT_CONFIG_DIR_PATH = Path.home() / ".config" / ".remotive"
DEPRECATED_CONFIG_DIR_PATH = Path.home() / ".remotive"
DEPRECATED_CONFIG_DIRS = [DEPRECATED_CONFIG_DIR_PATH, INCORRECT_CONFIG_DIR_PATH]


def _copy_dir_fail_on_conflict(src: Path, dst: Path) -> None:
    if not dst.is_dir():
        dst.mkdir(parents=True, exist_ok=True)

    for item in src.iterdir():
        src_file = src / item.name
        dst_file = dst / item.name

        if src_file.is_file():
            if dst_file.exists():
                raise FileExistsError(f"File '{dst_file}' already exists.")
            shutil.copy2(src_file, dst_file)  # preserve metadata


def migrate_legacy_settings_dir(path: Path, target_dir: Path) -> None:
    if not path.exists():
        return

    sys.stderr.write(f"found legacy config directory {path}, trying to migrate to {target_dir}\n")
    try:
        _copy_dir_fail_on_conflict(path, target_dir)
        shutil.rmtree(str(path))
    except FileExistsError as e:
        sys.stderr.write(
            f"file {e.filename} already exists in {target_dir}, so files in {path} cannot be migrated without risk of data loss. \
            Please remove or move the files to {target_dir} manually and make sure to remove {path}.\n"
        )
        raise e


def migrate_legacy_settings_dirs(target_dir: Path) -> None:
    """
    Migrate any valid configuration from legacy config directories to the new config directory.
    """
    for deprecated_config_dir in DEPRECATED_CONFIG_DIRS:
        migrate_legacy_settings_dir(deprecated_config_dir, target_dir)
