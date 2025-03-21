import click
from .searcher import Search


@click.command()
@click.argument('query')
@click.option('-p', '--path', type=click.Path(exists=True, file_okay=False, dir_okay=True), default='.',
              show_default=True, help='Base directory to search in.')
@click.option('-f', '--file', is_flag=True, help='Search only in file names.')
@click.option('-d', '--directory', is_flag=True, help='Search only in directory names.')
@click.option('-c', '--content', is_flag=True, help='Search inside file contents.')
@click.option('-C', '--case-sensitive', is_flag=True, help='Make the search case-sensitive.')
@click.option('--ext', multiple=True, type=click.STRING,
              help='Filter results by file extension. Example: --ext py --ext js')
@click.option('--regex', is_flag=True, help='Use regular expression for searching.')
@click.option('-i', '--include', type=click.Path(exists=True, file_okay=True, dir_okay=True),
              multiple=True, help='Directories or files that contain search results.')
@click.option('-e', '--exclude', type=click.Path(exists=True, file_okay=True, dir_okay=True),
              multiple=True, help='Directories or files not included in search results.')
@click.option('--word', is_flag=True, help='Search for results that match the whole word.')
@click.option('--max-size', type=click.FLOAT, help='Maximum size directory or file can have (MB)')
@click.option('--min-size', type=click.FLOAT, help='Minimum size directory or file can have (MB)')
@click.option('--full-path', is_flag=True, help='Display complete paths of files and directories.')
def search(query, path, file, directory, content, case_sensitive, ext, regex, include, exclude, word,
           max_size, min_size, full_path):
    """Search for files, directories, and content based on the query."""

    # Enable all search types if none are explicitly selected
    if not any([file, directory, content]):
        file = directory = content = True

    count_results = 0
    search_class = Search(path, query, case_sensitive, ext, regex, include, exclude, word, max_size, min_size,
                          full_path)

    if file:
        count_results += search_class.search('file').echo('Files', 'file')
    if directory and not ext:
        count_results += search_class.search('directory').echo('Directories', 'directory')
    if content:
        count_results += search_class.search('content').echo('Contents', 'content')

    message = f'\nTotal results: {count_results}' if count_results else 'No results found'
    click.echo(click.style(message, fg='red'))  # Display total of results


if __name__ == "__main__":
    search()
