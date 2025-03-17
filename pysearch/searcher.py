import re
import click
from pathlib import Path

from .utils import highlight_matches


def search_in_names(
        base_path: str, query: str, case_sensitive: bool,
        regex: bool, include: tuple[str], exclude: tuple[str],
        whole_word: bool, ext: tuple[str] = tuple(), is_file: bool = True
) -> list[str]:
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

        # If include is given, at least one of them must be present in the name
        if include and not any(p_resolved.is_relative_to(inc) for inc in include_paths):
            continue

        # If exclude is given, none should be in the name
        if exclude and any(p_resolved.is_relative_to(exc) for exc in exclude_paths):
            continue

        # Prevent unnecessary continuation in case of type mismatch
        if is_file and ext and p.suffix[1:] not in ext:
            continue

        if re.search(query, p.name, flags) and ((is_file and p.is_file()) or (not is_file and p.is_dir())):
            # Specify the found part
            highlighted_name = re.sub(query, lambda m: click.style(m.group(), fg='green'), p.name, flags=flags)
            matches.append(f'{p.parent}\\{highlighted_name}')

    return matches


def search_in_file_contents(
        base_path: str, query: str, case_sensitive: bool,
        ext: tuple[str], regex: bool, include: tuple[str],
        exclude: tuple[str], whole_word: bool
) -> list[str]:
    """Search the contents of files"""
    base_path = Path(base_path)
    matches = []

    if not regex:
        query = re.escape(query)  # Convert to plain text

    if whole_word:
        query = rf'\b{query}\b'  # Ensure search for whole words

    flags = 0 if case_sensitive else re.IGNORECASE  # Adjust case sensitivity

    # Convert include and exclude paths to `Path`
    include_paths = [Path(p).resolve() for p in include]
    exclude_paths = [Path(p).resolve() for p in exclude]

    for file_path in base_path.rglob('*'):
        p_resolved = file_path.resolve()  # Actual file path

        # If include is given, at least one of them must be present in the list
        if include and not any(p_resolved.is_relative_to(inc) for inc in include_paths):
            continue

        # If exclude is given, none should be in the list
        if exclude and any(p_resolved.is_relative_to(exc) for exc in exclude_paths):
            continue

        if not file_path.is_file() or (ext and file_path.suffix[1:] not in ext):
            continue

        try:
            for num, line in enumerate(file_path.read_text(encoding='utf-8', errors='ignore').splitlines(), 1):
                line = line.strip()

                if re.search(query, line, flags):
                    highlighted_snippet = highlight_matches(line, query, case_sensitive, regex, whole_word)
                    count_query = len(list(re.finditer(query, line, flags)))  # Count the number of repetitions

                    matches.append(
                        click.style(file_path, fg='blue')
                        + click.style(f' (Line {num}) (Repeated {count_query} time(s)): ', fg='magenta')
                        + highlighted_snippet
                    )
        except Exception:
            continue  # Continue if there is an error (e.g. binary file)

    return matches
