from pathlib import Path

import click


def search_in_names(base_path: str, query: str, is_file: bool = True) -> list[str]:
    """Search for file names"""
    base_path = Path(base_path)
    matches = []

    for p in base_path.rglob('*'):
        if query in p.name and (p.is_file() if is_file else p.is_dir()):
            p = str(p).replace(query, click.style(query, fg='green'))  # Specify the found part
            matches.append(p)

    return matches


def display_results(results: list[str], title: str, result_name: str):
    if results:
        click.echo(click.style(f'\n{title}:\n', fg='yellow'))
        for result in results:
            click.echo(result)
        click.echo(click.style(f'\n{len(results)} result(s) found for {result_name}', fg='blue'))
