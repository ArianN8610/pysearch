import re
import click

from .utils import display_results
from .searcher import search_in_names, search_in_file_contents


@click.command()
@click.argument('query')
@click.option(
    '-p', '--path',
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    default='.', show_default=True,
    help='Base directory to search in.'
)
@click.option('-f', '--files', is_flag=True, help='Search only in file names.')
@click.option('-d', '--directories', is_flag=True, help='Search only in directory names.')
@click.option('-c', '--content', is_flag=True, help='Search inside file contents.')
@click.option('-C', '--case-sensitive', is_flag=True, help='Make the search case-sensitive.')
@click.option('--ext', multiple=True, type=click.STRING,
    help='Filter results by file extension. Example: --ext py --ext js')
@click.option('-r', '--regex', is_flag=True, help='Use a regular expression for searching.')
@click.option('-i', '--include', type=click.Path(exists=True, file_okay=False, dir_okay=True),
              multiple=True, help='Folders that contain search results.')
@click.option('-e', '--exclude', type=click.Path(exists=True, file_okay=False, dir_okay=True),
              multiple=True, help='Folders not included in search results.')
def search(query: str, path: str, files: bool, directories: bool, content: bool, case_sensitive: bool, ext: tuple[str],
           regex: bool, include: tuple[str], exclude: tuple[str]):
    """Get query, search and display results"""

    # Check regex value to avoid errors
    if regex:
        try:
            re.compile(query)
        except re.error:
            click.echo(click.style('Invalid regex pattern: ', fg='red') + query)
            return

    if True not in (files, directories, content):
        files = directories = content = True  # If no option is selected, search all

    # Search in file names and directory names and files content separately
    if files:
        filename_results = search_in_names(path, query, case_sensitive, regex, include, exclude, ext)
        display_results(filename_results, 'Files', 'file')
    else:
        filename_results = []

    if directories and not ext:
        dir_results = search_in_names(path, query, case_sensitive, regex, include, exclude, is_file=False)
        display_results(dir_results, 'Directories', 'directory')
    else:
        dir_results = []

    if content:
        content_results = search_in_file_contents(path, query, case_sensitive, ext, regex, include, exclude)
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
