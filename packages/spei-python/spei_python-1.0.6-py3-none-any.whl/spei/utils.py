import re

_SNAKE_CASE_PATTERN = re.compile('(.)([A-Z0-9])')


def to_pascal_case(string: str) -> str:
    temp = string.split('_')
    new_string = [ele.title() for ele in temp]

    return ''.join(new_string)


def to_camel_case(string: str) -> str:
    return to_pascal_case(string)[0].lower() + to_pascal_case(string)[1:]  # noqa: E501, WPS221


def to_snake_case(string: str) -> str:
    return _SNAKE_CASE_PATTERN.sub(r'\1_\2', str(string)).lower()
