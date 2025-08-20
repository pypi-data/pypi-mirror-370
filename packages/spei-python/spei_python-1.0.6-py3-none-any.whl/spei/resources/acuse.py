from typing import Any, Optional, Union

from lxml import etree
from pydantic import BaseModel, ConfigDict

from spei.errors.sice import CodigoErrorAcuseBanxico, CodigoErrorAcuseServidor
from spei.types.sice import CodigoRespuestaAcuse, TipoRespuestaAcuse
from spei.utils import to_snake_case  # noqa: WPS347


class ResultadoBanxico(BaseModel):
    codigo: Optional[CodigoErrorAcuseBanxico] = None
    descripcion: str = 'ND'
    model_config = ConfigDict(use_enum_values=True)


class ResultadoServidor(BaseModel):
    codigo: Union[CodigoErrorAcuseServidor, CodigoRespuestaAcuse]
    descripcion: str = 'ND'
    model_config = ConfigDict(use_enum_values=True)


class MensajeRespuesta(BaseModel):
    tipo_respuesta: TipoRespuestaAcuse
    respuesta: Any = None

    @classmethod
    def parse_xml(cls, mensaje):
        root_element = etree.fromstring(mensaje)  # noqa: S320

        body_element = root_element.find(
            '{http://schemas.xmlsoap.org/soap/envelope/}Body',
        )

        respuesta_element = body_element.find(
            '{http://cep.fyg.com/}respuestaCDA',
        )

        xml_element = respuesta_element.find('xml')

        respuesta = etree.fromstring(  # noqa: S320
            bytes(xml_element.text, encoding='utf-8'),
        )
        respuesta_element = respuesta.xpath('//*[local-name()="mensajeRespuestaCDA"]')[
            0
        ]  # noqa: E501
        tipo_respuesta = respuesta_element.attrib['tipoRespuesta']

        return cls(
            tipo_respuesta=tipo_respuesta,
            respuesta=respuesta_element,
        )


class Acuse(BaseModel):
    cda_id: int
    mensaje_id: Any = None
    tipo_respuesta: TipoRespuestaAcuse
    resultado_enlace_cep: ResultadoServidor
    resultado_banxico: Optional[ResultadoBanxico] = None
    model_config = ConfigDict(use_enum_values=True)

    @classmethod
    def parse_synchronous_xml(cls, mensaje_element):
        tipo_respuesta = mensaje_element.attrib['tipoRespuesta']
        acuse_element = mensaje_element.find(
            '{http://www.praxis.com.mx/EnvioCda/}acuseCda',
        )  # noqa: E501
        cda_data = cls._find_mensaje_attributes(acuse_element, tipo_respuesta)
        resultado_element = acuse_element.find(
            '{http://www.praxis.com.mx/EnvioCda/}resultadoEnlaceCep',
        )  # noqa: E501
        codigo = resultado_element.find('{http://www.praxis.com.mx/EnvioCda/}codigo')
        descripcion = resultado_element.find(
            '{http://www.praxis.com.mx/EnvioCda/}descripcion',
        )  # noqa: E501
        enlace_cep_data = {
            'codigo': codigo.text,
            'descripcion': descripcion.text,
        }
        return cls._build_acuse(acuse_element, cda_data, enlace_cep_data)

    def build_xml(self):
        if self.mensaje_id:
            acuse = etree.Element(
                'acuse',
                idCda=str(self.cda_id),
                idMensaje=str(self.mensaje_id),
            )
        else:
            acuse = etree.Element(
                'acuse',
                idCda=str(self.cda_id),
            )

        etree.SubElement(
            acuse,
            'resultadoEnlaceCep',
            codigo=self.resultado_enlace_cep.codigo,
            descripcion=self.resultado_enlace_cep.descripcion,
        )

        if not self.resultado_banxico:
            etree.SubElement(
                acuse,
                'resultadoBanxico',
            )
            return acuse

        etree.SubElement(
            acuse,
            'resultadoBanxico',
            codigo=self.resultado_banxico.codigo,
            descripcion=self.resultado_banxico.descripcion,
        )

        return acuse

    @classmethod
    def parse_xml(cls, acuse_element, tipo_respuesta):
        cda_data = cls._find_mensaje_attributes(acuse_element, tipo_respuesta)
        enlace_cep_data = cls._find_enlace_cep_attributes(acuse_element)
        banxico_data = cls._find_banxico_attributes(acuse_element)

        return cls._build_acuse(acuse_element, cda_data, enlace_cep_data, banxico_data)

    @classmethod
    def _find_enlace_cep_attributes(cls, acuse_element):
        resultado_element = acuse_element.find('resultadoEnlaceCep')
        return {
            'codigo': resultado_element.attrib['codigo'],
            'descripcion': resultado_element.attrib['descripcion'],
        }

    @classmethod
    def _find_banxico_attributes(cls, acuse_element):
        resultado_element = acuse_element.find('resultadoBanxico')
        return {
            'codigo': resultado_element.attrib['codigo'],
            'descripcion': resultado_element.attrib['descripcion'],
        }

    @classmethod
    def _find_mensaje_attributes(cls, acuse_element, tipo_respuesta):
        return {
            'tipo_respuesta': tipo_respuesta,
            'cda_id': acuse_element.attrib['idCda'],
            'mensaje_id': acuse_element.get('idMensaje'),
        }

    @classmethod
    def _build_acuse(cls, acuse_element, cda_data, enlace_cep_data, banxico_data=None):
        for element in acuse_element.getchildren():
            localname = etree.QName(element).localname
            tag = to_snake_case(localname)
            if tag == 'resultado_enlace_cep':
                cda_data[tag] = ResultadoServidor(**enlace_cep_data)
                continue
            if tag == 'resultado_banxico':
                cda_data[tag] = ResultadoBanxico(**banxico_data)
                continue
            if tag in cls.model_fields:
                cda_data[tag] = element.text

        return cls(**cda_data)
