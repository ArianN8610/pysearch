import click
from .searcher import Search


@click.command()
@click.argument('query')
@click.option('-p', '--path', type=click.Path(exists=True, file_okay=False, dir_okay=True),
              default='.', show_default=True, help='Base directory to search in.')
# Search type options
@click.option('-f', '--file', is_flag=True, help='Search only in file names.')
@click.option('-d', '--directory', is_flag=True, help='Search only in directory names.')
@click.option('-c', '--content', is_flag=True, help='Search inside file contents.')
# Additional options
@click.option('-C', '--case-sensitive', is_flag=True, help='Make the search case-sensitive.')
@click.option('--regex', is_flag=True, help='Use regular expression for searching.')
@click.option('--word', is_flag=True, help='Match whole words only.')
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
# Size filters
@click.option('--max-size', type=click.FLOAT, help='Maximum file/directory size (in MB).')
@click.option('--min-size', type=click.FLOAT, help='Minimum file/directory size (in MB).')
# Output option
@click.option('--full-path', is_flag=True, help='Display full paths for results.')
def search(query, path, file, directory, content, case_sensitive, ext, exclude_ext, regex,
           include, exclude, word, max_size, min_size, full_path):
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
        whole_word=word,
        max_size=max_size,
        min_size=min_size,
        full_path=full_path
    )

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


if __name__ == "__main__":
    search()
