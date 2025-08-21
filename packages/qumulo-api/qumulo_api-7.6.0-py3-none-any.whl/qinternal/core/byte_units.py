# Copyright (c) 2017 Qumulo, Inc. All rights reserved.
#
# NOTICE: All information and intellectual property contained herein is the
# confidential property of Qumulo, Inc. Reproduction or dissemination of the
# information or intellectual property contained herein is strictly forbidden,
# unless separate prior written permission has been obtained from Qumulo, Inc.

from typing import Callable, Tuple

THOUSAND = 1000**1
MILLION = 1000**2
BILLION = 1000**3
TRILLION = 1000**4
QUADRILLION = 1000**5
QUINTILLION = 1000**6

KIBIBYTE = 1024**1
MEBIBYTE = 1024**2
GIBIBYTE = 1024**3
TEBIBYTE = 1024**4
PEBIBYTE = 1024**5
EXBIBYTE = 1024**6

DECIMAL_kB = THOUSAND
DECIMAL_MB = MILLION
DECIMAL_GB = BILLION
DECIMAL_TB = TRILLION
DECIMAL_PB = QUADRILLION
DECIMAL_EB = QUINTILLION

BINARY_KiB = KIBIBYTE
BINARY_MiB = MEBIBYTE
BINARY_GiB = GIBIBYTE
BINARY_TiB = TEBIBYTE
BINARY_PiB = PEBIBYTE
BINARY_EiB = EXBIBYTE

BLOCK_SIZE = 4 * KIBIBYTE


def bytes_to_blocks(num_bytes: int) -> int:
    """
    Convert bytes to blocks, taking the ceiling of the conversion.
    """
    res = num_bytes // BLOCK_SIZE
    return res + 1 if num_bytes % BLOCK_SIZE != 0 else res


def blocks_to_bytes(num_bytes: int) -> int:
    return num_bytes * BLOCK_SIZE


def _humanize_bytes(byte_size: int, base: int, rounder: Callable[[float], int]) -> Tuple[str, str]:
    units = ['B', 'K', 'M', 'G', 'T', 'P']
    for i, unit in enumerate(units):
        val = rounder(byte_size / base**i)
        if val < base:
            return str(val), unit
    return str(byte_size), 'B'


def humanize_binary(byte_size: int, rounder: Callable[[float], int] = round) -> Tuple[str, str]:
    """
    Format number of bytes to a tuple of integer value and binary unit (B, KiB,
    MiB, GiB, TiB, or PiB) as strings.
    """
    val, unit = _humanize_bytes(byte_size, base=1024, rounder=rounder)
    if unit != 'B':
        unit += 'iB'
    return val, unit


def humanize_decimal(byte_size: int, rounder: Callable[[float], int] = round) -> Tuple[str, str]:
    """
    Format number of bytes to a tuple of integer value and decimal unit (B, KB,
    MB, GB, TB, or PB) as strings.
    """
    val, unit = _humanize_bytes(byte_size, base=1000, rounder=rounder)
    if unit != 'B':
        unit += 'B'
    return val, unit


def parse_humanized(humanized: str) -> int:
    """
    Convert a humanized representation of a number of bytes into its integer value.
    """
    suffixes = {
        'kB': DECIMAL_kB,
        'KB': DECIMAL_kB,
        'KiB': KIBIBYTE,
        'MB': DECIMAL_MB,
        'MiB': MEBIBYTE,
        'GB': DECIMAL_GB,
        'GiB': GIBIBYTE,
        'TB': DECIMAL_TB,
        'TiB': TEBIBYTE,
        'PB': DECIMAL_PB,
        'PiB': PEBIBYTE,
    }

    try:
        return int(humanized)
    except ValueError:
        pass

    try:
        suffix, unit = next(s for s in suffixes.items() if humanized.endswith(s[0]))
    except StopIteration:
        raise ValueError(f'Unrecognized suffix for {humanized}')

    number = humanized[: -len(suffix)]
    try:
        return unit * int(number)
    except ValueError:
        return int(unit * float(number))
