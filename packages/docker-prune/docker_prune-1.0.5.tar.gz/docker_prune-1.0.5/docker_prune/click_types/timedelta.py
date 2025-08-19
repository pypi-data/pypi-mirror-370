# -*- coding: utf-8 -*-
"""Parse human-readable time durations"""
import re
from datetime import (
    timedelta
)
import click


class TimeDeltaType(click.ParamType):
    """
    Parse human-readable time durations (e.g., "2w 3d 4h") into timedelta objects.
    Supported Units:
    - Weeks (w), Days (d), Hours (h), Minutes (m), Seconds (s)
    Examples:
    - Valid: "2w 3d", "1h30m"
    - Invalid: "abc123", "3x"
    """
    name = "timedelta"
    envvar_list_splitter = '|'

    timedelta_regex = (r'((?P<weeks>-?\d+)\s*w(eek(s)?)?[^\d]*)?'
                       r'((?P<days>-?\d+)\s*d(ay(s)?)?[^\d]*)?'
                       r'((?P<hours>-?\d+)\s*h(our(s)?)?[^\d]*)?'
                       r'((?P<minutes>-?\d+)\s*m(in(ute(s)?)?)?[^\d]*)?'
                       r'((?P<seconds>-?\d+)\s*(s(ec(ond(s)?)?)?)?)?\s*$')

    def __init__(self,
                 negative: bool = False,
                 flags: re.RegexFlag = re.IGNORECASE):
        self.negative = negative
        self.flags = flags
        self.timedelta_pattern = re.compile(
            self.timedelta_regex,
            flags=flags
        )

    def to_info_dict(self):
        info_dict = super().to_info_dict()
        info_dict["negative"] = self.negative
        info_dict["flags"] = self.flags
        return info_dict

    def convert(self, value, param: click.Parameter | None, ctx: click.Context | None):
        if isinstance(value, timedelta):
            return value
        match = self.timedelta_pattern.match(value)
        if match:
            parts = {k: int(v) for k, v in match.groupdict().items() if v}
            if len(parts) == 0:
                self.fail(
                    f"{value!r} is not a valid timedelta pattern", param, ctx)
            if self.negative is False and any(v < 0 for v in parts.values()):
                self.fail(
                    f"{value!r} is not a valid timedelta pattern negative values not allowed",
                    param,
                    ctx
                )
            return timedelta(**parts)
        self.fail(
            f"{value!r} is not a valid timedelta pattern", param, ctx)


class NullableTimeDeltaType(TimeDeltaType):
    """
    Extend `TimeDeltaType` to allow null-like values (e.g., "none", "null").
    Examples:
    - Valid: "2w 3d", "none", "null"
    - Invalid: "abc123", "3x"
    """

    def convert(self, value, param: click.Parameter | None, ctx: click.Context | None):
        if value is None or str(value).lower() in {'null', 'none', 'off'}:
            return None
        return super().convert(value=value, param=param, ctx=ctx)
