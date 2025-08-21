"""
This module has wrappers over Python built-ins for filsystem operations
"""

import shutil
from pathlib import Path
import os

from iccore.runtime import ctx


def copy(src: Path, dst: Path) -> None:
    """
    Copy the file or directory from `src` to `dst`
    :param src: The location to copy from
    :param dst: The location to copy to
    """

    if ctx.can_modify():
        shutil.copy(src, dst)
    else:
        ctx.add_cmd(f"copy {src} {dst}")


def make_archive(archive: Path, fmt: str, src: Path, rename: bool = False) -> None:
    """
    Create an archive with name `archive_name` and chosen format, e.g. zip
    from the content in `src`
    :param Path archive_name: The path to the created archive
    :param str fmt: The desired archive format, e.g. zip
    :param Path src: The src of the content to be archived
    :param bool rename: If true rename source directory to have the archive name
    """

    if ctx.can_modify():
        if rename:
            shutil.copytree(src, archive)
            src = archive
        shutil.make_archive(str(archive), fmt, src)
        if rename:
            shutil.rmtree(archive)
    else:
        ctx.add_cmd(f"make_archive {archive} {fmt} {src}")


def unpack_archive(src: Path, dst: Path) -> None:
    """
    Extract the archive at `src` to `dst`
    """

    if ctx.can_modify():
        shutil.unpack_archive(src, dst)
    else:
        ctx.add_cmd(f"unpack_archive {src} {dst}")


def copy_file(src: Path, dst: Path):
    """
    Copy a file in src to the target directory in dst

    Make the dst directory if needed
    """
    os.makedirs(dst, exist_ok=True)
    shutil.copy(src, dst / src.name)


def copy_files(src: Path, dst: Path):
    """
    Copy all files from the `src` directory to the `dst` directory

    Create the dst directory first if needed.

    :param Path src: The directory to copy from
    :param Path dst: The directory to copy to
    """
    os.makedirs(dst, exist_ok=True)
    for direntry in src.iterdir():
        if direntry.is_file():
            shutil.copy(direntry, dst)


def copy_files_relative(paths: list[Path], src: Path, dst: Path):
    """
    For each relative path in `paths` copy the file at `src/path` to
    `dst/path`.

    Tries to create the dst directory first.

    :param list[Path] paths: The list of paths to copy
    :param Path src: The source path to copy relative to
    :param Path dst: The destination path to copy into.
    """

    for path in paths:
        os.makedirs(dst / path.parent, exist_ok=True)
        shutil.copy(src / path, dst / path)


def clear_dir(src: Path):
    """
    If there is a directory at `src` delete it and make a new one
    """

    if src.exists():
        shutil.rmtree(src)
    os.makedirs(src)


def read_file(src: Path):
    """
    Read a file at the provided path
    """
    with open(src, "r", encoding="utf-8") as f:
        return f.read()


def read_file_lines(src: Path):
    """
    Read a file as lines
    """

    with open(src, "r", encoding="utf-8") as f:
        return f.readlines()


def write_file_lines(
    src: Path, lines: list[str], make_parents: bool = True, make_exe: bool = False
):
    """
    Write a file with lines
    """

    if make_parents:
        os.makedirs(src.parent, exist_ok=True)

    with open(src, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line)

    if make_exe:
        os.chmod(src, 0o0755)


def write_file(src: Path, content: str, make_parents: bool = True):
    """
    Write a file
    """
    if make_parents:
        os.makedirs(src.parent, exist_ok=True)

    with open(src, "w", encoding="utf-8") as f:
        f.write(content)


def replace_in_file(src: Path, search_term: str, replace_term: str) -> bool:
    """
    Replace the search term in a file
    """

    content = read_file_lines(src)
    has_update = False
    for idx, line in enumerate(content):
        replaced_line = line.replace(search_term, replace_term)
        if replaced_line != line:
            content[idx] = replaced_line
            has_update = True
    if has_update:
        write_file_lines(src, content)
        return True
    return False


def replace_in_files(
    src: Path, search_term: str, replace_term: str, extension: str
) -> int:
    """
    Replace a search term in multiple files
    """

    count = 0
    for direntry in src.iterdir():
        if direntry.is_file():
            if not extension or direntry.suffix == f".{extension}":
                replaced = replace_in_file(direntry, search_term, replace_term)
                if replaced:
                    count += 1
    return count


def file_contains_string(src: Path, search_term: str) -> bool:
    """
    True if a file contains the search term
    """
    content = read_file(src)
    return search_term in content


def get_dirs(path: Path, prefix: str = "") -> list[Path]:
    """
    Return all directories in a path, optionally filter directory
    name on a prefix
    """
    if prefix:
        return [
            entry
            for entry in path.iterdir()
            if entry.is_dir() and entry.name.startswith(prefix)
        ]
    return [entry for entry in path.iterdir() if entry.is_dir()]


def is_file_with_ext(f, extension: str) -> bool:
    """
    True if the path item is a file with given extension
    """
    return f.is_file() and str(f).endswith(f".{extension}")


def get_files(path: Path, extension: str) -> list:
    """
    Return all files in this dir with the provided extension
    """
    return [f for f in path.glob("*") if is_file_with_ext(f, extension)]


def is_file_with_extensions(
    f, extensions: tuple[str], excludes: list[str] | None = None
):
    """
    True if the path item is a file and has one of the provided extensions
    """

    if not f.is_file():
        return False
    for ext in extensions:
        check_str = str(f).lower()
        if check_str.endswith(f".{ext.lower()}"):
            if excludes:
                for exclude in excludes:
                    if check_str.endswith(f"{exclude.lower()}.{ext.lower()}"):
                        return False
            return True
    return False


def get_files_recursive(
    path: Path, extensions: tuple[str], excludes: list[str] | None = None
):
    """
    Get all provided files recursively, filter on extensions and excludes
    """
    return [
        f for f in path.rglob("*") if is_file_with_extensions(f, extensions, excludes)
    ]


def get_json_files(path: Path):
    """
    Get all json files in this dir
    """
    return get_files(path, extension="json")


def get_csv_files(path: Path):
    """
    Get all csv files in this dir
    """
    return get_files(path, extension="csv")
