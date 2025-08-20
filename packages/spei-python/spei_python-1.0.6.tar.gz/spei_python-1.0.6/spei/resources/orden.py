import re
from datetime import date, datetime
from typing import Any, Dict, Optional

from lxml import etree
from lxml.etree import _Element  # noqa: WPS450, WPS458
from pydantic import BaseModel, ConfigDict, field_validator

from spei import types
from spei.resources.validators import normalize_invalid_chars
from spei.types.common import InstitutionCode
from spei.utils import to_camel_case, to_pascal_case, to_snake_case  # noqa: WPS347

SOAP_NS = 'http://schemas.xmlsoap.org/soap/envelope/'
PRAXIS_NS = 'http://www.praxis.com.mx/'
_DATE_PATTERN = re.compile(r'^\d{4}(0[1-9]|1[0-2])(0[1-9]|[12][0-9]|3[01])$')
_CAMEL_CASE_FIELDS = frozenset(
    (
        'op_rastreo_ori',
        'op_fecha_oper_ori',
        'op_monto_ori',
        'op_monto_intereses',
        'op_comision_trans',
    ),
)


class Orden(BaseModel):
    model_config = ConfigDict(strict=False, coerce_numbers_to_str=True)

    id: int
    categoria: types.CategoriaOrdenPago
    op_fecha_oper: date
    op_folio: int
    op_monto: str
    op_tp_clave: types.TipoPagoOrdenPago
    op_cve_rastreo: str
    op_estado: types.EstadoOrdenPago
    op_tipo_orden: types.TipoOrdenPago
    op_prioridad: types.PrioridadOrdenPago
    op_me_clave: types.MedioEntregaOrdenPago
    op_topologia: types.TopologiaOrdenPago = (
        types.TopologiaOrdenPago.notify_on_payment_settlement
    )
    op_usu_clave: str
    # checksum
    op_firma_dig: str
    # origin info
    op_nom_ord: Optional[str] = None
    op_tc_clave_ord: Optional[types.TipoCuentaOrdenPago] = None
    op_cuenta_ord: Optional[str] = None
    op_rfc_curp_ord: Optional[str] = None
    # In Karpay only OpInsClave exists.
    # It is always the institution that generates the payment order.
    # For deposits, it is the other institution.
    # For transfers, it is Fondeadora.
    # Here we use OpInsClaveOrd and OpInsClaveBen to differentiate between them.
    op_ins_clave_ord: Optional[InstitutionCode] = None
    # destination info
    op_nom_ben: Optional[str] = None
    op_tc_clave_ben: Optional[types.TipoCuentaOrdenPago] = None
    op_cuenta_ben: Optional[str] = None
    op_rfc_curp_ben: Optional[str] = None
    op_ins_clave_ben: Optional[InstitutionCode] = None
    # participant info
    op_cuenta_participante_ord: Optional[str] = None
    op_nom_participante_ord: Optional[str] = None
    op_rfc_participante_ord: Optional[str] = None
    # additional destination info
    op_nom_ben_2: Optional[str] = None
    op_tc_clave_ben_2: Optional[types.TipoCuentaOrdenPago] = None
    op_cuenta_ben_2: Optional[str] = None
    op_rfc_curp_ben_2: Optional[str] = None
    # concept info
    op_concepto_pago: Optional[str] = None
    op_concepto_pag_2: Optional[str] = None
    # additional general info
    op_iva: Optional[float] = None
    op_ref_numerica: Optional[int] = None
    op_ref_cobranza: Optional[str] = None
    op_clave_pago: Optional[str] = None
    # refunds info
    op_to_clave: Optional[int] = None
    op_cd_clave: Optional[types.TipoDevolucionOrdenPago] = None
    # invoice info
    op_info_factura: Optional[str] = None
    # original info
    op_folio_ori: Optional[int] = None
    paq_folio_ori: Optional[int] = None
    op_fecha_oper_ori: Optional[date] = None
    op_rastreo_ori: Optional[str] = None
    op_monto_intereses: Optional[float] = None
    op_monto_ori: Optional[float] = None
    # beneficiary
    op_indica_ben_rec: Optional[int] = None
    # codi origin info
    op_num_cel_ord: Optional[int] = None
    op_digito_ver_ord: Optional[int] = None
    # codi destination info
    op_num_cel_ben: Optional[int] = None
    op_digito_ver_ben: Optional[int] = None
    # codi info
    op_folio_codi: Optional[str] = None
    op_comision_trans: Optional[int] = None
    op_monto_comision: Optional[float] = None
    # codi merchant info
    op_cert_comer_env: Optional[int] = None
    op_digito_ver_comer: Optional[int] = None
    # karpay system info
    op_fecha_cap: Optional[date] = None
    op_folio_servidor: Optional[int] = None
    op_usu_autoriza: Optional[str] = None
    op_err_clave: Optional[types.CodigoError] = None
    op_razon_rechazo: Optional[str] = None
    op_hora_cap: Optional[int] = None
    op_hora_liq_bm: Optional[int] = None
    op_hora_liq_sist: Optional[int] = None
    op_cde: Optional[str] = None
    op_cuenta_dev: Optional[str] = None
    op_hora_lectura_host: Optional[int] = None  # noq]a: N815
    op_hora_insercion: Optional[int] = None
    hr_deposito_acuse_banxico: Optional[int] = None
    paq_folio: Optional[int] = None
    ah_ar_clave: Optional[int] = None
    emp_clave: Optional[int] = None

    # remesas
    op_id_remesa: Optional[str] = None
    op_pais: Optional[str] = None
    op_divisa: Optional[str] = None
    op_tipo_cambio: Optional[float] = None
    op_nom_emisor_remesa: Optional[str] = None
    tc_clave_emisor_remesa: Optional[int] = None
    op_cuenta_emisor_remesa: Optional[str] = None
    op_rfc_curp_emisor_remesa: Optional[str] = None
    op_nom_ben_remesa: Optional[str] = None
    op_nom_prov_remesa_extranjera: Optional[str] = None
    op_nom_prov_remesa_nacional: Optional[str] = None
    op_nom_ben_indirecto_receptor: Optional[str] = None
    model_config = ConfigDict(use_enum_values=True)

    @field_validator('op_monto', mode='before')
    def set_amount(cls, value):  # noqa: WPS110, N805
        amount = float(value)
        return '{amount:.2f}'.format(amount=amount)

    def build_xml(self) -> _Element:  # noqa: WPS231, C901
        ordenpago: _Element = etree.Element(
            'ordenpago',
            attrib={'Id': str(self.id)},
            nsmap=None,
        )

        elements = self.model_dump(
            exclude_none=True,
            exclude={'id', 'categoria', 'op_ins_clave_ord'},
        )

        for element, value in elements.items():  # noqa: WPS110
            if element not in self.model_fields:
                continue

            if element == 'op_ins_clave_ben':
                subelement = etree.SubElement(
                    ordenpago,
                    'OpInsClave',
                    attrib={},
                    nsmap=None,
                )
                subelement.text = str(value)
                continue

            if element == 'op_firma_dig':  # Lower case o in op
                subelement = etree.SubElement(
                    ordenpago,
                    'opFirmaDig',
                    attrib={},
                    nsmap=None,
                )
                subelement.text = str(value)
                continue

            if 'op_fecha' in element:
                value = value.strftime('%Y%m%d')

            tag = (
                to_camel_case(element)
                if element in _CAMEL_CASE_FIELDS
                else to_pascal_case(element)
            )
            subelement = etree.SubElement(
                ordenpago,
                tag,
                attrib={},
                nsmap=None,
            )
            subelement.text = normalize_invalid_chars(str(value))

        return ordenpago

    @classmethod
    def parse_xml(cls, orden_element: _Element, categoria: types.CategoriaOrdenPago):
        """Parse XML element into an Orden instance."""
        orden_data: Dict[str, Any] = {
            'id': orden_element.attrib['Id'],
            'categoria': categoria,
        }

        for element in orden_element.getchildren():
            cls._process_xml_element(element, orden_data)

        return cls(**orden_data)

    @classmethod
    def _process_xml_element(
        cls,
        element: _Element,
        orden_data: Dict[str, Any],
    ) -> None:
        """Process a single XML element and update orden_data."""
        if not element.text:
            return

        tag = to_snake_case(element.tag)
        stripped = element.text.strip()

        if tag == 'op_ins_clave':
            orden_data['op_ins_clave_ord'] = stripped
            return

        if tag == 'op_firma_dig':
            orden_data['op_firma_dig'] = stripped
            return

        if tag not in cls.model_fields:
            return

        if 'op_fecha' in tag:
            orden_data[tag] = datetime.strptime(stripped, '%Y%m%d').date()
            return

        orden_data[tag] = stripped
