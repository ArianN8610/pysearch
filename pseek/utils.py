import re
import sys
import click
import shutil
import rarfile
import platform
from pathlib import Path


def compile_regex(txt, flags=0):
    if txt is not None:
        try:
            return re.compile(txt, flags)
        except re.error as e:
            click.echo(click.style(f"Regex compile error: {e}", fg='red'))
            sys.exit(1)


def get_archive_path_size(info, file_type: str) -> float:
    """Get and return the size of the files inside the archive files in MB"""
    if file_type in ('zip', 'rar'):
        return info.file_size / 1_048_576
    elif file_type == '7z':
        return info.uncompressed / 1_048_576
    elif file_type in ('tar', 'tar.gz', 'tar.bz2', 'tar.xz'):
        return info.size / 1_048_576


def try_decode(data: bytes):
    """Try decoding byte data to UTF-8 text. Return None if decoding fails."""
    try:
        return data.decode('utf-8')
    except UnicodeDecodeError:
        return None


def check_rar_backend(archive_enabled: bool, tool_path: str, backend: str):
    """Check for the existence of rar backend or save and set it for rarfile"""

    backend_path = Path(__file__).parent / "RARBackend"
    # Save backend path for later executions
    if tool_path:
        if backend in ('unrar', 'bsdtar', 'unar', '7z'):
            with open(backend_path, 'w') as f:
                f.write(f'{backend}:{tool_path}')
            click.secho(f"RAR backend set to: {backend}", fg="green")
        else:
            click.secho("Unknown RAR backend tool. Please provide unrar, bsdtar, unar, or 7z.", fg="red")
        sys.exit(1)

    if archive_enabled:
        # Try to detect presence of RAR backends in PATH
        unrar_path = shutil.which('unrar')
        bsdtar_path = shutil.which('bsdtar')
        sevenzip_path = shutil.which('7z') or shutil.which('7za')  # Some versions are in 7za format
        unar_path = shutil.which('unar')

        if not any((unrar_path, bsdtar_path, sevenzip_path, unar_path)) and not backend_path.exists():
            system = platform.system()
            if system == 'Linux':
                install_tip = "sudo apt install unrar"
            elif system == 'Darwin':
                install_tip = "brew install unrar"
            else:
                install_tip = "Download from https://www.rarlab.com/download.htm"

            click.secho(
                "Warning: unrar, bsdtar, 7zip or unar is not installed on system or "
                "it is not in the system PATH.\nRAR archive support is disabled.\n"
                "To enable RAR support, please install one of them. For example:\n"
                f"  - {install_tip}\n"
                "If it is installed or in the system PATH and you still have problems, use this option: '--rarfb'\n",
                fg='yellow'
            )
        elif backend_path.exists():
            with open(backend_path, 'r') as f:
                b, tool = f.read().split(':', 1)

            # Set up the backend for rarfile
            if b == 'unrar':
                rarfile.UNRAR_TOOL = tool
            elif b == 'bsdtar':
                rarfile.BSDTAR_TOOL = tool
            elif b == 'unar':
                rarfile.UNAR_TOOL = tool
            elif b == '7z':
                rarfile.SEVENZIP_TOOL = tool
