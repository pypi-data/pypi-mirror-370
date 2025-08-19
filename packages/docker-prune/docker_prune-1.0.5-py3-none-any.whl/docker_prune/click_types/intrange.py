# -*- coding: utf-8 -*-
"""Extend `click.IntRange` to allow null-like values"""

import click


class NullableIntRange(click.IntRange):
    """
    Extend `click.IntRange` to allow null-like values (e.g., "none", "null").
    Examples:
    - Valid: 10 (within range), "none", "null"
    - Invalid: "abc123", 100 (out of range)
    """

    def convert(self, value, param: click.Parameter | None, ctx: click.Context | None):
        if value is None or str(value).lower() in {'null', 'none', 'off'}:
            return None
        return super().convert(value=value, param=param, ctx=ctx)
