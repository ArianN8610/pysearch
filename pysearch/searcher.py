import re
import click
from pathlib import Path

from .utils import highlight_matches


def search_in_names(base_path: str, query: str, case_sensitive: bool, ext: str = '', is_file: bool = True) -> list[str]:
    """Search for file names"""
    base_path = Path(base_path)
    matches = []

    if not case_sensitive:
        query = query.lower()

    # Remove extra spaces and processing extensions
    ext_list = [e.strip() for e in ext.split(',') if e.strip()]

    for p in base_path.rglob('*'):
        p_name = p.name.lower() if not case_sensitive else p.name

        if query in p_name and ((is_file and p.is_file()) or (not is_file and p.is_dir())):
            if is_file and ext_list and p.suffix[1:] not in ext_list:
                continue  # Prevent unnecessary continuation in case of type mismatch

            p_name = p_name.replace(query, click.style(query, fg='green'))  # Specify the found part
            matches.append(f'{p.parent}\\{p_name}')

    return matches


def search_in_file_contents(base_path: str, query: str, case_sensitive: bool, ext: str) -> list[str]:
    """Search the contents of files"""
    base_path = Path(base_path)
    matches = []

    if not case_sensitive:
        query = query.lower()

    ext_list = [e.strip() for e in ext.split(',') if e.strip()]

    for file_path in base_path.rglob('*'):
        if not file_path.is_file() or (ext_list and file_path.suffix[1:] not in ext_list):
            continue

        try:
            for num, line in enumerate(file_path.read_text(encoding='utf-8', errors='ignore').splitlines(), 1):
                line_content = line.lower() if not case_sensitive else line

                if query in line_content:
                    highlighted_snippet = highlight_matches(line_content.strip(), query, case_sensitive)
                    count_query = len(re.findall(query, line_content))  # Count query in each line

                    matches.append(
                        click.style(file_path, fg='blue')
                        + click.style(f' (Line {num}) (Repeated {count_query} time(s)): ', fg='magenta')
                        + highlighted_snippet
                    )
        except Exception:
            continue  # Continue if there is an error (e.g. binary file)

    return matches
