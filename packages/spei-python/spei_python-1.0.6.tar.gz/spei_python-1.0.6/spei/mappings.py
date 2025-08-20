from types import MappingProxyType
from typing import Mapping, Type

from spei.resources import payments
from spei.resources.orden import Orden
from spei.types import CategoriaOrdenPago, TipoPagoOrdenPago

ORDEN_RESPONSES = MappingProxyType(
    {
        CategoriaOrdenPago.odps_liquidadas_abonos: CategoriaOrdenPago.odps_liquidadas_abonos_respuesta,  # noqa: E501
        CategoriaOrdenPago.odps_liquidadas_cargos: CategoriaOrdenPago.odps_liquidadas_cargos_respuesta,  # noqa: E501
        CategoriaOrdenPago.odps_canceladas_local: CategoriaOrdenPago.odps_canceladas_local_respuesta,  # noqa: E501
        CategoriaOrdenPago.odps_canceladas_x_banxico: CategoriaOrdenPago.odps_canceladas_x_banxico_respuesta,  # noqa: E501
        CategoriaOrdenPago.cargar_odp: CategoriaOrdenPago.cargar_odp_respuesta,
    },
)

ORDEN_PAYMENT_TYPES: Mapping[TipoPagoOrdenPago, Type[Orden]] = MappingProxyType(
    {
        TipoPagoOrdenPago.devolucion_no_acreditada: payments.DevolucionNoAcreditada,
        TipoPagoOrdenPago.tercero_a_tercero: payments.TerceroATercero,
        TipoPagoOrdenPago.tercero_a_ventanilla: payments.TerceroAVentilla,
        TipoPagoOrdenPago.tercero_a_tercero_vostro: payments.TerceroATerceroVostro,
        TipoPagoOrdenPago.tercero_a_participante: payments.TerceroAParticipante,
        TipoPagoOrdenPago.participante_a_tercero: payments.ParticipanteATercero,
        TipoPagoOrdenPago.participante_a_tercero_vostro: payments.ParticipanteATerceroVostro,
        TipoPagoOrdenPago.participante_a_participante: payments.ParticipanteAParticipante,
        TipoPagoOrdenPago.tercero_a_tercero_fsw: payments.TerceroATerceroFSW,
        TipoPagoOrdenPago.tercero_a_tercero_vostro_fsw: payments.TerceroATerceroVostroFSW,
        TipoPagoOrdenPago.participante_a_tercero_fsw: payments.ParticipanteATerceroFSW,
        TipoPagoOrdenPago.participante_a_tercero_vostro_fsw: payments.TerceroATerceroFSW,
        TipoPagoOrdenPago.nomina: payments.Nomina,
        TipoPagoOrdenPago.pago_factura: payments.PagoFactura,
        TipoPagoOrdenPago.devolucion_extemporanea_no_acreditada: payments.DevolucionExtemporaneaNoAcreditada,
        TipoPagoOrdenPago.devolucion_acreditada: payments.DevolucionAcreditada,
        TipoPagoOrdenPago.devolucion_extemporanea_acreditada: payments.DevolucionExtemporaneaAcreditada,
        TipoPagoOrdenPago.cobros_presenciales_de_una_ocasion: payments.CobrosPresencialesUnaOcasion,
        TipoPagoOrdenPago.cobros_no_presenciales_de_una_ocasion: payments.CobrosNoPresencialesUnaOcasion,
        TipoPagoOrdenPago.cobros_no_presenciales_recurrentes: payments.CobrosNoPresencialesRecurrentes,
        TipoPagoOrdenPago.cobros_no_presenciales_a_nombre_de_tercero: payments.CobrosNoPresencialesNoRecurrentesTercero,
        TipoPagoOrdenPago.devolucion_especial_acreditada: payments.DevolucionEspecialAcreditada,
        TipoPagoOrdenPago.devolucion_extemporanea_especial_acreditada: payments.DevolucionEspecialAcreditada,
    },
)
