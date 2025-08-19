"""Backup iCloud iBooks epub dir as an epub archive."""
# iCloud stores epubs exploded on disk.

import os
from argparse import Namespace
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile

from termcolor import cprint

ZIP_MTIME_MIN = 315644400.0  # 1 day after 1980 for timezones


def _get_src_file_mtime(src_file_path: Path) -> float:
    """Get source file mtime, but alter it if pkzip will reject it."""
    src_file_mtime = src_file_path.stat().st_mtime
    if src_file_mtime < ZIP_MTIME_MIN:
        cprint(f"\tUpdating mtime for zip compatibility: {src_file_path}", "yellow")
        src_file_path.touch()
        src_file_mtime = src_file_path.stat().st_mtime
    return src_file_mtime


def get_dest_file_mtime(dest_path: Path) -> float:
    """Get Destination file mtime."""
    return dest_path.stat().st_mtime if dest_path.exists() else 0.0


def _get_updated_files(
    archive_mtime: float, epub_dir_src_path: Path, args: Namespace
) -> frozenset[Path]:
    """Check for updated files."""
    src_paths = set()
    update = False

    for root, _, src_files in os.walk(epub_dir_src_path):
        root_path = Path(root)
        for src_filename in sorted(src_files):
            src_file_path = root_path / src_filename
            src_paths.add(src_file_path)
            src_file_mtime = _get_src_file_mtime(src_file_path)
            update = update or src_file_mtime > archive_mtime

    if not update and not args.force:
        src_paths = set()

    return frozenset(src_paths)


def _archive_epub(
    epub_dest_path: Path, src_paths: frozenset[Path], args: Namespace
) -> None:
    """Make a new archive in a tempfile."""
    cprint(f"\nArchiving: {epub_dest_path.name}", "cyan")
    new_epub_path = epub_dest_path.with_suffix(".epub_new")

    with ZipFile(
        new_epub_path, mode="w", compression=ZIP_DEFLATED, compresslevel=9
    ) as epub:
        for src_file_path in sorted(src_paths):
            ctype = ZIP_STORED if src_file_path.name == "mimetype" else ZIP_DEFLATED
            epub.write(src_file_path, compress_type=ctype)
            if args.verbose:
                cprint(f"\t{src_file_path}", "cyan")

    # Move tempfile over old epub
    new_epub_path.replace(epub_dest_path)


def backup_epub_dir(epub_dir_src_path: Path, args: Namespace) -> bool:
    """Compress the exploded epub dir to the backup destination."""
    epub_dest_path = args.dest / epub_dir_src_path.name
    archive_mtime = get_dest_file_mtime(epub_dest_path)
    if src_paths := _get_updated_files(archive_mtime, epub_dir_src_path, args):
        _archive_epub(epub_dest_path, src_paths, args)
        return True
    return False
