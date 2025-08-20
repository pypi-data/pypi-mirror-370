# mypy: disable-error-code="override"

from datetime import date
from typing import Optional

from spei import types
from spei.resources.orden import Orden


class TerceroATercero(Orden):
    op_nom_ord: str
    op_tc_clave_ord: types.TipoCuentaOrdenPago
    op_cuenta_ord: str
    op_rfc_curp_ord: str

    op_nom_ben: str
    op_tc_clave_ben: types.TipoCuentaOrdenPago
    op_cuenta_ben: str
    op_rfc_curp_ben: Optional[str] = None

    op_concepto_pag_2: str
    op_iva: Optional[float] = None
    op_ref_numerica: int
    op_ref_cobranza: Optional[str] = None


class TerceroAVentilla(Orden):
    op_nom_ord: str
    op_tc_clave_ord: types.TipoCuentaOrdenPago
    op_cuenta_ord: str
    op_rfc_curp_ord: str

    op_nom_ben: str

    op_concepto_pago: str
    op_iva: Optional[float] = None
    op_clave_pago: str


class TerceroATerceroVostro(Orden):
    op_nom_ord: str
    op_tc_clave_ord: types.TipoCuentaOrdenPago
    op_cuenta_ord: str
    op_rfc_curp_ord: str

    op_nom_ben: str
    op_tc_clave_ben: types.TipoCuentaOrdenPago
    op_cuenta_ben: str

    op_nom_ben_2: Optional[str] = None
    op_tc_clave_ben_2: Optional[types.TipoCuentaOrdenPago] = None
    op_cuenta_ben_2: Optional[str] = None
    op_rfc_curp_ben_2: Optional[str] = None

    op_concepto_pago: str
    op_concepto_pag_2: Optional[str] = None
    op_iva: Optional[float] = None
    op_ref_numerica: int


class TerceroAParticipante(Orden):
    op_nom_ord: str
    op_tc_clave_ord: types.TipoCuentaOrdenPago
    op_cuenta_ord: str
    op_rfc_curp_ord: Optional[str] = None

    op_concepto_pago: str
    op_iva: Optional[float] = None
    op_ref_numerica: int

    op_to_clave: int


class ParticipanteATercero(Orden):
    op_nom_ben: str
    op_tc_clave_ben: types.TipoCuentaOrdenPago
    op_cuenta_ben: str
    op_rfc_curp_ben: Optional[str] = None

    op_concepto_pag_2: str
    op_iva: Optional[float] = None
    op_ref_numerica: int


class ParticipanteATerceroVostro(Orden):
    op_nom_ben: str
    op_tc_clave_ben: types.TipoCuentaOrdenPago
    op_cuenta_ben: str

    op_nom_ben_2: Optional[str] = None
    op_tc_clave_ben_2: Optional[types.TipoCuentaOrdenPago] = None
    op_cuenta_ben_2: Optional[str] = None
    op_rfc_curp_ben_2: Optional[str] = None

    op_concepto_pago: str
    op_concepto_pag_2: Optional[str] = None
    op_iva: Optional[float] = None
    op_ref_numerica: int


class ParticipanteAParticipante(Orden):
    op_concepto_pago: str
    op_iva: Optional[float] = None
    op_ref_numerica: int

    op_to_clave: int


class TerceroATerceroFSW(Orden):
    op_nom_ord: str
    op_tc_clave_ord: Optional[types.TipoCuentaOrdenPago] = None
    op_cuenta_ord: Optional[str] = None
    op_rfc_curp_ord: Optional[str] = None

    op_nom_ben: str
    op_tc_clave_ben: Optional[types.TipoCuentaOrdenPago] = None
    op_cuenta_ben: Optional[str] = None
    op_rfc_curp_ben: Optional[str] = None

    op_concepto_pag_2: str
    op_iva: Optional[float] = None
    op_ref_numerica: int
    op_ref_cobranza: Optional[str] = None


class TerceroATerceroVostroFSW(Orden):
    op_nom_ord: str
    op_tc_clave_ord: Optional[types.TipoCuentaOrdenPago] = None
    op_cuenta_ord: Optional[str] = None
    op_rfc_curp_ord: Optional[str] = None

    op_nom_ben: str
    op_tc_clave_ben: Optional[types.TipoCuentaOrdenPago] = None
    op_cuenta_ben: Optional[str] = None

    op_nom_ben_2: Optional[str] = None
    op_tc_clave_ben_2: Optional[types.TipoCuentaOrdenPago] = None
    op_cuenta_ben_2: Optional[str] = None
    op_rfc_curp_ben_2: Optional[str] = None

    op_concepto_pago: str
    op_concepto_pag_2: Optional[str] = None
    op_iva: Optional[float] = None
    op_ref_numerica: int


class ParticipanteATerceroFSW(Orden):
    op_nom_ben: str
    op_tc_clave_ben: Optional[types.TipoCuentaOrdenPago] = None
    op_cuenta_ben: Optional[str] = None
    op_rfc_curp_ben: Optional[str] = None

    op_concepto_pag_2: str
    op_iva: Optional[float] = None
    op_ref_numerica: int


class ParticipanteATerceroVostroFSW(Orden):
    op_nom_ben: str
    op_tc_clave_ben: Optional[types.TipoCuentaOrdenPago] = None
    op_cuenta_ben: Optional[str] = None

    op_nom_ben_2: Optional[str] = None
    op_tc_clave_ben_2: Optional[types.TipoCuentaOrdenPago] = None
    op_cuenta_ben_2: Optional[str] = None
    op_rfc_curp_ben_2: Optional[str] = None

    op_concepto_pago: Optional[str] = None
    op_concepto_pag_2: Optional[str] = None
    op_iva: Optional[float] = None
    op_ref_numerica: Optional[int] = None


class Nomina(Orden):
    op_nom_ord: str
    op_tc_clave_ord: types.TipoCuentaOrdenPago
    op_cuenta_ord: str
    op_rfc_curp_ord: str

    op_nom_ben: str
    op_tc_clave_ben: types.TipoCuentaOrdenPago
    op_cuenta_ben: str
    op_rfc_curp_ben: Optional[str] = None

    op_concepto_pag_2: str
    op_iva: Optional[float] = None
    op_ref_numerica: int
    op_ref_cobranza: Optional[str] = None


class PagoFactura(Orden):
    op_nom_ord: str
    op_tc_clave_ord: types.TipoCuentaOrdenPago
    op_cuenta_ord: str
    op_rfc_curp_ord: str

    op_nom_ben: str
    op_tc_clave_ben: types.TipoCuentaOrdenPago
    op_cuenta_ben: str
    op_rfc_curp_ben: Optional[str] = None

    op_concepto_pag_2: str
    op_ref_numerica: int

    op_info_factura: str


class CobrosPresencialesUnaOcasion(Orden):
    op_nom_ord: str
    op_tc_clave_ord: types.TipoCuentaOrdenPago
    op_cuenta_ord: str
    op_rfc_curp_ord: str

    op_nom_ben: str
    op_tc_clave_ben: types.TipoCuentaOrdenPago
    op_cuenta_ben: str
    op_rfc_curp_ben: Optional[str] = None

    op_concepto_pag_2: str
    op_ref_numerica: int

    op_num_cel_ord: int
    op_digito_ver_ord: int

    op_num_cel_ben: int
    op_digito_ver_ben: int

    op_folio_codi: str
    op_comision_trans: int
    op_monto_comision: float


class CobrosNoPresencialesUnaOcasion(Orden):
    op_nom_ord: str
    op_tc_clave_ord: types.TipoCuentaOrdenPago
    op_cuenta_ord: str
    op_rfc_curp_ord: str

    op_nom_ben: str
    op_tc_clave_ben: types.TipoCuentaOrdenPago
    op_cuenta_ben: str
    op_rfc_curp_ben: Optional[str] = None

    op_concepto_pag_2: str
    op_ref_numerica: int

    op_num_cel_ord: int
    op_digito_ver_ord: int

    op_folio_codi: str
    op_comision_trans: int
    op_monto_comision: float

    op_cert_comer_env: int
    op_digito_ver_comer: int


class CobrosNoPresencialesRecurrentes(Orden):
    op_nom_ord: str
    op_tc_clave_ord: types.TipoCuentaOrdenPago
    op_cuenta_ord: str
    op_rfc_curp_ord: str

    op_nom_ben: str
    op_tc_clave_ben: types.TipoCuentaOrdenPago
    op_cuenta_ben: str
    op_rfc_curp_ben: Optional[str] = None

    op_concepto_pag_2: str
    op_ref_numerica: int

    op_num_cel_ord: int
    op_digito_ver_ord: int

    op_folio_codi: str
    op_comision_trans: int
    op_monto_comision: float

    op_cert_comer_env: int
    op_digito_ver_comer: int


class CobrosNoPresencialesNoRecurrentesTercero(Orden):
    op_nom_ord: str
    op_tc_clave_ord: types.TipoCuentaOrdenPago
    op_cuenta_ord: str
    op_rfc_curp_ord: str

    op_nom_ben: str
    op_tc_clave_ben: types.TipoCuentaOrdenPago
    op_cuenta_ben: str
    op_rfc_curp_ben: Optional[str] = None

    op_nom_ben_2: str
    op_tc_clave_ben_2: types.TipoCuentaOrdenPago
    op_cuenta_ben_2: str
    op_rfc_curp_ben_2: Optional[str] = None

    op_concepto_pag_2: str
    op_ref_numerica: int

    op_num_cel_ord: int
    op_digito_ver_ord: int

    op_folio_codi: str
    op_comision_trans: int
    op_monto_comision: float

    op_cert_comer_env: int
    op_digito_ver_comer: int


class DevolucionNoAcreditada(Orden):
    op_cd_clave: types.TipoDevolucionOrdenPago


class DevolucionExtemporaneaNoAcreditada(Orden):
    op_tc_clave_ord: types.TipoCuentaOrdenPago
    op_cuenta_ord: str

    op_concepto_pag_2: str
    op_ref_numerica: int

    op_cd_clave: types.TipoDevolucionOrdenPago

    op_folio_ori: Optional[int] = None
    paq_folio_ori: Optional[int] = None

    op_fecha_oper_ori: date
    op_rastreo_ori: str
    op_monto_intereses: float
    op_monto_ori: float


class DevolucionAcreditada(Orden):
    op_rastreo_ori: str


class DevolucionExtemporaneaAcreditada(Orden):
    op_cuenta_ord: str

    op_concepto_pag_2: str
    op_ref_numerica: int

    op_folio_ori: Optional[int] = None
    paq_folio_ori: Optional[int] = None

    op_fecha_oper_ori: date
    op_rastreo_ori: str
    op_monto_ori: float


class DevolucionEspecialAcreditada(Orden):
    op_rastreo_ori: str
    op_monto_ori: float

    op_indica_ben_rec: Optional[int] = None


class DevolucionExtemporaneaEspecialAcreditada(Orden):
    op_tc_clave_ord: types.TipoCuentaOrdenPago
    op_cuenta_ord: str

    op_concepto_pag_2: str
    op_ref_numerica: int

    op_folio_ori: Optional[int] = None
    paq_folio_ori: Optional[int] = None

    op_fecha_oper_ori: date
    op_rastreo_ori: str
    op_monto_ori: float

    op_indica_ben_rec: Optional[int] = None
