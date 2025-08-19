# -*- coding: utf-8 -*-
"""Parse human-readable byte sizes"""
import re

import click


class BytesType(click.ParamType):
    """
    Parse human-readable byte sizes (e.g., "10MB", "2GiB") into integers (bytes).
    Supported Units:
    - SI Units (base 1000): kB, MB, GB, etc.
    - Binary Units (base 1024): KiB, MiB, GiB, etc.
    Examples:
    - Valid: "10MB" → 10,000,000 bytes, "2GiB" → 2,147,483,648 bytes
    - Invalid: "10", "abc123", "123MB/s"
    """

    name = "bytes"
    human_pattern = r'((-?\d+(?:\.\d+)?)(\s*[kmgtpezy]?i?b?))'

    def __init__(self, flags: re.RegexFlag = re.IGNORECASE | re.MULTILINE):
        self.flags: re.RegexFlag = flags
        self.pattern: re.Pattern = re.compile(
            self.human_pattern,
            flags=self.flags
        )

    def convert(self, value, param: click.Parameter | None, ctx: click.Context | None):
        if isinstance(value, int):
            return value
        match = self.pattern.search(value)
        if match:
            size_str = match.group(1)
            # Strip off any non-numeric characters at the start of the string
            unit_str = size_str.lstrip('-0123456789.').strip().lower()
            num_str = re.sub(r'[^0-9|\-|\.]', '', size_str)
            if unit_str.endswith('b'):
                unit_str = unit_str[:-1]
            # Define the multiplier for each unit
            units = {
                'k': 1000, 'm': 1000**2, 'g': 1000**3, 't': 1000**4,
                'p': 1000**5, 'e': 1000**6, 'z': 1000**7, 'y': 1000**8,
                'ki': 1024, 'mi': 1024**2, 'gi': 1024**3, 'ti': 1024**4,
                'pi': 1024**5, 'ei': 1024**6, 'zi': 1024**7, 'yi': 1024**8,
            }
            # Convert the string to a float and multiply by the corresponding unit
            return int(float(num_str) * units.get(unit_str, 1.0))
        self.fail(
            f"{value!r} is not a valid size pattern",
            param,
            ctx
        )

    @staticmethod
    def to_human(num: int, binary=False, suffix="B"):
        """Convert bytes to a human-readable string (e.g., 1.5GiB, 10MB)."""
        unit_strs = ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi")
        base = 1024.0
        if not binary:
            unit_strs = ("", "K", "M", "G", "T", "P", "E", "Z")
            base = 1000
        for unit in unit_strs:
            if abs(num) < base:
                return f"{num:3.2f}{unit}{suffix}"
            num /= base
        return f"{num:.2f}Y{'i' if binary else ''}{suffix}"


bytes_to_human = BytesType.to_human


class BytesTypeRange(click.IntRange):
    """
    A range validator for human-readable byte sizes.
    Combines `BytesType` (for parsing sizes) and `click.IntRange` 
    (for range validation).
    Examples:
    - Valid: "10MB" (within range), "1GiB" (within range)
    - Invalid: "XYZ" (invalid format), "100GB" (out of range)
    """
    name = "bytes range"

    def __init__(self, *args, flags: re.RegexFlag = re.IGNORECASE | re.MULTILINE,  **kwargs):
        super().__init__(*args, **kwargs)
        self.bytes = BytesType(flags=flags)

    def convert(self, value, param: click.Parameter | None, ctx: click.Context | None):
        return super().convert(
            value=self.bytes.convert(
                value=value,
                param=param,
                ctx=ctx
            ),
            param=param,
            ctx=ctx
        )


class NullableBytesType(BytesType):
    """
    Extend `BytesType` to allow null-like values (e.g., "none", "null").
    Examples:
    - Valid: "10MB", "none", "null"
    - Invalid: "XYZ" (invalid format)
    """

    def convert(self, value, param: click.Parameter | None, ctx: click.Context | None):
        if value is None or str(value).lower() in {'null', 'none', 'off'}:
            return None
        return super().convert(value=value, param=param, ctx=ctx)
