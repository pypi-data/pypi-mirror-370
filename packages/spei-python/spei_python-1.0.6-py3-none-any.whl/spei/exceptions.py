from spei.resources import Respuesta


class SPEIError(Exception):
    def __init__(self, respuesta: Respuesta):
        self.error_code = respuesta.err_codigo
        self.error_description = respuesta.err_descripcion


class TipoPagoInvalidoError(SPEIError):
    """Tipo pago es invalido."""


class FechaOperacionIncorrectaError(SPEIError):
    """Fecha operacion incorrecta."""
