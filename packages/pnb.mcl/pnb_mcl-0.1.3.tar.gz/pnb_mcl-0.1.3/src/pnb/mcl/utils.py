from __future__ import annotations

import re
import typing as T


def _fullmatch(pattern):
    return f'^{pattern}$'

LEADING_CHAR = '[A-Za-z]' # TODO: fix in schema, tests
FOLLOWING_CHAR = '[A-Za-z_0-9]'
SYMBOL = f'{LEADING_CHAR}{FOLLOWING_CHAR}*'
SYMBOL_REFERENCE = fr'{SYMBOL}(\.{SYMBOL})?'
MULTIPLE_SYMBOL_REFERENCES = f'({SYMBOL_REFERENCE}( {SYMBOL_REFERENCE})*)?'
IDENTIFIER_PATTERN = re.compile(_fullmatch(SYMBOL))
SYMBOL_PATTERN = re.compile(SYMBOL) # TODO: remove alias
SYMBOL_REFERENCE_PATTERN = re.compile(SYMBOL_REFERENCE)
MULTIPLE_SYMBOL_REFERENCES_PATTERN = re.compile(MULTIPLE_SYMBOL_REFERENCES)


def check_is_uri(text: str, name: T.Optional[str]=None):
    pass # TODO


def check_is_symbol(text: str, name: T.Optional[str]=None):
    if not SYMBOL_PATTERN.fullmatch(text):
        if name:
            intro = f'{name}: '
        else:
            intro = ''
        raise ValueError(
            f'{intro}{text!r} '
                f'does not match the pattern {SYMBOL}')

def check_is_symbol_reference(text: str, name: T.Optional[str]=None):
    if not SYMBOL_REFERENCE_PATTERN.fullmatch(text):
        if name:
            intro = f'{name}: '
        else:
            intro = ''
        raise ValueError(
            f'{intro}{text!r} '
                f'does not match the pattern {SYMBOL_REFERENCE}')

def check_is_multiple_symbol_references(text: str, name: T.Optional[str]=None):
    if not MULTIPLE_SYMBOL_REFERENCES_PATTERN.fullmatch(text):
        if name:
            intro = f'{name}: '
        else:
            intro = ''
        raise ValueError(
            f'{intro}{text!r} '
                f'does not match the pattern {MULTIPLE_SYMBOL_REFERENCES}')
