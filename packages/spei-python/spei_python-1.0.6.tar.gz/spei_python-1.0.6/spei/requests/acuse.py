from typing import List, Optional

from lxml import etree

from spei.resources import Acuse
from spei.types.sice import TipoRespuestaAcuse

SOAP_NS = 'http://schemas.xmlsoap.org/soap/envelope/'
XML_SCHEMA_NS = 'http://www.w3.org/2001/XMLSchema'
CEP_NS = 'http://cep.fyg.com/'
XML_XSD_NS = 'http://www.w3.org/2001/XMLSchema-instance'


class MensajeElement(object):
    def __new__(cls, acuses: List[Acuse], tipo_respuesta: TipoRespuestaAcuse):
        mensaje = etree.Element(
            'mensajeRespuestaCDA',
            tipoRespuesta=tipo_respuesta,
        )
        for acuse in acuses:
            mensaje.append(acuse.build_xml())
        return mensaje


class ReturnElement(object):
    def __new__(cls, mensaje_element):
        return_element = etree.Element(
            'return',
        )
        mensaje = etree.CDATA(etree.tostring(mensaje_element))
        return_element.text = mensaje
        return return_element


class RespuestaElement(object):
    def __new__(cls, return_element):
        respuesta = etree.Element(etree.QName(CEP_NS, 'respuestaCDAResponse'))
        respuesta.append(return_element)
        return respuesta


class BodyElement(object):
    def __new__(cls, respuesta):
        namespaces_uris = {
            'xsi': XML_SCHEMA_NS,
            'xsd': XML_XSD_NS,
        }
        body = etree.Element(etree.QName(SOAP_NS, 'Body'), nsmap=namespaces_uris)
        body.append(respuesta)
        return body


class EnvelopeElement(object):
    def __new__(cls, body):
        etree.register_namespace('soapenv', SOAP_NS)
        etree.register_namespace('cep', CEP_NS)
        ns_map = {'cep': CEP_NS, 'soapenv': SOAP_NS}
        envelope = etree.Element(etree.QName(SOAP_NS, 'Envelope'), nsmap=ns_map)
        envelope.append(body)
        return envelope


class AcuseRequest(object):
    def __new__(
        cls,
        tipo_respuesta: TipoRespuestaAcuse,
        acuses: Optional[List[Acuse]] = None,
        as_string=True,
    ):
        respuesta_element = RespuestaElement(
            ReturnElement(MensajeElement(acuses or [], tipo_respuesta)),
        )
        envelope = EnvelopeElement(BodyElement(respuesta_element))
        if not as_string:
            return envelope
        return etree.tostring(envelope, xml_declaration=True, encoding='utf-8')
