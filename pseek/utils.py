import re
import click


def highlight_matches(line, query, case_sensitive, regex, whole_word, context=20):
    """Highlight matches and truncate long lines with proper handling"""

    flags = 0 if case_sensitive else re.IGNORECASE

    if not regex and not whole_word:
        query = re.escape(query)  # If regex is disabled, use escape to search for regular text

    # Find all matches
    matches = list(re.finditer(query, line, flags))

    if not matches:
        return None  # If there is no match, return None

    start_positions = [max(0, m.start() - context) for m in matches]  # 20 characters before
    end_positions = [min(len(line), m.end() + context) for m in matches]  # 20 characters after

    # Combine sections close together to avoid repetition
    merged_snippets = []
    current_start, current_end = start_positions[0], end_positions[0]

    for i in range(1, len(matches)):
        if start_positions[i] <= current_end:  # If the next section is close, combine them
            current_end = max(current_end, end_positions[i])
        else:
            merged_snippets.append((current_start, current_end))
            current_start, current_end = start_positions[i], end_positions[i]

    merged_snippets.append((current_start, current_end))  # Add the last section

    result = []
    for start, end in merged_snippets:
        snippet = line[start:end]
        snippet = re.sub(query, lambda m: click.style(m.group(), fg='green'), snippet, flags=flags)
        result.append(snippet)

    final_output = ' ... '.join(result)  # If there are multiple results, put `...` between them

    # Add `...` at the beginning and end if needed
    if merged_snippets[0][0] > 0:
        final_output = '...' + final_output
    if merged_snippets[-1][1] < len(line):
        final_output += '...'

    return final_output, len(matches)  # Count the number of repetitions


def display_results(results, title, result_name):
    """Display search results"""
    if results:
        click.echo(click.style(f'\n{title}:\n', fg='yellow'))
        for result in results:
            click.echo(result)
        click.echo(click.style(f'\n{len(results)} result(s) found for {result_name}', fg='blue'))
