from typing import Type

from lxml import etree

from spei.resources import Orden


class OrdenPagoElement(object):
    def __new__(cls, mensaje_element, orden_cls: Type[Orden] = Orden):
        ordenpago = mensaje_element.find('ordenpago')
        categoria = mensaje_element.attrib['categoria']
        return orden_cls.parse_xml(ordenpago, categoria)


class MensajeElement(object):
    def __new__(cls, ordenpago):
        return etree.fromstring(  # noqa: S320
            bytes(ordenpago.text.strip(), encoding='cp850'),
        )


class RootElement(object):
    def __new__(cls, body):
        return body.find('{http://www.praxis.com.mx/}ordenpago')


class BodyElement(object):
    def __new__(cls, mensaje):
        return mensaje.find(
            '{http://schemas.xmlsoap.org/soap/envelope/}Body',
        )


class OrdenResponse(object):
    def __new__(cls, orden):
        mensaje = etree.fromstring(  # noqa: S320
            bytes(orden, encoding='cp850'),
        )
        return OrdenPagoElement(MensajeElement(RootElement(BodyElement(mensaje))))
