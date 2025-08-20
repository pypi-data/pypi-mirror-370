from typing import List

from lxml import etree

from spei.resources import Respuesta
from spei.types import CategoriaOrdenPago

SOAP_NS = 'http://schemas.xmlsoap.org/soap/envelope/'
PRAXIS_NS = 'http://www.praxis.com.mx/'
XML_SCHEMA_NS = 'http://www.w3.org/2001/XMLSchema-instance'


class MensajeElement(object):
    def __new__(cls, respuestas: List[Respuesta], categoria: CategoriaOrdenPago):
        qname = etree.QName(XML_SCHEMA_NS, 'type')

        mensaje = etree.Element(
            'mensaje',
            {qname: 'mensaje'},
            categoria=categoria,
        )

        for respuesta in respuestas:
            mensaje.append(respuesta.build_xml())

        return mensaje


class RespuestaElement(object):
    def __new__(cls, mensaje):
        respuesta = etree.Element(
            etree.QName(PRAXIS_NS, 'respuesta'),
            nsmap={None: PRAXIS_NS},
        )
        respuesta.text = etree.tostring(mensaje, xml_declaration=True, encoding='cp850')
        return respuesta


class BodyElement(object):
    def __new__(cls, respuesta):
        body = etree.Element(etree.QName(SOAP_NS, 'Body'))
        body.append(respuesta)
        return body


class EnvelopeElement(object):
    def __new__(cls, body):
        etree.register_namespace('S', SOAP_NS)
        envelope = etree.Element(etree.QName(SOAP_NS, 'Envelope'))
        envelope.append(body)
        return envelope


class RespuestaRequest(object):
    def __new__(cls, respuestas: List[Respuesta], categoria, as_string=True):
        envelope = RespuestaElement(MensajeElement(respuestas, categoria))
        if not as_string:
            return envelope
        return etree.tostring(envelope, xml_declaration=True, encoding='utf-8')
