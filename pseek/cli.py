import click
from .searcher import Search
from multiprocessing import Process


def run_search_process(file, directory, content, ext, exclude_ext, search_instance):
    """Performs the basic search operation"""
    total_results = 0

    # Search for files if requested.
    if file:
        total_results += search_instance.search('file').echo('Files', 'file')
    # Search for directories if requested and extension filters are not active.
    if directory and not (ext or exclude_ext):
        total_results += search_instance.search('directory').echo('Directories', 'directory')
    # Search for content inside files if requested.
    if content:
        total_results += search_instance.search('content').echo('Contents', 'content')

    # Display final summary message.
    message = f'\nTotal results: {total_results}' if total_results else 'No results found'
    click.echo(click.style(message, fg='red'))



@click.command()
@click.argument('query')
@click.option('-p', '--path', type=click.Path(exists=True, file_okay=False, dir_okay=True),
              default='.', show_default=True, help='Base directory to search in.')
# Search type options
@click.option('-f', '--file', is_flag=True, help='Search only in file names.')
@click.option('-d', '--directory', is_flag=True, help='Search only in directory names.')
@click.option('-c', '--content', is_flag=True, help='Search inside file contents.')
# Additional options
@click.option('-C', '--case-sensitive', is_flag=True,
              help='Make the search case-sensitive '
                   '(except when --expr is enabled, '
                   'in which case you can make it case sensitive by putting c before term: c"foo")')
@click.option('-r', '--regex', is_flag=True,
              help='Use regular expressions to search '
                   '(except when --expr is enabled, '
                   'in which case you can make it regex by putting r before term: r"foo")')
@click.option('-w', '--word', is_flag=True,
              help='Match whole words only '
                   '(except when --expr is enabled, '
                   'in which case you can make it match whole word by putting w before term: w"foo")')
@click.option('--expr', is_flag=True,
              help='Enable to write conditions in the query. Example: r"foo.*bar" and ("bar" or "baz") and not "qux" '
                   '(To use regex, word, and case-sensitive features, '
                   'you can use the prefixes r, w, and c before terms. Allowed modes: r, w, c, wc, cw, rc, cr. '
                   'Examples: r"foo.*bar", wc"Foo", cr".*Foo", ...)')
@click.option('--timeout', type=click.INT,
              help='To stop the search after a specified period of time (Seconds)')
# Extension filters
@click.option('--ext', multiple=True, type=click.STRING,
              help='Include files with these extensions. Example: --ext py --ext js')
@click.option('-E', '--exclude-ext', multiple=True, type=click.STRING,
              help='Exclude files with these extensions. Example: --exclude-ext jpg --exclude-ext exe')
# Include/Exclude specific paths (files or directories)
@click.option('-i', '--include', type=click.Path(exists=True, file_okay=True, dir_okay=True),
              multiple=True, help='Directories or files to include in search.')
@click.option('-e', '--exclude', type=click.Path(exists=True, file_okay=True, dir_okay=True),
              multiple=True, help='Directories or files to exclude from search.')
@click.option('--re-include', type=click.STRING,
              help='Directories or files to include in search with regex.')
@click.option('--re-exclude', type=click.STRING,
              help='Directories or files to exclude from search with regex.')
# Size filters
@click.option('--max-size', type=click.FLOAT, help='Maximum file/directory size (in MB).')
@click.option('--min-size', type=click.FLOAT, help='Minimum file/directory size (in MB).')
# Output option
@click.option('--full-path', is_flag=True, help='Display full paths for results.')
@click.option('--no-content', is_flag=True, help='Only display files path for content search.')
def search(query, path, file, directory, content, case_sensitive, ext, exclude_ext, regex, include, exclude,
           re_include, re_exclude, word, expr, timeout, max_size, min_size, full_path, no_content):
    """Search for files, directories, and file content based on the query."""
    # If no search type is specified, search in all types.
    if not any((file, directory, content)):
        file = directory = content = True

    # Initialize the Search class with provided options.
    search_instance = Search(
        base_path=path,
        query=query,
        case_sensitive=case_sensitive,
        ext=ext,
        exclude_ext=exclude_ext,
        regex=regex,
        include=include,
        exclude=exclude,
        re_include=re_include,
        re_exclude=re_exclude,
        whole_word=word,
        expr=expr,
        max_size=max_size,
        min_size=min_size,
        full_path=full_path,
        no_content=no_content
    )

    # Stop search if it exceeds timeout with multiprocessing
    if timeout:
        p = Process(
            target=run_search_process,
            args=(file, directory, content, ext, exclude_ext, search_instance)
        )
        p.start()
        p.join(timeout)

        if p.is_alive():
            p.terminate()
            p.join()
            click.echo(click.style(f"\nTimeout! Search exceeded {timeout} seconds and was stopped.", fg="red"))
    else:
        run_search_process(file, directory, content, ext, exclude_ext, search_instance)


if __name__ == "__main__":
    search()
