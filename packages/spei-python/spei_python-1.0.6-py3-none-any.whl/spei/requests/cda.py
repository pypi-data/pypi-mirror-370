from lxml import etree

from spei.resources import CDA

SOAP_NS = 'http://schemas.xmlsoap.org/soap/envelope/'
PRAXIS_NS = 'http://www.praxis.com.mx/EnvioCda/'


class CDAElement(object):
    def __new__(cls, element):
        cda = etree.Element(
            etree.QName(PRAXIS_NS, 'generaCda'),
        )
        cda.append(element)
        return cda


class BodyElement(object):
    def __new__(cls, respuesta):
        body = etree.Element(etree.QName(SOAP_NS, 'Body'))
        body.append(respuesta)
        return body


class EnvelopeElement(object):
    def __new__(cls, body):
        namespaces_uris = {
            'soapenv': SOAP_NS,
            'env': PRAXIS_NS,
        }
        envelope = etree.Element(
            etree.QName(SOAP_NS, 'Envelope'),
            nsmap=namespaces_uris,
        )
        envelope.append(body)
        return envelope


class CDARequest(object):
    def __init__(self, mensaje: CDA):
        self._envelope = EnvelopeElement(BodyElement(CDAElement(mensaje.build_xml())))

    @property
    def tree(self):
        return self._envelope

    def to_string(self) -> bytes:
        """Returns the SOAP request as a string encoded in cp850 (bytes)."""
        return etree.tostring(self._envelope, encoding='cp850', xml_declaration=True)
