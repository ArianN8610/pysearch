import re
import sys
import click
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# Extensions that are not suitable for content search
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

        self.result = []

    def conditions(self, p_resolved: Path, search_type: str) -> bool:
        """Check the correctness of path based on data"""

        try:
            p_size_mb = p_resolved.stat().st_size / 1_048_576  # Convert to MB
        except OSError:
            return True  # if path cannot be accessible

        # Convert include and exclude paths to `Path`
        include_paths = {Path(p).resolve() for p in self.include}
        exclude_paths = {Path(p).resolve() for p in self.exclude}

        if (
                # Filter by include/exclude directories and files
                (include_paths and not any(p_resolved.is_relative_to(inc) for inc in include_paths))
                or (exclude_paths and any(p_resolved.is_relative_to(exc) for exc in exclude_paths))
                # Filter by extension
                or (self.ext and p_resolved.suffix[1:] not in self.ext)
                or (self.exclude_ext and p_resolved.suffix[1:] in self.exclude_ext)
                or (search_type == 'content' and p_resolved.suffix[1:] in EXCLUDED_EXTENSIONS)
                # Filter by file size
                or (self.max_size and p_size_mb > self.max_size)
                or (self.min_size and p_size_mb < self.min_size)
                # Filter by path type
                or ((search_type == 'file' or search_type == 'content') and not p_resolved.is_file())
                or (search_type == 'directory' and not p_resolved.is_dir())
        ):
            return True

        return False

    def search(self, search_type: str):
        """Search for paths based on the query"""

        base_path = Path(self.base_path)
        query = self.query

        if not self.regex:
            query = re.escape(query)  # If regex is disabled, convert query to plain text
        else:
            try:
                re.compile(query)  # Ensure valid regex
            except re.error:
                click.echo(click.style('Invalid regex pattern: ', fg='red') + query)
                sys.exit(1)  # Exit the program with error code

        if self.whole_word:
            query = rf'\b{query}\b'  # Ensure search for whole words

        flags = 0 if self.case_sensitive else re.IGNORECASE  # Adjust case sensitivity

        if search_type == 'file' or search_type == 'directory':
            matches = []
            for p in base_path.rglob('*'):
                p_resolved = p.resolve()  # Actual file or folder path
                if self.conditions(p_resolved, search_type) or (not re.search(query, p.name, flags)):
                    continue

                # Specify the found part
                highlighted_name = re.sub(query, lambda m: click.style(m.group(), fg='green'), p.name, flags=flags)
                # Get full path if full_path is True
                p_parent = p_resolved.parent if self.full_path else p.parent

                matches.append(f'{p_parent}\\{highlighted_name}')
        else:
            matches = dict()
            def process_file(file_path):
                """Processes a single file and searches for the query inside its content."""
                p_resolved = file_path.resolve()
                line_matches = []

                try:
                    for num, line in enumerate(p_resolved.read_text(encoding='utf-8', errors='ignore').splitlines(), 1):
                        line = line.strip()
                        if re.search(query, line, flags):
                            # Count query in each line
                            count_query = len(list(re.finditer(query, line, flags)))
                            highlighted_name = re.sub(query, lambda m: click.style(m.group(), fg='green'), line,
                                                      flags=flags)
                            count_query = f'- Repeated {count_query} times' if count_query >= 3 else ''

                            line_matches.append(
                                click.style(f'Line {num}{count_query}: ', fg='magenta')
                                + highlighted_name
                            )
                except Exception:
                    return  # Ignore unreadable files

                if line_matches:
                    file_path = p_resolved if self.full_path else file_path
                    matches.update({click.style(file_path, fg='cyan'): line_matches})

            # Use multi-threading for faster processing
            with ThreadPoolExecutor() as executor:
                executor.map(
                    process_file,
                    (file for file in base_path.rglob('*')
                     if not self.conditions(Path(file).resolve(), 'content'))
                )

        self.result = matches
        return self

    def echo(self, title: str, result_name: str) -> int:
        """Display search results"""
        count_result = 0

        if self.result:
            click.echo(click.style(f'\n{title}:\n', fg='yellow'))

            if isinstance(self.result, dict):
                # Display for content results
                for key, value in self.result.items():
                    click.echo(key)
                    click.echo('\n'.join(value) + '\n')
                    count_result += len(value)
            else:
                # Display for directory and file results
                count_result = len(self.result)
                click.echo('\n'.join(self.result))

            if count_result >= 3:
                click.echo(click.style(f'\n{count_result} results found for {result_name}', fg='blue'))

        return count_result
