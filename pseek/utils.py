import re
import sys
import click


def compile_regex(txt, flags=0):
    if txt is not None:
        try:
            return re.compile(txt, flags)
        except re.error as e:
            click.echo(click.style(f"Regex compile error: {e}", fg='red'))
            sys.exit(1)
