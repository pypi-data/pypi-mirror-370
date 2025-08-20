"""
file and dir utils
"""

import os
import pathlib
import shutil

from waflibs import log

logger = log.logger().get_logger()


def __write(filename, mode, contents):
    with open(filename, mode) as f:
        f.write(contents)


def write(filename, contents, append=False):
    mode = "w"
    if append:
        mode = "a"
    try:
        __write(filename, mode, contents)
    except FileNotFoundError as e:
        logger.debug(f"parent directories do not exist... creating")

        pathlib.Path(filename).parent.mkdir(parents=True, exist_ok=True)

        __write(filename, mode, contents)


def expand_vars(string):
    logger.debug(f"original string: {string}")

    full_string = os.path.expandvars(string)
    logger.debug(f"full expanded string: {full_string}")

    return full_string


def get_absolute_path(path):
    absolute_path = pathlibs.Path(expand_vars(path))
    logger.debug(f"absolute path: {absolute_path}")

    return absolute_path


get_full_path = get_absolute_path
full_path = get_absolute_path


def backup(dest, dry_run=False):
    """backup path"""

    dest_bak = pathlib.Path(f"{dest}.bak")

    logger.debug(f"removing backup file: {dest_bak}")
    remove(dest_bak, dry_run=dry_run)

    logger.debug("back up entry {}".format(dest_bak))

    logger.debug(f"backing up file/dir {dest} to {dest_bak}")
    try:
        copy(dest, dest_bak, dry_run=dry_run)
    except FileNotFoundError as e:
        logger.debug(f"ignoring error: {e}")


def backup_and_remove(dest, dry_run=False):
    """backup and remove path"""

    logger.debug(f"backing up and removing {dest}")

    backup(dest, dry_run=dry_run)

    remove(dest, dry_run=dry_run)


def remove(dest, dry_run=False):
    """remove path"""

    if dry_run:
        print(f"would remove {dest}")
        return

    if os.path.exists(dest) or os.path.islink(dest):
        if dest.is_dir() and not dest.is_symlink():
            logger.debug(f"removing dest dir: {dest}")

            shutil.rmtree(dest)
        else:
            logger.debug(f"removing dest: {dest}")

            dest.unlink(missing_ok=True)
    else:
        logger.debug(f"nothing to remove for {dest}")


def get_destination_location(dest, dotfile=True, target_dir="/tmp", custom=False):
    """get standardized destination location"""

    logger.debug(f"orig dest is: {dest}")
    if custom:
        logger.debug("using custom dir")

        dest_parts = dest.parts
        dest = pathlib.Path(f"{pathlib.Path(*dest_parts[1:])}-{dest_parts[0]}")
    logger.debug(f"real orig dest is: {dest}")

    parent_dir = os.getcwd()
    logger.debug(f"parent dir is {parent_dir}")
    final_target_dest = pathlib.Path(dest).absolute().relative_to(parent_dir)
    logger.debug(f"final target dest is {final_target_dest}")

    if dotfile:
        logger.debug("dotfile set to true... adding dot to dest")

        final_dest = pathlib.Path(target_dir, f".{final_target_dest}")
    else:
        logger.debug("dotfile not set to true... not adding dot to dest")

        final_dest = pathlib.Path(target_dir, final_target_dest)
    logger.debug(f"final dest: {final_dest}")

    return final_dest


get_dest_location = get_destination_location
get_dest_dir = get_destination_location
get_dest_file = get_destination_location


def get_parent_directory(directory, absolute=True):
    """get parent directory"""

    parent_dir = pathlib.Path(directory).parent
    if absolute:
        logger.debug(f"getting absolute path for {parent_dir}")

        parent_dir = parent_dir.absolute()
    logger.debug(f"parent dir: {parent_dir}")

    return parent_dir


get_parent_dir = get_parent_directory


def copy(src, dest, dir_exist=False, dry_run=False):
    """copy path"""

    if dry_run:
        print(f"would copy {src} to {dest}")
    else:
        if not dest.parent.exists():
            dest.mkdir(parents=True)

        if src.is_dir():
            return shutil.copytree(
                src,
                dest,
                ignore_dangling_symlinks=True,
                symlinks=True,
                dirs_exist_ok=dir_exist,
            )
        else:
            return shutil.copy2(
                src,
                dest,
                follow_symlinks=False,
            )
