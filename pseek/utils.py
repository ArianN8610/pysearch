import re
import sys
import click


def compile_regex(txt, flags=0):
    if txt is not None:
        try:
            return re.compile(txt, flags)
        except re.error as e:
            click.echo(click.style(f"Regex compile error: {e}", fg='red'))
            sys.exit(1)


def get_archive_path_size(info, file_type: str) -> float:
    """Get and return the size of the files inside the archive files in MB"""
    if file_type == 'zip':
        return info.file_size / 1_048_576
    elif file_type == '7z':
        return info.uncompressed / 1_048_576
    elif file_type in ('tar', 'tar.gz', 'tar.bz2', 'tar.xz'):
        return info.size / 1_048_576
