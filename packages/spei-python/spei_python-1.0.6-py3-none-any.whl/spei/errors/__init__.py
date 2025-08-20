from spei.errors.spei import ERROR_CODES, CodigoError  # noqa: F401

__all__ = ['CodigoError'] + [enum.__name__ for enum in ERROR_CODES]  # noqa: WPS410
