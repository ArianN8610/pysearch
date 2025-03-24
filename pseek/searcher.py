import re
import sys
import click
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# Extensions that are not suitable for content search (binary, media, etc.)
EXCLUDED_EXTENSIONS = {
    'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp', 'svg',
    'mp4', 'mov', 'avi', 'mkv', 'webm', 'flv', 'm4v', 'mpg', 'wmv',
    'mp3', 'wav', 'ogg', 'flac', 'aac', 'wma', 'opus',
    'exe', 'dll', 'bin', 'iso', 'img', 'dat', 'dmg', 'class', 'so', 'o', 'obj',
    'zip', 'rar', '7z', 'tar', 'gz', 'bz2', 'xz',
    'ttf', 'otf', 'woff', 'woff2', 'eot',
    'db', 'sqlite', 'mdf', 'bak', 'log', 'jsonl', 'dat',
    'apk', 'ipa', 'deb', 'rpm', 'pkg', 'appimage', 'jar', 'war',
    'pyc', 'ps1', 'pem', 'pyd', 'whl'
}


class Search:
    def __init__(self, base_path, query, case_sensitive, ext, exclude_ext, regex, include, exclude, whole_word,
                 max_size, min_size, full_path):
        """Initialize search parameters"""
        self.base_path = base_path
        self.query = query
        self.case_sensitive = case_sensitive
        self.ext = ext
        self.exclude_ext = exclude_ext
        self.regex = regex
        self.include = include
        self.exclude = exclude
        self.whole_word = whole_word
        self.max_size = max_size
        self.min_size = min_size
        self.full_path = full_path
        self.result = None

    def conditions(self, p_resolved: Path, search_type: str) -> bool:
        """
        Check whether the file/directory should be skipped based on various filters.
        Returns True if the path should be skipped.
        """
        try:
            p_size_mb = p_resolved.stat().st_size / 1_048_576  # Convert size to MB
        except OSError:
            # If path is inaccessible, skip it.
            return True

        # Prepare include/exclude sets as resolved Paths
        include_paths = {Path(p).resolve() for p in self.include}
        exclude_paths = {Path(p).resolve() for p in self.exclude}

        file_ext = p_resolved.suffix[1:]

        # Conditions for skipping:
        if (include_paths and not any(p_resolved.is_relative_to(inc) for inc in include_paths)) \
                or (exclude_paths and any(p_resolved.is_relative_to(exc) for exc in exclude_paths)) \
                or (self.ext and file_ext not in self.ext) \
                or (self.exclude_ext and file_ext in self.exclude_ext) \
                or (search_type == 'content' and file_ext in EXCLUDED_EXTENSIONS) \
                or (self.max_size and p_size_mb > self.max_size) \
                or (self.min_size and p_size_mb < self.min_size) \
                or ((search_type in ('file', 'content')) and not p_resolved.is_file()) \
                or (search_type == 'directory' and not p_resolved.is_dir()):
            return True

        return False

    def search(self, search_type: str):
        """Main search function. search_type can be 'file', 'directory' or 'content'"""
        base_path = Path(self.base_path).resolve()
        query = self.query

        # Prepare query: escape if not regex
        if not self.regex:
            query = re.escape(query)
        else:
            try:
                re.compile(query)  # Validate regex pattern
            except re.error:
                click.echo(click.style('Invalid regex pattern: ', fg='red') + query)
                sys.exit(1)

        # Apply whole-word matching only if not using regex (or if desired behavior is defined)
        if self.whole_word and not self.regex:
            query = rf'\b{query}\b'

        flags = 0 if self.case_sensitive else re.IGNORECASE  # Adjust case sensitivity

        # Precompile the regex pattern for performance
        try:
            pattern = re.compile(query, flags)
        except re.error as e:
            click.echo(click.style(f"Regex compile error: {e}", fg='red'))
            sys.exit(1)

        if search_type in ('file', 'directory'):
            matches = []
            for p in base_path.rglob('*'):
                try:
                    p_resolved = p.resolve()
                except Exception:
                    continue
                # Skip if conditions fail or if name doesn't match the query
                if self.conditions(p_resolved, search_type) or not pattern.search(p.name):
                    continue

                # Highlight matched query in the name
                highlighted_name = pattern.sub(lambda m: click.style(m.group(), fg='green'), p.name)
                # Choose parent path based on full_path flag
                p_parent = p_resolved.parent if self.full_path else p.parent
                matches.append(f'{p_parent}\\{highlighted_name}')
        else:  # For content search
            # Use dictionary: key: file path (colored), value: list of line matches
            matches = {}

            def process_file(file_path: Path):
                """Process a single file for content search"""
                try:
                    p_resolved = file_path.resolve()
                except Exception:
                    return

                # Skip file if any filter condition is met
                if self.conditions(p_resolved, 'content'):
                    return

                line_matches = []
                try:
                    # Read file line by line
                    with open(p_resolved, 'r', encoding='utf-8', errors='ignore') as f:
                        for num, line in enumerate(f, 1):
                            line = line.strip()
                            if pattern.search(line):
                                # Count occurrences of query in line
                                count = len(list(pattern.finditer(line)))
                                highlighted_line = pattern.sub(lambda m: click.style(m.group(), fg='green'), line)
                                count_query = f'- Repeated {count} times' if count >= 3 else ''
                                line_matches.append(
                                    click.style(f'Line {num}{count_query}: ', fg='magenta') + highlighted_line
                                )
                except Exception:
                    return  # Skip unreadable files

                if line_matches:
                    file_label = str(p_resolved) if self.full_path else str(file_path)
                    # Use colored file path as key
                    matches[click.style(file_label, fg='cyan')] = line_matches

            # Create a list of files to process (filter out inaccessible ones early)
            files_to_process = [file for file in base_path.rglob('*')]
            with ThreadPoolExecutor() as executor:
                executor.map(process_file, files_to_process)

        self.result = matches
        return self

    def echo(self, title: str, result_name: str) -> int:
        """
        Display the search results with a title.
        Returns the count of results.
        """
        count_result = 0

        if self.result:
            click.echo(click.style(f'\n{title}:\n', fg='yellow'))
            if isinstance(self.result, dict):
                # For content search results
                for key, value in self.result.items():
                    click.echo(key)
                    click.echo('\n'.join(value) + '\n')
                    count_result += len(value)
            else:
                # For file/directory search results
                count_result = len(self.result)
                click.echo('\n'.join(self.result))

            if count_result >= 3:
                click.echo(click.style(f'\n{count_result} results found for {result_name}', fg='blue'))

        return count_result
