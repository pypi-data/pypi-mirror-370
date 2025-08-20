from spei.types import TipoPagoOrdenPago

PAYMENT_TYPES_WITH_DEFAULT_FIELDS = (
    TipoPagoOrdenPago.devolucion_no_acreditada,
    TipoPagoOrdenPago.devolucion_extemporanea_no_acreditada,
    TipoPagoOrdenPago.participante_a_participante,
    TipoPagoOrdenPago.devolucion_acreditada,
    TipoPagoOrdenPago.devolucion_especial_acreditada,
)

PAYMENT_TYPES_WITH_ORIGIN_ACCOUNT = (
    TipoPagoOrdenPago.tercero_a_ventanilla,
    TipoPagoOrdenPago.tercero_a_participante,
    TipoPagoOrdenPago.devolucion_extemporanea_acreditada,
    TipoPagoOrdenPago.devolucion_extemporanea_especial_acreditada,
    TipoPagoOrdenPago.devolucion_especial_acreditada,
)

PAYMENT_TYPES_WITH_BENEFICIARY_ACCOUNT = (
    TipoPagoOrdenPago.participante_a_tercero,
    TipoPagoOrdenPago.participante_a_tercero_fsw,
)

PAYMENT_TYPES_WITH_ORIGIN_AND_BENEFICIARY_ACCOUNT = (
    TipoPagoOrdenPago.tercero_a_tercero,
    TipoPagoOrdenPago.tercero_a_tercero_fsw,
    TipoPagoOrdenPago.nomina,
    TipoPagoOrdenPago.pago_factura,
    TipoPagoOrdenPago.cobros_no_presenciales_de_una_ocasion,
    TipoPagoOrdenPago.cobros_no_presenciales_recurrentes,
    TipoPagoOrdenPago.cobros_presenciales_de_una_ocasion,
)

PAYMENT_TYPES_WITH_BENEFICIARY_AND_ADDITIONAL_BENEFICIARY_ACCOUNT = (
    TipoPagoOrdenPago.participante_a_tercero_vostro,
    TipoPagoOrdenPago.participante_a_tercero_vostro_fsw,
)

PAYMENT_TYPES_WITH_ORIGIN_BENEFICIARY_AND_ADDITIONAL_BENEFICIARY_ACCOUNT = (
    TipoPagoOrdenPago.tercero_a_tercero_vostro,
    TipoPagoOrdenPago.tercero_a_tercero_vostro_fsw,
)

REMITTANCE_PAYMENT_TYPES = (
    TipoPagoOrdenPago.remesa_entrante,
    TipoPagoOrdenPago.remesa_saliente,
)

INDIRECT_PAYMENT_TYPES = (
    TipoPagoOrdenPago.tercero_indirecto_a_tercero,
    TipoPagoOrdenPago.presencial_de_una_ocasion_indirecto,
    TipoPagoOrdenPago.no_presencial_de_una_ocasion_indirecto,
    TipoPagoOrdenPago.no_presencial_recurrente_indirecto,
)
