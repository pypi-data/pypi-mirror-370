from enum import Enum


class TipoRespuestaAcuse(str, Enum):
    sincrona = 'sincrona'
    asincrona = 'asincrona'


class CodigoRespuestaAcuse(str, Enum):
    exito_core_bancario = 'EQ01'
    error_code_bancario = 'EQ02'
