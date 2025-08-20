import logging
from typing import Any

from unidecode import unidecode

# Set up basic configuration for logging
logging.basicConfig(level=logging.WARNING)

# From "APÉNDICE B: TABLA DE CARACTERES VÁLIDOS Y CÓDIGOS ASCII RESPECTIVOS"
# in SPEI Manual.
VALID_CHARACTERS = frozenset(
    (
        ' ',
        '!',
        '"',
        '#',
        '$',
        '%',
        '&',
        "'",
        '(',
        ')',
        '*',
        '+',
        ',',
        '-',
        '.',
        '/',
        '0',
        '1',
        '2',
        '3',
        '4',
        '5',
        '6',
        '7',
        '8',
        '9',
        ':',
        ';',
        '?',
        '@',
        'A',
        'B',
        'C',
        'D',
        'E',
        'F',
        'G',
        'H',
        'I',
        'J',
        'K',
        'L',
        'M',
        'N',
        'O',
        'P',
        'Q',
        'R',
        'S',
        'T',
        'U',
        'V',
        'W',
        'X',
        'Y',
        'Z',
        '\\',
        '_',
        'a',
        'b',
        'c',
        'd',
        'e',
        'f',
        'g',
        'h',
        'i',
        'j',
        'k',
        'l',
        'm',
        'n',
        'o',
        'p',
        'q',
        'r',
        's',
        't',
        'u',
        'v',
        'w',
        'x',
        'y',
        'z',
        'é',
        'á',
        'í',
        'ó',
        'ú',
        'ñ',
        'Ñ',
        '¿',
        '¡',
    ),
)


def validate_alphanumeric(text: str) -> str:
    if not all(char in VALID_CHARACTERS for char in text):
        invalid_chars = set(text) - VALID_CHARACTERS
        raise ValueError(f'Invalid characters found: {invalid_chars}')

    return text


def normalize_invalid_chars(text: Any) -> str:
    """Converts a text to a valid string.

    Selectively replacing invalid characters with their ASCII
    equivalents. Valid characters are preserved as-is, only invalid ones
    are converted using unidecode. If the conversion is not possible,
    the character is replaced with a '?' character.
    """
    result = []
    text_str = str(text)

    for char in text_str:
        if char in VALID_CHARACTERS:
            result.append(char)
        else:
            # Convert only this character to ASCII and validate it
            ascii_char = unidecode(char)
            # Take first char in case unidecode returns multiple chars
            first_ascii = ascii_char[0] if ascii_char else ''
            if first_ascii and first_ascii in VALID_CHARACTERS:
                result.append(first_ascii)
            else:
                # Log a warning and replace with '?'
                logging.warning(
                    f'Character "{char}" cannot be converted to a valid character, replacing with "?"',  # noqa: E501
                )
                result.append('?')

    return ''.join(result)
