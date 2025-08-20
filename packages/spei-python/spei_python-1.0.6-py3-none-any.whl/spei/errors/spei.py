from enum import Enum
from typing import Dict, Optional


class GenericoCodigoError(str, Enum):
    exitoso = 0
    categoria_incorrecta = -1
    error_interno = 3
    error_base_de_datos = 4
    fuera_de_sistema = 440
    clave_ordenante_requerida = 5
    clave_ordenante_invalida = 6
    tipo_pago_requerido = 7
    tipo_pago_invalido = 8
    monto_requerido = 9
    monto_invalido = 10


class NombreOrdenanteCodigoError(str, Enum):
    nombre_ordenante_requerido = 11
    nombre_ordenante_excede_longitud = 12
    nombre_ordenante_invalido = 13
    nombre_ordenante_vacio = 14


class TipoCuentaOrdenanteCodigoError(str, Enum):
    tipo_cuenta_ordenante_requerido = 15
    tipo_cuenta_ordenante_invalido = 16


class CuentaOrdenanteCodigoError(str, Enum):
    cuenta_ordenante_requerida = 17
    cuenta_ordenante_solo_digitos = 18
    cuenta_ordenante_excede_longitud = 19
    cuenta_ordenante_solo_ceros = 20
    cuenta_ordenante_clabe_longitud_incorrecta = 21
    cuenta_ordenante_tarjeta_longitud_incorrecta = 22
    cuenta_ordenante_digito_verificador_incorrecto = 202


class IdentificacionCuentaOrdenanteCodigoError(str, Enum):
    identification_cuenta_ordenante_invalida = 23
    identification_cuenta_ordenante_excede_longitud = 24
    identification_cuenta_ordenante_caracteres_invalidos = 25
    identification_cuenta_ordenante_vacio = 26


class NombreBeneficiarioCodigoError(str, Enum):
    nombre_beneficiario_requerido = 27
    nombre_beneficiario_excede_longitud = 28
    nombre_beneficiario_caracters_invalidos = 29
    nombre_beneficiario_vacio = 30


class TipoCuentaBeneficiarioCodigoError(str, Enum):
    tipo_cuenta_beneficiario_requerido = 31
    tipo_cuenta_beneficiario_invalido = 32


class CuentaBeneficiarioCodigoError(str, Enum):
    cuenta_beneficiario_requerida = 33
    cuenta_beneficiario_solo_digitos = 34
    cuenta_beneficiario_excede_longitud = 35
    cuenta_beneficiario_solo_ceros = 36
    cuenta_beneficiario_clabe_longitud_incorrecta = 37
    cuenta_beneficiario_tarjeta_longitud_incorrecta = 38


class IdentificacionBeneficiarioCodigoError(str, Enum):
    identificacion_beneficiario_invalida = 39
    identificacion_beneficiario_excede_longitud = 40
    identificacion_beneficiario_caracteres_invalidos = 41
    identificacion_beneficiario_vacio = 42


class ConceptoCodigoError(str, Enum):
    concepto_requerido = 43
    concepto_excede_longitud = 44
    concepto_invalido = 45
    concepto_vacio = 46


class IvaCodigoError(str, Enum):
    iva_requerido = 47
    iva_mayor_a_cero = 48
    iva_menor_a_maximo = 49  # 9999999999999999.99


class ReferenciaCodigoError(str, Enum):
    referencia_requerida = 50
    referencia_mayor_a_cero = 51
    referencia_excede_longitud = 52


class ReferenciaCobranzaCodigoError(str, Enum):
    referencia_cobranza_requerida = 53
    referencia_cobranza_invalida = 54
    referencia_cobranza_excede_longitud = 55
    referencia_cobranza_solo_ceros = 56


class ClavePagoCodigoError(str, Enum):
    clave_pago_requerida = 57
    clave_pago_excede_longitud = 58
    clave_pago_invalida = 59
    clave_pago_vacia = 60


class NombreBeneficiario2CodigoError(str, Enum):
    nombre_beneficiario_2_requerido = 61
    nombre_beneficiario_2_excede_longitud = 62
    nombre_beneficiario_2_caracters_invalidos = 63
    nombre_beneficiario_2_vacio = 64


class TipoCuentaBeneficiario2CodigoError(str, Enum):
    tipo_cuenta_beneficiario_2_requerido = 65
    tipo_cuenta_beneficiario_2_invalido = 66


class CuentaBeneficiario2CodigoError(str, Enum):
    cuenta_beneficiario_2_requerida = 67
    cuenta_beneficiario_2_solo_digitos = 68
    cuenta_beneficiario_2_excede_longitud = 69
    cuenta_beneficiario_2_solo_ceros = 70
    cuenta_beneficiario_2_clabe_longitud_incorrecta = 71
    cuenta_beneficiario_2_tarjeta_longitud_incorrecta = 72


class IdentificacionBeneficiario2CodigoError(str, Enum):
    identificacion_beneficiario_2_invalida = 73
    identificacion_beneficiario_2_excede_longitud = 74
    identificacion_beneficiario_2_caracteres_invalidos = 75
    identificacion_beneficiario_2_vacio = 76


class Concepto2CodigoError(str, Enum):
    concepto_2_requerido = 77
    concepto_2_excede_longitud = 78
    concepto_2_invalido = 79
    concepto_2_vacio = 80


class TipoOperacionCodigoError(str, Enum):
    tipo_operacion_requerido = 81
    tipo_operacion_invalido = 82


class MedioEntregaCodigoError(str, Enum):
    medio_entrega_requerido = 83
    medio_entrega_invalido = 84


class PrioridadCodigoError(str, Enum):
    prioridad_requerido = 85
    prioridad_invalido = 86


class TopologiaCodigoError(str, Enum):
    topologia_requerido = 87
    topologia_invalido = 88


class ClaveRastreoCodigoError(str, Enum):
    clave_rastreo_excede_longitud = 89
    clave_rastreo_invalido = 90
    clave_rastreo_vacio = 91
    clave_rastreo_requerida = 92


class OtrosCodigoError(str, Enum):
    otros_fecha_operacion_requerido = 93
    otros_tipo_traspaso_requerido = 94
    otros_tipo_traspaso_invalido = 95
    otros_medio_entrega_vacio = 96
    otros_usuario_captura_requerido = 97
    otros_estado_envio_requerido = 98
    otros_estado_envio_invalido = 99
    otros_clave_rastreo_existente = 100
    otros_usuario_no_existe = 101
    otros_causa_devolucion_invalida = 102
    otros_causa_devolucion_requerida = 103
    otros_fecha_operacion_fecha_invalida = 104
    otros_fecha_operacion_hora_invalida = 105
    otros_tipo_orden_requerido = 106
    otros_tipo_orden_invalido = 107
    otros_fecha_operacion_invalida = 108  # yyyyMMdd
    otros_op_folio_invalido = 109  # -1
    otros_op_folio_invalido_2 = 110  # -1
    otros_fecha_operacion_incorrecta = 111  # debe ser la del sistema karpay
    otros_cuenta_beneficiario_2_requerida = 112
    otros_tipo_cuenta_beneficiario_2_requerida = 113
    otros_devolucion_sin_correspondencia = 114
    otros_tipo_pago_invalido = 115
    otros_tipo_cuenta_celular_cuenta_ordenante_invalida = 116  # 10 digitos
    otros_tipo_cuenta_celular_cuenta_beneficiario_invalida = 117  # 10 digitos
    otros_cde_vacio = 118
    otros_cde_requerido = 119
    otros_usuario_autorizado_requerido_traspasos = 120
    otros_tipo_pago_horario_invalido = 121
    otros_tipo_pago_cuenta_beneficiario_invalido = 122
    otros_operaciones_concluidas = 123
    otros_tipo_cuenta_ordenante_requerido = 124
    otros_tipo_cuenta_beneficiario_requerida = 125
    otros_cuenta_beneficiario_2_invalida = 126
    otros_tipo_de_pago_invalido = 127
    otros_cuenta_clabe_invalida = 175
    otros_usuario_no_pertenece_empresa = -20
    otros_tipo_cuenta_ordenante_no_habilitado_habiles = -21
    otros_tipo_cuenta_ordenante_no_habilitado_inhabiles = -22
    otros_tipo_cuenta_ordenante_fuera_horario_habiles = -23
    otros_tipo_cuenta_ordenante_fuera_horario_inhabiles = -24
    otros_tipo_cuenta_beneficiario_no_habilitado_habiles = -25
    otros_tipo_cuenta_beneficiario_no_habilitado_inhabiles = -26
    otros_tipo_cuenta_beneficiario_fuera_horario_habiles = -27
    otros_tipo_cuenta_beneficiario_fuera_horario_inhabiles = -28
    otros_tipo_cuenta_beneficiario_2_no_habilitado_habiles = -29
    otros_tipo_cuenta_beneficiario_2_no_habilitado_inhabiles = -30
    otros_tipo_cuenta_beneficiario_2_fuera_horario_habiles = -31
    otros_tipo_cuenta_beneficiario_2_fuera_horario_inhabiles = -32
    otros_cuenta_ordenante_no_pertence_banxico = -33
    otros_tipo_pago_invalido_coa_poa = -34
    otros_institucion_no_certificada_poa = -35
    otros_cuenta_ordenante_domicilio_requerido = 128
    otros_cuenta_ordenante_domicilio_excede_longitud = 129
    otros_cuenta_ordenante_domicilio_invalido = 130
    otros_cuenta_ordenante_domicilio_vacio = 131


class CodigoPostalOrdenante(str, Enum):
    codigo_postal_requerido = 132
    codigo_postal_numerico = 133
    codigo_postal_excede_longitud = 134
    codigo_postal_vacio = 135


class FechaConstitucionOrdenante(str, Enum):
    fecha_constitucion_requerido = 136
    fecha_constitucion_excede_longitud = 137
    fecha_constitucion_invalida = 138


class DevolucionExtemporaneaCodigoError(str, Enum):
    devolucion_extemporanea_clave_rastreo_requerido = 400
    devolucion_extemporanea_clave_rastreo_excede_longitud = 401
    devolucion_extemporanea_clave_rastreo_invalida = 402
    devolucion_extemporanea_folio_paquete_longitud_incorrecta = 403
    devolucion_extemporanea_folio_paquete_numerico = 404
    devolucion_extemporanea_folio_paquete_vacio = 405
    devolucion_extemporanea_folio_pago_longitud_incorrecta = 406
    devolucion_extemporanea_folio_pago_solo_numeros = 407
    devolucion_extemporanea_folio_pago_vacio = 409
    devolucion_extemporanea_fecha_operacion_original_requerida = 410
    devolucion_extemporanea_fecha_operacion_original_longitud_incorrecta = 411
    devolucion_extemporanea_interes_original_requerido = 412
    devolucion_extemporanea_interes_original_longitud_incorrecta = 413
    devolucion_extemporanea_interes_original_invalido = 414
    devolucion_extemporanea_interes_original_no_permitido = 415
    devolucion_extemporanea_monto_original_requerido = 416
    devolucion_extemporanea_monto_original_longitud_incorrecta = 417
    devolucion_extemporanea_monto_original_invalido = 418
    devolucion_extemporanea_monto_original_no_permitido = 419
    devolucion_extemporanea_clave_rastreo_hexadecimal_requerido = 420
    devolucion_extemporanea_clave_rastreo_hexadecimal_longitud_incorrecta = 421


class ClasificacionOperacionCodigoError(str, Enum):
    clasificacion_operacion_requerido = 139
    clasificacion_operacion_excede_longitud = 140
    clasificacion_operacion_solo_numerica = 141
    clasificacion_operacion_invalido = 142


class DireccionIPCodigoError(str, Enum):
    direccion_ip_requerido = 143
    direccion_ip_excede_longitud = 144
    direccion_ip_invalida = 145


class FechaInstruccionCodigoError(str, Enum):
    fecha_instruccion_requerida = 146
    fecha_instruccion_excede_longitud = 147
    fecha_instruccion_invalido = 148


class HoraInstruccionCodigoError(str, Enum):
    hora_instruccion_requerida = 149
    hora_instruccion_excede_longitud = 150
    hora_instruccion_invalido = 151


class FechaAceptacionCodigoError(str, Enum):
    fecha_aceptacion_requerida = 152
    fecha_aceptacion_excede_longitud = 153
    fecha_aceptacion_invalido = 154


class HoraAceptacionCodigoError(str, Enum):
    hora_aceptacion_requerida = 155
    hora_aceptacion_excede_longitud = 156
    hora_aceptacion_invalido = 157


class ClaveBancoUsuarioCodigoError(str, Enum):
    clave_banco_usuario_requerida = 158
    clave_banco_usuario_numerica = 159
    clave_banco_usuario_excede_longitud = 160
    clave_banco_usuario_solo_ceros = 161


class TipoCuentaBancoUsuarioCodigoError(str, Enum):
    tipo_cuenta_banco_usuario_requerido = 162
    tipo_cuenta_banco_usuario_invalida = 163


class BancoUsuarioCodigoError(str, Enum):
    banco_usuario_requerido = 164
    banco_usuario_numerica = 165
    banco_usuario_excede_longitud = 166
    banco_usuario_solo_ceros = 167
    banco_usuario_tipo_cuenta_clabe_invalida = 168
    banco_usuario_tipo_cuenta_tarjeta_invalida = 169
    banco_usuario_primeros_digitos_incorrectos = 172  # [1,2]
    banco_usuario_fiel_invalida = 173
    banco_usuario_cuenta_inexistente = 174
    # no pertenece al participante
    banco_usuario_tipo_cuenta_clabe_cuenta_ordenante_incorrecta = 422
    banco_usuario_digito_verificador_incorrecto = 423
    # no coincide monto menos el interes
    banco_usuario_monto_original_incorrecto = 424
    # no es posible una devolucion de una devolucion extratemporanea  noqa:E501
    banco_usuario_devolucion_extratemporanea_no_permitida = 425
    banco_usuario_devolucion_extratemporanea_fecha_incorrecta = 426
    # no es posible una devolucion de una devolucion
    banco_usuario_devolucion_no_permitida = 427


class PagoFacturaCodigoError(str, Enum):
    pago_factura_requerido = 428
    pago_factura_excede_longitud = 429
    pago_factura_invalida = 430
    pago_factura_incorrecto = 431
    pago_factura_faltan_datos = 432
    pago_factura_uuid_invalido = 433
    pago_factura_importe_invalido = 434
    pago_factura_excede_numero = 435
    pago_factura_tipo_pago_invalido = 188
    pago_factura_firma_invalida = 436
    pago_factura_certificado_no_encontrado = 437
    pago_factura_sistema_no_disponible = 441
    pago_factura_listener_outgoing_no_habilitado = 500


class CoDiCodigoError(str, Enum):
    codi_certificado_invalido = 442
    codi_certificado_requerido = 443
    codi_certificado_excede_longitud = 444
    codi_folio_codi_requerido = 445
    codi_folio_codi_invalido = 446
    codi_folio_codi_excede_longitud = 447
    codi_pago_comision_requerido = 448
    codi_pago_comision_invalido = 449
    codi_pago_comision_numero = 450
    codi_monto_comision_requerido = 451
    codi_monto_comision_invalido = 452
    codi_telefono_ordenante_numerico = 453
    codi_telefono_ordenante_requerido = 454
    codi_telefono_ordenante_invalido = 455
    codi_telefono_ordenante_excede_longitud = 456
    codi_digito_verificador_ordenante_numerico = 457
    codi_digito_verificador_ordenante_requerido = 458
    codi_digito_verificador_ordenante_invalido = 459
    codi_digito_verificador_ordenante_excede_longitud = 460
    codi_telefono_beneficiario_numerico = 461
    codi_telefono_beneficiario_requerido = 462
    codi_telefono_beneficiario_invalido = 463
    codi_telefono_beneficiario_excede_longitud = 464
    codi_digito_verificador_beneficiario_numerico = 465
    codi_digito_verificador_beneficiario_requerido = 466
    codi_digito_verificador_beneficiario_invalido = 467
    codi_digito_verificador_beneficiario_excede_longitud = 468
    codi_digito_verificador_comercio_alfanumerico = 469
    codi_digito_verificador_comercio_requerido = 470
    codi_digito_verificador_comercio_excede_longitud = 471


class DevolucionAcreditadaCodigoError(str, Enum):
    devolucion_acreditada_no_encontrada = 472
    devolucion_acreditada_devolucion_no_permitida = 473
    devolucion_acreditada_institucion_incorrecta = 474
    devolucion_acreditada_orden_no_liquidada = 475
    # es la misma que la fecha de operación actual
    devolucion_acreditada_fecha_operacion_incorrecta = 476
    devolucion_acreditada_abono_no_encontrado = 477
    devolucion_acreditada_no_permitida = 478
    devolucion_acreditada_ya_devuelta = 479
    devolucion_acreditada_orden_no_liquidada_banxico = 480
    # no puede ser mayor al de la orden original
    devolucion_acreditada_devolucion_tipo_pago_codi_monto_incorrecto = 481
    # no puede ser superior al original
    devolucion_acreditada_monto_superior_original = 482
    devolucion_acreditada_monto_incorrecto = 483


ERROR_CODES = (
    GenericoCodigoError,
    NombreOrdenanteCodigoError,
    TipoCuentaOrdenanteCodigoError,
    CuentaOrdenanteCodigoError,
    IdentificacionCuentaOrdenanteCodigoError,
    NombreBeneficiarioCodigoError,
    CuentaBeneficiarioCodigoError,
    TipoCuentaBeneficiarioCodigoError,
    IdentificacionBeneficiarioCodigoError,
    ConceptoCodigoError,
    IvaCodigoError,
    ReferenciaCodigoError,
    ReferenciaCobranzaCodigoError,
    ClavePagoCodigoError,
    NombreBeneficiario2CodigoError,
    CuentaBeneficiario2CodigoError,
    TipoCuentaBeneficiario2CodigoError,
    IdentificacionBeneficiario2CodigoError,
    Concepto2CodigoError,
    TipoOperacionCodigoError,
    MedioEntregaCodigoError,
    PrioridadCodigoError,
    TopologiaCodigoError,
    ClaveRastreoCodigoError,
    OtrosCodigoError,
    CodigoPostalOrdenante,
    FechaConstitucionOrdenante,
    DevolucionExtemporaneaCodigoError,
    ClasificacionOperacionCodigoError,
    DireccionIPCodigoError,
    FechaInstruccionCodigoError,
    HoraInstruccionCodigoError,
    FechaAceptacionCodigoError,
    HoraAceptacionCodigoError,
    ClaveBancoUsuarioCodigoError,
    TipoCuentaBancoUsuarioCodigoError,
    BancoUsuarioCodigoError,
    PagoFacturaCodigoError,
    CoDiCodigoError,
    DevolucionAcreditadaCodigoError,
)


# Generate all members for CodigoError
_members = {}
for error_enum in ERROR_CODES:
    _members.update(
        {name: member.value for name, member in error_enum.__members__.items()},
    )


class CodigoError(str, Enum):
    """Unified error codes enum that combines all SPEI error codes.

    This implementation provides better type hints and is more
    maintainable.
    """

    # Add all enum members
    locals().update(_members)  # noqa: WPS421, WPS604

    @classmethod
    def get_all_errors(cls) -> Dict[str, int]:
        """Returns a dictionary of all error codes and their values."""
        return {name: member.value for name, member in cls.__members__.items()}

    @classmethod
    def get_error_by_value(cls, value: int) -> Optional[str]:  # noqa: WPS110
        """Get error name by its value."""
        for member in cls.__members__.values():
            if member.value == value:
                return member.name
        return None

    @classmethod
    def get_error_by_name(cls, name: str) -> Optional[int]:
        """Get error value by its name."""
        try:
            return cls[name].value
        except KeyError:
            return None
