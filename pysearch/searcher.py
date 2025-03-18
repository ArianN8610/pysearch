import re
import click
from pathlib import Path

from .utils import highlight_matches


def search_in_names(base_path, query, case_sensitive, regex, include, exclude, whole_word, ext=tuple(), is_file=True):
    """Search for file and folder names"""
    base_path = Path(base_path)
    matches = []

    if not regex:
        query = re.escape(query)  # If regex is disabled, convert query to plain text

    if whole_word:
        query = rf'\b{query}\b'  # Ensure search for whole words

    flags = 0 if case_sensitive else re.IGNORECASE  # Adjust case sensitivity

    # Convert include and exclude paths to `Path`
    include_paths = [Path(p).resolve() for p in include]
    exclude_paths = [Path(p).resolve() for p in exclude]

    for p in base_path.rglob('*'):
        p_resolved = p.resolve()  # Actual file or folder path

        if (
                # If include is given, at least one of them must be present in the name
                (include and not any(p_resolved.is_relative_to(inc) for inc in include_paths))
                # If exclude is given, none should be in the name
                or (exclude and any(p_resolved.is_relative_to(exc) for exc in exclude_paths))
                # Prevent unnecessary continuation in case of type mismatch
                or (is_file and ext and p.suffix[1:] not in ext)
        ):
            continue

        if re.search(query, p.name, flags) and ((is_file and p.is_file()) or (not is_file and p.is_dir())):
            # Specify the found part
            highlighted_name = re.sub(query, lambda m: click.style(m.group(), fg='green'), p.name, flags=flags)
            matches.append(f'{p.parent}\\{highlighted_name}')

    return matches


def search_in_file_contents(base_path, query, case_sensitive, ext, regex, include, exclude, whole_word):
    """Search inside file contents"""
    base_path = Path(base_path)
    matches = []

    if not regex:
        query = re.escape(query)

    if whole_word:
        query = rf'\b{query}\b'

    flags = 0 if case_sensitive else re.IGNORECASE

    include_paths = [Path(p).resolve() for p in include]
    exclude_paths = [Path(p).resolve() for p in exclude]

    for file_path in base_path.rglob('*'):
        p_resolved = file_path.resolve()

        if (
                (include and not any(p_resolved.is_relative_to(inc) for inc in include_paths))
                or (exclude and any(p_resolved.is_relative_to(exc) for exc in exclude_paths))
                or (not file_path.is_file() or (ext and file_path.suffix[1:] not in ext))
        ):
            continue

        try:
            for num, line in enumerate(file_path.read_text(encoding='utf-8', errors='ignore').splitlines(), 1):
                line = line.strip()

                if re.search(query, line, flags):
                    highlighted_snippet, count_query = highlight_matches(line, query, case_sensitive, regex, whole_word)

                    matches.append(
                        click.style(file_path, fg='cyan')
                        + click.style(f' (Line {num}) (Repeated {count_query} time(s)): ', fg='magenta')
                        + highlighted_snippet
                    )
        except Exception:
            continue  # Continue if there is an error (e.g. binary file)

    return matches
