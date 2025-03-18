import re
import click
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from .utils import highlight_matches


def search_in_names(base_path, query, case_sensitive, regex, include, exclude, whole_word, max_size, min_size,
                    ext=tuple(), is_file=True):
    """Search for file and folder names"""
    base_path = Path(base_path)
    matches = []

    if not regex:
        query = re.escape(query)  # If regex is disabled, convert query to plain text

    if whole_word:
        query = rf'\b{query}\b'  # Ensure search for whole words

    flags = 0 if case_sensitive else re.IGNORECASE  # Adjust case sensitivity

    # Convert include and exclude paths to `Path`
    include_paths = {Path(p).resolve() for p in include}
    exclude_paths = {Path(p).resolve() for p in exclude}

    for p in base_path.rglob('*'):
        p_resolved = p.resolve()  # Actual file or folder path
        p_size_mb = p_resolved.stat().st_size / 1_048_576  # Convert to MB

        if (
                # If include is given, at least one of them must be present in the name
                (include and not any(p_resolved.is_relative_to(inc) for inc in include_paths))
                # If exclude is given, none should be in the name
                or (exclude and any(p_resolved.is_relative_to(exc) for exc in exclude_paths))
                # Prevent unnecessary continuation in case of type mismatch
                or (is_file and ext and p.suffix[1:] not in ext)
                # Check file or directory size
                or (max_size and p_size_mb > max_size)
                or (min_size and p_size_mb < min_size)
        ):
            continue

        if re.search(query, p.name, flags) and ((is_file and p.is_file()) or (not is_file and p.is_dir())):
            # Specify the found part
            highlighted_name = re.sub(query, lambda m: click.style(m.group(), fg='green'), p.name, flags=flags)
            matches.append(f'{p.parent}\\{highlighted_name}')

    return matches


def search_in_file_contents(base_path, query, case_sensitive, ext, regex, include, exclude, whole_word,
                            max_size, min_size):
    """Search inside file contents"""
    base_path = Path(base_path)
    matches = []

    if not regex:
        query = re.escape(query)

    if whole_word:
        query = rf'\b{query}\b'

    flags = 0 if case_sensitive else re.IGNORECASE

    include_paths = {Path(p).resolve() for p in include}
    exclude_paths = {Path(p).resolve() for p in exclude}

    def process_file(file_path):
        """Processes a single file and searches for the query inside its content."""
        p_resolved = file_path.resolve()
        p_size_mb = p_resolved.stat().st_size / 1_048_576

        if (
                # Filter by include/exclude directories
                (include and not any(p_resolved.is_relative_to(inc) for inc in include_paths))
                or (exclude and any(p_resolved.is_relative_to(exc) for exc in exclude_paths))
                # Filter by extension
                or (ext and p_resolved.suffix[1:] not in ext)
                # Filter by file size
                or (max_size and p_size_mb > max_size)
                or (min_size and p_size_mb < min_size)
        ):
            return

        try:
            for num, line in enumerate(p_resolved.read_text(encoding='utf-8', errors='ignore').splitlines(), 1):
                line = line.strip()

                if re.search(query, line, flags):
                    highlighted_snippet, count_query = highlight_matches(line, query, case_sensitive, regex, whole_word)
                    matches.append(
                        click.style(file_path, fg='cyan')
                        + click.style(f' (Line {num}) (Repeated {count_query} time(s)): ', fg='magenta')
                        + highlighted_snippet
                    )
        except Exception:
            return  # Ignore unreadable files

    # Use multi-threading for faster processing
    with ThreadPoolExecutor() as executor:
        executor.map(process_file, (file for file in base_path.rglob('*') if file.is_file()))

    return matches
