import click

from .utils import search_in_names, display_results


@click.command()
@click.argument('query')
@click.option(
    '-p', '--path',
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    default='.', help='Path to search results'
)
@click.option('-f', '--files', is_flag=True, help='Search only in file names')
@click.option('-d', '--directories', is_flag=True, help='Search only in directory names')
def search(query: str, path: str, files: bool, directories: bool):
    """Get query, search and display results"""

    if True not in (files, directories):
        files = directories = True  # If no option is selected, search all

    # Search in file names and directory names separately
    if files:
        filename_results = search_in_names(path, query)
        display_results(filename_results, 'Files', 'file')
    else:
        filename_results = []

    if directories:
        dir_results = search_in_names(path, query, False)
        display_results(dir_results, 'Directories', 'directory')
    else:
        dir_results = []

    # Display total of results
    if results:=(filename_results + dir_results):
        click.echo(click.style(f'\nTotal results: {len(results)}', fg='cyan'))
    else:
        click.echo(click.style('No results found', fg='red'))


if __name__ == "__main__":
    search()
