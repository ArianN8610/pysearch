import re
import click
from pathlib import Path

from .utils import highlight_matches


def search_in_names(base_path: str, query: str, case_sensitive: bool, regex: bool, ext: tuple[str] = tuple(),
                    is_file: bool = True) -> list[str]:
    """Search for file names"""
    base_path = Path(base_path)
    matches = []

    if not regex:
        query = re.escape(query)  # If regex is disabled, convert query to plain text

    flags = 0 if case_sensitive else re.IGNORECASE  # Adjust case sensitivity

    for p in base_path.rglob('*'):
        if re.search(query, p.name, flags) and ((is_file and p.is_file()) or (not is_file and p.is_dir())):
            if is_file and ext and p.suffix[1:] not in ext:
                continue  # Prevent unnecessary continuation in case of type mismatch

            p_name = re.sub(query, lambda m: click.style(m.group(), fg='green'), p.name, flags=flags)  # Specify the found part
            matches.append(f'{p.parent}\\{p_name}')

    return matches


def search_in_file_contents(base_path: str, query: str, case_sensitive: bool, ext: tuple[str],
                            regex: bool) -> list[str]:
    """Search the contents of files"""
    base_path = Path(base_path)
    matches = []

    if not regex:
        query = re.escape(query)  # Convert to plain text

    flags = 0 if case_sensitive else re.IGNORECASE  # Adjust case sensitivity

    for file_path in base_path.rglob('*'):
        if not file_path.is_file() or (ext and file_path.suffix[1:] not in ext):
            continue

        try:
            for num, line in enumerate(file_path.read_text(encoding='utf-8', errors='ignore').splitlines(), 1):
                if re.search(query, line, flags):
                    highlighted_snippet = highlight_matches(line.strip(), query, case_sensitive)
                    count_query = len(list(re.finditer(query, line, flags)))  # Count the number of repetitions

                    matches.append(
                        click.style(file_path, fg='blue')
                        + click.style(f' (Line {num}) (Repeated {count_query} time(s)): ', fg='magenta')
                        + highlighted_snippet
                    )
        except Exception:
            continue  # Continue if there is an error (e.g. binary file)

    return matches
