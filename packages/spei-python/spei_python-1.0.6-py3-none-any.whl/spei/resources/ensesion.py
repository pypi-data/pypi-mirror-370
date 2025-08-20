from typing import List

from pydantic import BaseModel

from spei import types
from spei.utils import to_snake_case  # noqa: WPS347


class Institucion(BaseModel):
    clave_cesif: int
    ins_nombre: str
    estado_receptivo: str
    estado_institucion: str

    @classmethod
    def parse_xml(cls, institucion_info):
        return cls(
            clave_cesif=institucion_info.find('clave_cesif').text,
            ins_nombre=institucion_info.find('ins_nombre').text,
            estado_receptivo=institucion_info.find('estado_receptivo').text,
            estado_institucion=institucion_info.find('estado_institucion').text,
        )


class Ensesion(BaseModel):
    categoria: types.CategoriaOrdenPago
    fecha_operacion_banxico: str
    inst_bancarias: List[Institucion]

    @classmethod
    def parse_xml(cls, mensaje_element):
        ensesion_element = mensaje_element.find('ensesion')

        ensesion_data = {
            'categoria': types.CategoriaOrdenPago.ensesion,
            'inst_bancarias': [],
        }

        for element in ensesion_element.getchildren():
            tag = to_snake_case(element.tag)
            if tag == 'inst_bancarias':
                instituciones = element.xpath('//institucion')
                for institucion_info in instituciones:
                    institucion = Institucion.parse_xml(institucion_info)
                    ensesion_data['inst_bancarias'].append(institucion)
                continue
            if tag in cls.model_fields:
                ensesion_data[tag] = element.text

        return cls(**ensesion_data)
