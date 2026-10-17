"""Safe arithmetic evaluator for the calculator.

Supports + - * / ** and unary +/-. Uses Decimal so 0.1 + 0.2 gives 0.3.
Raises ValueError for malformed input and ArithmeticError (e.g. division
by zero, overflow) for invalid maths.
"""

import re
from decimal import Context, Decimal

_TOKEN = re.compile(
    r"(?P<num>(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)|(?P<op>\*\*|[+\-*/])"
)
_DISPLAY_CONTEXT = Context(prec=12)
_INTEGER_LIMIT = Decimal(10) ** 15
_PLAIN_MIN = Decimal(10) ** -9


def _tokenize(text):
    tokens = []
    pos = 0
    text = text.strip()
    while pos < len(text):
        match = _TOKEN.match(text, pos)
        if match is None:
            raise ValueError(f"Unexpected character at position {pos}")
        if match.group("num") is not None:
            tokens.append(("num", Decimal(match.group("num"))))
        else:
            tokens.append(("op", match.group("op")))
        pos = match.end()
    return tokens


class _Parser:
    """Recursive-descent parser: expr -> term -> unary -> power -> number."""

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def _peek_op(self):
        if self.pos < len(self.tokens) and self.tokens[self.pos][0] == "op":
            return self.tokens[self.pos][1]
        return None

    def parse(self):
        value = self._expr()
        if self.pos != len(self.tokens):
            raise ValueError("Unexpected trailing input")
        return value

    def _expr(self):
        value = self._term()
        while self._peek_op() in ("+", "-"):
            op = self._peek_op()
            self.pos += 1
            rhs = self._term()
            value = value + rhs if op == "+" else value - rhs
        return value

    def _term(self):
        value = self._unary()
        while self._peek_op() in ("*", "/"):
            op = self._peek_op()
            self.pos += 1
            rhs = self._unary()
            value = value * rhs if op == "*" else value / rhs
        return value

    def _unary(self):
        op = self._peek_op()
        if op in ("+", "-"):
            self.pos += 1
            value = self._unary()
            return -value if op == "-" else value
        return self._power()

    def _power(self):
        base = self._number()
        if self._peek_op() == "**":
            self.pos += 1
            result = base ** self._unary()
            if not result.is_finite():  # e.g. 0**-1 gives Infinity, not an error
                raise ArithmeticError("Result is not a finite number")
            return result
        return base

    def _number(self):
        if self.pos >= len(self.tokens) or self.tokens[self.pos][0] != "num":
            raise ValueError("Expected a number")
        value = self.tokens[self.pos][1]
        self.pos += 1
        return value


def evaluate(expression):
    """Evaluate an expression string and return a Decimal."""
    return _Parser(_tokenize(expression)).parse()


def format_result(value):
    """Format a Decimal for the display (12 significant digits at most)."""
    if value == 0:
        return "0"
    if value == value.to_integral_value() and abs(value) < _INTEGER_LIMIT:
        return str(int(value))
    rounded = _DISPLAY_CONTEXT.plus(value).normalize()
    if abs(rounded) >= _INTEGER_LIMIT or abs(rounded) < _PLAIN_MIN:
        return format(rounded, "e")
    return format(rounded, "f")
