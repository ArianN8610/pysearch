import click
from pathlib import Path

from .utils import highlight_matches


def search_in_names(base_path: str, query: str, is_file: bool = True) -> list[str]:
    """Search for file names"""
    base_path = Path(base_path)
    matches = []

    for p in base_path.rglob('*'):
        if query in p.name and (p.is_file() if is_file else p.is_dir()):
            p = str(p).replace(query, click.style(query, fg='green'))  # Specify the found part
            matches.append(p)

    return matches


def search_in_file_contents(base_path, query):
    """Search the contents of files"""
    base_path = Path(base_path)
    matches = []

    for file_path in base_path.rglob('*'):
        if file_path.is_file():
            try:
                for num, line in enumerate(file_path.read_text(encoding='utf-8', errors='ignore').splitlines(), 1):
                    if query in line:
                        highlighted_snippet = highlight_matches(line.strip(), query)
                        matches.append(
                            click.style(file_path, fg='blue')
                            + click.style(f' (Line {num}): ', fg='magenta')
                            + highlighted_snippet
                        )
            except Exception:
                continue  # Continue if there is an error (e.g. binary file)

    return matches
