import click
from pathlib import Path

from .utils import highlight_matches


def search_in_names(base_path: str, query: str, case_sensitive: bool, is_file: bool = True) -> list[str]:
    """Search for file names"""
    base_path = Path(base_path)
    matches = []

    if not case_sensitive:
        query = query.lower()

    for p in base_path.rglob('*'):
        p_name = p.name.lower() if not case_sensitive else p.name

        if query in p_name and (p.is_file() if is_file else p.is_dir()):
            p_name = p_name.replace(query, click.style(query, fg='green'))  # Specify the found part
            matches.append(str(p.parent) + '\\' + p_name)

    return matches


def search_in_file_contents(base_path: str, query: str, case_sensitive: bool) -> list[str]:
    """Search the contents of files"""
    base_path = Path(base_path)
    matches = []

    if not case_sensitive:
        query = query.lower()

    for file_path in base_path.rglob('*'):
        if file_path.is_file():
            try:
                for num, line in enumerate(file_path.read_text(encoding='utf-8', errors='ignore').splitlines(), 1):
                    line_content = line.lower() if not case_sensitive else line

                    if query in line_content:
                        highlighted_snippet = highlight_matches(line_content.strip(), query, case_sensitive)
                        matches.append(
                            click.style(file_path, fg='blue')
                            + click.style(f' (Line {num}): ', fg='magenta')
                            + highlighted_snippet
                        )
            except Exception:
                continue  # Continue if there is an error (e.g. binary file)

    return matches
