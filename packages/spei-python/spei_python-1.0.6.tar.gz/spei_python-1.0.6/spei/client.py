import base64
import logging

import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.hashes import SHA256

from spei import exceptions
from spei.checksum.factory import get_checksum_generator
from spei.errors import spei as errors
from spei.requests import OrdenRequest
from spei.resources import Orden, Respuesta
from spei.responses import RespuestaResponse

logger = logging.getLogger('spei')
logger.setLevel(logging.DEBUG)


class BaseClient(object):
    def __init__(
        self,
        priv_key,
        priv_key_passphrase,
        host,
        username,
        password,
        verify=False,
        http_client=requests,
        checksum_generator_factory=get_checksum_generator,
    ):
        self.priv_key = priv_key
        self.priv_key_passphrase = priv_key_passphrase or None
        self.host = host
        self.session = http_client.Session()
        self.session.headers.update(
            {
                'Content-Type': 'application/xml; charset=cp850',
                'User-Agent': 'Fondeadora/Karpay/v0.52.0',
            },
        )
        self.session.verify = verify
        self.session.auth = (username, password)

        if priv_key_passphrase:
            self.priv_key_passphrase = priv_key_passphrase.encode('ascii')

        self.pkey = serialization.load_pem_private_key(
            self.priv_key.encode('utf-8'),
            self.priv_key_passphrase,
            default_backend(),
        )

        self.checksum_generator_factory = checksum_generator_factory

    def registra_orden(
        self,
        orden_data,
        orden_cls=Orden,
        respuesta_response_cls=RespuestaResponse,
    ):
        checksum = self.generate_checksum(orden_data)
        orden = orden_cls(op_firma_dig=checksum, **orden_data)
        soap_request = OrdenRequest(orden).to_string()
        logger.info(soap_request)

        response = self.session.post(data=soap_request, url=self.host)
        logger.info(response.text)
        response.raise_for_status()

        respuesta = respuesta_response_cls(response.text)

        if respuesta.err_codigo != errors.GenericoCodigoError.exitoso:
            self._raise_error(respuesta)

        return respuesta

    def generate_checksum(self, message_data):
        orden = Orden(**message_data, op_firma_dig='')
        generator = self.checksum_generator_factory(orden.op_tp_clave)
        message_as_bytes = generator.format_data(orden)

        signed_message = self.pkey.sign(
            message_as_bytes,
            padding.PKCS1v15(),
            SHA256(),
        )

        return base64.b64encode(signed_message)

    def _raise_error(self, respuesta: Respuesta):
        if respuesta.err_codigo == errors.GenericoCodigoError.tipo_pago_invalido:
            raise exceptions.TipoPagoInvalidoError(respuesta)

        if (  # noqa: WPS337
            respuesta.err_codigo
            == errors.OtrosCodigoError.otros_fecha_operacion_incorrecta
        ):
            raise exceptions.FechaOperacionIncorrectaError(respuesta)

        raise exceptions.SPEIError(respuesta)
