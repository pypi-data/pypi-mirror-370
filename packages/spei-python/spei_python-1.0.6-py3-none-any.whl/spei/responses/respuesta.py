from typing import Type

from lxml import etree

from spei.requests.respuesta import XML_SCHEMA_NS
from spei.requests.respuesta import BodyElement as BodyElementP2P
from spei.requests.respuesta import EnvelopeElement as EnvelopeElementP2P
from spei.requests.respuesta import RespuestaElement as RespuestaElementP2P
from spei.resources import Respuesta
from spei.types import CategoriaOrdenPago


class RespuestaElement(object):
    def __new__(cls, mensaje_element, respuesta_cls: Type[Respuesta] = Respuesta):
        respuesta = mensaje_element.find('respuesta')
        categoria = mensaje_element.attrib['categoria']
        return respuesta_cls.parse_xml(respuesta, categoria)


class MensajeElement(object):
    def __new__(cls, respuesta):
        return etree.fromstring(  # noqa: S320
            bytes(respuesta.text, encoding='cp850'),
        )


class MensajeElementP2P(object):
    def __new__(cls, respuesta: str, categoria: CategoriaOrdenPago):
        qname = etree.QName(XML_SCHEMA_NS, 'type')

        mensaje = etree.Element(
            'mensaje',
            {qname: 'mensaje'},
            categoria=categoria,
        )
        mensaje.append(respuesta)
        return mensaje


class RootElement(object):
    def __new__(cls, body):
        return body.find('{http://www.praxis.com.mx/}respuesta')


class BodyElement(object):
    def __new__(cls, mensaje):
        return mensaje.find(
            '{http://schemas.xmlsoap.org/soap/envelope/}Body',
        )


class RespuestaResponse(object):
    def __new__(cls, respuesta):
        mensaje = etree.fromstring(respuesta)  # noqa: S320
        return RespuestaElement(MensajeElement(RootElement(BodyElement((mensaje)))))


class RespuestaResponseP2P(object):
    def __init__(self, respuesta, categoria):
        self.tree = EnvelopeElementP2P(
            BodyElementP2P(
                RespuestaElementP2P(
                    MensajeElementP2P(respuesta, categoria),
                ),
            ),
        )

    def __bytes__(self):
        return etree.tostring(self.tree, encoding='utf-8')

    def __str__(self):
        return etree.tostring(self.tree, encoding='unicode')
