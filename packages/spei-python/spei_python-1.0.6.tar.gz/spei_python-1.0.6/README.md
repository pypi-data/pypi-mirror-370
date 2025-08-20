[![wemake-python-styleguide](https://img.shields.io/badge/style-wemake-000000.svg)](https://github.com/wemake-services/wemake-python-styleguide)

spei-python
===========

A library for accessing the SPEI API and SICE API for python.


## Installation
Use the package manager [poetry](https://pypi.org/project/poetry/) to install.

    poetry install spei-python

## Usage
Use our client to send orders to SPEI.
```python
from spei.client import BaseClient

client = BaseClient(
    host='http://karpay-beta.intfondeadora.app',
    username='karpay',
    password='password',
    priv_key='private_key',
    priv_key_passphrase='passphrase',
)
```

Use our client to send orders to SICE.
```python
from spei.sice import BaseClient

client = BaseClient(
    host='https://172.30.3.204:8443',
)
```

## Methods
- [registra_orden](/spei/client.py#58)
- [registra_cda](/spei/sice.py#25)

## Resources
There are four main resources.

- [Orden](spei/resources/orden.py) our abstraction of order, this goes through SPEI as XML.
- [Respuesta](spei/resources/respuesta.py) our abstraction of received SPEI messages and response to SPEI orders.
- [CDA](spei/resources/cda.py) our abstraction of cda, this goes through SICE as XML.
- [Acuse](spei/resources/acuse.py) our abstraction of received SICE messages and confirmation message to SICE.

## Types
- [TipoPagoOrdenPago](/spei/types.py#6) Order payment type.
- [TipoOrdenPago](/spei/types.py#33) Order type.
- [TipoCuentaOrdenPago](/spei/types.py#38) Account type.
- [PrioridadOrdenPago](/spei/types.py#58) Order priority.
- [CategoriaOrdenPago](/spei/types.py#63) Order Category.
- [EstadoOrdenPago](/spei/types.py#76) Order status.
- [ClaveOrdenanteOrdenPago](/spei/types.py#83) Root Institution Code.
- [FolioOrdenPago](/spei/types.py#87) Order invoice identifier.
- [MedioEntregaOrdenPago](/spei/types.py#91) Order transmission method.
- [TopologiaOrdenPago](/spei/types.py#107) Order notification method.

## Requests
These are used to perform requests to karpay using our resources.
- [OrdenRequest](spei/requests/orden.py) Maps an existing orden to XML.
- [RespuestaRequest](spei/requests/respuesta.py) Maps an existing respuesta to XML.
- [CDARequest](spei/requests/cda.py) Maps an existing CDA to XML.

## Responses
These are used to map karpay results to our resources.
- [AcuseResponse](spei/responses/orden.py) Maps a acuse XML to our CDA resource.
- [RespuestaResponse](spei/responses/respuesta.py) Maps a respuesta XML to our Response resource.

## Errors
Available [errors](/spei/errors.py) messages from Karpay.

These errors are included inside respuesta.

## Test
Tested with [mamba](https://mamba-framework.readthedocs.io/en/latest/), install poetry dev packages and then run tests.

    poetry run make test

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)

## Checksum Generator
This repo includes a utility to generate [firma digital aplicada](https://www.notion.so/fondeadoraroot/Algoritmo-de-Firma-e-Karpay-SPEI-02e6c25b7c5943bea054ae37c9605bdc)

```sh
python bin/generate_checksum.py bin/message.json
```
