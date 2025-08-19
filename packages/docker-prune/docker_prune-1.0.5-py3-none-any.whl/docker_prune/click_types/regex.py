# -*- coding: utf-8 -*-
"""Compile strings into regex patterns."""
import re
try:
    from re import PatternError
except ImportError:
    from re import error as PatternError
import click


class RegexType(click.ParamType):
    """
    Compile strings into regex patterns.
    Examples:
    - Valid: "^app.*$", ".*test$"
    - Invalid: "[", 12345
    """
    name = "regex"
    envvar_list_splitter = '|||'

    def __init__(self,
                 flags: re.RegexFlag = re.IGNORECASE):
        self.flags = flags

    def convert(self, value, param: click.Parameter | None, ctx: click.Context | None):
        if isinstance(value, re.Pattern):
            return value
        try:
            return re.compile(value, flags=self.flags)
        except (PatternError, TypeError, ValueError) as e:
            self.fail(
                f"{value!r} is not a valid regex pattern {e}",
                param,
                ctx
            )


class NullableRegexType(RegexType):
    """
    Extend `RegexType` to allow null-like values (e.g., "none", "null").
    Examples:
    - Valid: "^app.*$", "none", "null"
    - Invalid: "[", 12345
    """

    def convert(self, value, param: click.Parameter | None, ctx: click.Context | None):
        if value is None or str(value).lower() in {'null', 'none', 'off'}:
            return None
        return super().convert(value=value, param=param, ctx=ctx)
