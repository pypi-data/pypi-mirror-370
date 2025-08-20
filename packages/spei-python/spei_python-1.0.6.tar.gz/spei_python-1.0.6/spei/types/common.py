# spei/types.py (or wherever you keep your custom types)
import re
from typing import Union

from pydantic import BeforeValidator
from typing_extensions import Annotated


def validate_institution_code(value: Union[str, int]) -> int:
    """Validates and converts an institution code to a 3 or 5-digit integer."""
    value_str = str(value)
    if not re.match(r'^\d{3,5}$', value_str):
        raise ValueError('must be exactly 3 or 5 digits')

    return int(value_str)


InstitutionCode = Annotated[int, BeforeValidator(validate_institution_code)]
