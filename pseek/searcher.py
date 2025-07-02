import mmap
import click
from pathlib import Path
from .utils import compile_regex
from .parser import parse_query_expression, TermNode, highlight_text_safe
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
    def __init__(self, base_path, query, case_sensitive, ext, exclude_ext, regex, include, exclude, re_include,
                 re_exclude, whole_word, expr, max_size, min_size, full_path, no_content):
        """Initialize search parameters"""
        self.base_path = Path(base_path)
        self.query = query
        self.case_sensitive = case_sensitive
        self.ext = set(ext)
        self.exclude_ext = set(exclude_ext)
        self.regex = regex
        self.include = {Path(p).resolve() for p in include}
        self.exclude = {Path(p).resolve() for p in exclude}
        self.re_include = re_include
        self.re_exclude = re_exclude
        self.whole_word = whole_word
        self.expr = expr
        self.max_size = max_size
        self.min_size = min_size
        self.full_path = full_path
        self.no_content = no_content
        self.result = None

    def should_skip(self, p_resolved: Path, search_type: str) -> bool:
        """
        Check whether the file/directory should be skipped based on various filters.
        Returns True if the path should be skipped.
        """
        try:
            p_size_mb = p_resolved.stat().st_size / 1_048_576  # Convert size to MB
        except OSError:
            # If path is inaccessible, skip it.
            return True

        file_ext = p_resolved.suffix[1:].lower()

        if (self.include and not any(p_resolved.is_relative_to(inc) for inc in self.include)) \
                or (self.exclude and any(p_resolved.is_relative_to(exc) for exc in self.exclude)) \
                or (self.ext and file_ext not in self.ext) \
                or (self.exclude_ext and file_ext in self.exclude_ext) \
                or (search_type == 'content' and file_ext in EXCLUDED_EXTENSIONS) \
                or (self.max_size and p_size_mb > self.max_size) \
                or (self.min_size and p_size_mb < self.min_size) \
                or ((search_type in ('file', 'content')) and not p_resolved.is_file()) \
                or (search_type == 'directory' and not p_resolved.is_dir()):
            return True

        # Filter by regex include and exclude
        if compiled_inc:=compile_regex(self.re_include):
            return not compiled_inc.search(str(p_resolved))
        if compiled_exc:=compile_regex(self.re_exclude):
            return compiled_exc.search(str(p_resolved)) is not None

        return False

    def search(self, search_type: str):
        """Main search function. search_type can be 'file', 'directory' or 'content'"""
        pattern = parse_query_expression(self.query, self.expr, self.regex, self.whole_word, self.case_sensitive)

        if search_type in ('file', 'directory'):
            matches = []
            for p in self.base_path.rglob('*'):
                try:
                    p_resolved = p.resolve()
                except Exception:
                    continue
                # Skip if conditions fail or if name doesn't match the query
                if self.should_skip(p_resolved, search_type) or not pattern.evaluate(p.name):
                    continue

                # Highlight matched query in the name
                highlighted_name = highlight_text_safe(pattern, p.name)
                # Choose parent path based on full_path flag
                p_parent = p_resolved.parent if self.full_path else p.parent
                matches.append(f'{p_parent}\\{highlighted_name}')
        else:  # content search
            # Use dictionary: key: file path (colored), value: list of line matches
            matches = {} if not self.no_content else set()

            # If expression is simple and is a single TermNode, we can use binary pattern
            binary_pattern = None
            if isinstance(pattern, TermNode):
                try:
                    binary_pattern = pattern.get_binary_pattern()
                except Exception:
                    binary_pattern = None

            def process_file(file_path: Path):
                """Process a single file for content search"""
                try:
                    # Avoid empty files for mmap
                    if file_path.stat().st_size == 0:
                        return

                    # Open the file in binary read mode
                    with open(file_path, 'rb') as f:
                        # Memory-map the file for efficient access
                        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                            if binary_pattern is not None:
                                if not binary_pattern.search(mm):
                                    return
                            else:
                                # fallback: decode whole file for complex expressions
                                try:
                                    content = mm.read().decode('utf-8')
                                except UnicodeDecodeError:
                                    return

                                if not pattern.evaluate(content) and not self.expr:
                                    return

                            # Choose the file path format based on the full_path setting
                            file_label = str(file_path.resolve()) if self.full_path else str(file_path)

                            # Avoid searching through the entire file content if the fast-content flag is True
                            if self.no_content and not self.expr:
                                matches.add(click.style(file_label, fg='cyan'))
                                return

                            lines = []
                            mm.seek(0)  # Move the cursor to the beginning of the file

                            # Iterate over each line in the file
                            for num, line in enumerate(iter(mm.readline, b''), 1):
                                try:
                                    # Decode the binary line as UTF-8 and strip whitespace
                                    line_decoded = line.decode('utf-8').strip()
                                except UnicodeDecodeError:
                                    # Skip lines that can't be decoded
                                    continue

                                # If the pattern matches in the decoded line
                                if pattern.evaluate(line_decoded):
                                    if self.no_content and self.expr:
                                        matches.add(click.style(file_label, fg='cyan'))
                                        return
                                    count = pattern.count_matches(line_decoded) if isinstance(pattern, TermNode) else 0
                                    # Highlight the matching parts in green
                                    highlighted = highlight_text_safe(pattern, line_decoded)
                                    # Show a note if the pattern repeats 3 or more times
                                    count_query = f' - Repeated {count} times' if count >= 3 else ''
                                    # Format the output line with line number and highlighted matches
                                    lines.append(
                                        click.style(f'Line {num}{count_query}: ', fg='magenta') + highlighted
                                    )

                            # If any matching lines were found
                            if lines:
                                # Add the file and its matching lines to the results
                                matches[click.style(file_label, fg='cyan')] = lines
                except Exception:
                    return

            # Filter files before processing
            files_to_process = {
                p for p in self.base_path.rglob('*') if not self.should_skip(p.resolve(), 'content')
            }

            with ThreadPoolExecutor(max_workers=8) as executor:
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
