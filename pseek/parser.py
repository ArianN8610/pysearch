import re
import sys
import click
from lark import Lark, Transformer
from .utils import compile_regex


class ExprNode:
    """Base class for expression tree nodes"""
    def evaluate(self, text: str) -> bool:
        raise NotImplementedError


class TermNode(ExprNode):
    """Node representing a single search term"""
    def __init__(self, term: str, regex, whole_word, case_sensitive):
        self.raw_term = term
        self.whole_word = whole_word
        self.case_sensitive = case_sensitive

        flags = 0 if case_sensitive else re.IGNORECASE  # Adjust case sensitivity

        # Build the regex pattern
        if not regex:
            term = re.escape(term)  # Escape if not regex
            # Apply whole-word matching only if not using regex (or if desired behavior is defined)
            if whole_word:
                term = r'\b' + term + r'\b'

        self.pattern = compile_regex(term, flags)  # Precompile the regex pattern for performance

    def evaluate(self, text: str) -> bool:
        return bool(self.pattern.search(text))

    def count_matches(self, text: str) -> int:
        """Count how many times the pattern appears in the text"""
        return len(list(self.pattern.finditer(text)))

    def get_binary_pattern(self) -> re.Pattern:
        """Return a compiled binary regex pattern"""
        return re.compile(self.pattern.pattern.encode("utf-8"), self.pattern.flags)


class NotNode(ExprNode):
    """Node representing logical NOT"""
    def __init__(self, child: ExprNode):
        self.child = child

    def evaluate(self, text: str) -> bool:
        return not self.child.evaluate(text)


class AndNode(ExprNode):
    """Node representing logical AND"""
    def __init__(self, left: ExprNode, right: ExprNode):
        self.left = left
        self.right = right

    def evaluate(self, text: str) -> bool:
        return self.left.evaluate(text) and self.right.evaluate(text)


class OrNode(ExprNode):
    """Node representing logical OR"""
    def __init__(self, left: ExprNode, right: ExprNode):
        self.left = left
        self.right = right

    def evaluate(self, text: str) -> bool:
        return self.left.evaluate(text) or self.right.evaluate(text)


# Lark grammar for parsing logical expressions
query_grammar = r"""
?start: expr

?expr: or_expr

?or_expr: and_expr
        | or_expr "or" and_expr     -> or_expr

?and_expr: not_expr
         | and_expr "and" not_expr  -> and_expr

?not_expr: "not" not_expr           -> not_expr
         | term

?term: REGEX_STRING                 -> regex_string
     | ESCAPED_STRING               -> string
     | "(" expr ")"

REGEX_STRING: "r" ESCAPED_STRING

%import common.ESCAPED_STRING
%import common.WS
%ignore WS
"""


class TreeToExpr(Transformer):
    """Transform parsed tree into expression tree (ExprNode subclasses)"""
    def __init__(self, whole_word, case_sensitive):
        super().__init__()
        self.whole_word = whole_word
        self.case_sensitive = case_sensitive

    def string(self, s):
        """ Match normal quoted string: "foo" """
        term = s[0][1:-1]  # Remove surrounding quotes (e.g., "foo" -> foo)
        return TermNode(
            term,
            False,
            self.whole_word,
            self.case_sensitive
        )

    def regex_string(self, s):
        """ Match regex pattern like r"foo.*bar" """
        term = s[0][2:-1]  # remove r and quotes
        return TermNode(
            term,
            True,
            False,  # whole_word doesn't make sense for regex
            self.case_sensitive
        )

    def and_expr(self, args):
        return AndNode(args[0], args[1])

    def or_expr(self, args):
        return OrNode(args[0], args[1])

    def not_expr(self, args):
        return NotNode(args[0])


def parse_query_expression(query: str, expr, regex, whole_word, case_sensitive) -> ExprNode:
    """
    Function to parse the query and return expression tree.
    If expr is False, treat the whole query as a single term.
    """

    if not expr:
        return TermNode(query, regex, whole_word, case_sensitive)

    # Otherwise, parse using Lark
    parser = Lark(query_grammar, parser="lalr")
    try:
        tree = parser.parse(query)
        return TreeToExpr(
            whole_word,
            case_sensitive
        ).transform(tree)
    except Exception as e:
        click.echo(click.style("Query parser error:\n\n", fg='red') + str(e))
        sys.exit(1)


def highlight_text_safe(expr: ExprNode, text: str) -> str:
    matches = []

    def collect_matches(node):
        if isinstance(node, TermNode):
            for match in node.pattern.finditer(text):
                matches.append((match.start(), match.end()))
        elif isinstance(node, (AndNode, OrNode)):
            collect_matches(node.left)
            collect_matches(node.right)
        elif isinstance(node, NotNode):
            collect_matches(node.child)

    collect_matches(expr)

    # Remove overlaps (for example, if one match was inside another match)
    matches.sort()  # sort by start position
    merged = []
    for start, end in matches:
        if not merged or start >= merged[-1][1]:  # no overlap
            merged.append((start, end))

    # Create the final text with highlight
    result = []
    last = 0
    for start, end in merged:
        result.append(text[last:start])
        result.append(click.style(text[start:end], fg='green'))
        last = end
    result.append(text[last:])

    return ''.join(result)
