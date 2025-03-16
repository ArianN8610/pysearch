import click

from .utils import display_results
from .searcher import search_in_names, search_in_file_contents


@click.command()
@click.argument('query')
@click.option(
    '-p', '--path',
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    default='.', help='Path to search results'
)
@click.option('-f', '--files', is_flag=True, help='Search only in file names')
@click.option('-d', '--directories', is_flag=True, help='Search only in directory names')
@click.option('-c', '--content', is_flag=True, help='Search only in file contents')
@click.option('-cs', '--case-sensitive', is_flag=True, help='Case sensitive in searches')
def search(query: str, path: str, files: bool, directories: bool, content: bool, case_sensitive: bool):
    """Get query, search and display results"""

    if True not in (files, directories, content):
        files = directories = content = True  # If no option is selected, search all

    # Search in file names and directory names and files content separately
    if files:
        filename_results = search_in_names(path, query, case_sensitive)
        display_results(filename_results, 'Files', 'file')
    else:
        filename_results = []

    if directories:
        dir_results = search_in_names(path, query, case_sensitive, False)
        display_results(dir_results, 'Directories', 'directory')
    else:
        dir_results = []

    if content:
        content_results = search_in_file_contents(path, query, case_sensitive)
        display_results(content_results, 'Contents', 'content')
    else:
        content_results = []

    # Display total of results
    if results:=(filename_results + dir_results + content_results):
        click.echo(click.style(f'\nTotal results: {len(results)}', fg='cyan'))
    else:
        click.echo(click.style('No results found', fg='red'))


if __name__ == "__main__":
    search()
