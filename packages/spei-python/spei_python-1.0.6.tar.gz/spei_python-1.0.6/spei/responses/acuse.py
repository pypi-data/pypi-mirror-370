from lxml import etree

from spei.resources import Acuse


class RespuestaElement(object):
    def __new__(cls, body):
        return body.find(
            '{http://www.praxis.com.mx/EnvioCda/}generaCdaResponse',
        )


class BodyElement(object):
    def __new__(cls, mensaje):
        return mensaje.find(
            '{http://schemas.xmlsoap.org/soap/envelope/}Body',
        )


class AcuseResponse(object):
    def __new__(cls, acuse, acuse_cls=Acuse):
        mensaje = etree.fromstring(acuse)  # noqa: S320
        mensaje_element = RespuestaElement(BodyElement((mensaje)))
        return acuse_cls.parse_synchronous_xml(mensaje_element)
