from typing import Any, Optional

from lxml import etree
from pydantic import BaseModel, ConfigDict

from spei.types import CategoriaOrdenPago


class Mensaje(BaseModel):
    categoria: Optional[CategoriaOrdenPago] = None
    ordenpago: Optional[Any] = None
    respuesta: Optional[Any] = None
    ensesion: Optional[Any] = None
    model_config = ConfigDict(extra='allow')

    @classmethod
    def parse_xml(cls, mensaje: bytes):  # noqa: WPS210
        encoding = 'cp850'
        if b'ENSESION' in mensaje:
            encoding = 'utf-8'
            mensaje = (
                mensaje.decode('latin1').replace('&amp;', '&amp;amp;').encode(encoding)
            )
        mensaje_parsed: etree.Element = etree.fromstring(mensaje)  # noqa: S320
        body = mensaje_parsed.find(
            '{http://schemas.xmlsoap.org/soap/envelope/}Body',
        )
        ordenpago = body.find('{http://www.praxis.com.mx/}ordenpago')
        respuesta = body.find('{http://www.praxis.com.mx/}respuesta')

        if ordenpago is not None:
            element = etree.fromstring(  # noqa: S320
                bytes(ordenpago.text.strip(), encoding=encoding),
            )
            categoria = element.attrib['categoria']

            if categoria == CategoriaOrdenPago.ensesion:
                return cls(
                    categoria=categoria,
                    ensesion=element,
                )

            return cls(categoria=categoria, ordenpago=element)

        if respuesta is not None:
            element = etree.fromstring(  # noqa: S320
                bytes(respuesta.text.strip(), encoding=encoding),
            )
            categoria = element.attrib['categoria']
            return cls(categoria=categoria, respuesta=element)

        raise NotImplementedError
