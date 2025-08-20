from lxml import etree

from spei.resources import Orden

SOAP_NS = 'http://schemas.xmlsoap.org/soap/envelope/'
PRAXIS_NS = 'http://www.praxis.com.mx/'


class MensajeElement(object):
    def __new__(cls, orden: Orden):
        mensaje = etree.Element('mensaje', categoria=orden.categoria)
        mensaje.append(orden.build_xml())

        return mensaje


class OrdenPagoElement(object):
    def __new__(cls, mensaje):
        ordenpago = etree.Element(etree.QName(PRAXIS_NS, 'ordenpago'))

        mensaje_str = etree.tostring(mensaje, encoding='cp850')
        ordenpago.text = etree.CDATA(mensaje_str.decode('cp850'))

        return ordenpago


class BodyElement(object):
    def __new__(cls, ordenpago):
        body = etree.Element(etree.QName(SOAP_NS, 'Body'))
        body.append(ordenpago)

        return body


class EnvelopeElement(object):
    def __new__(cls, body):
        namespaces_uris = {
            'soapenv': SOAP_NS,
            'prax': PRAXIS_NS,
        }
        envelope = etree.Element(
            etree.QName(SOAP_NS, 'Envelope'),
            nsmap=namespaces_uris,
        )
        envelope.append(body)

        return envelope


class OrdenRequest(object):
    def __init__(self, orden: Orden):
        self._envelope: etree._Element = EnvelopeElement(  # noqa: WPS437
            BodyElement(OrdenPagoElement(MensajeElement(orden))),
        )

    @property
    def tree(self) -> etree._Element:  # noqa: WPS437
        return self._envelope

    def to_string(self) -> bytes:
        return etree.tostring(self._envelope, encoding='cp850', xml_declaration=True)
