# RegistraOrden
Create a new order in SPEI as XML based on [mensaje.xsd](https://drive.google.com/file/d/1bf28_MmSRywfCvIwcPO2IyaEOwPFvKlJ/view?usp=sharing) and returns a response XML.

**op_fecha_oper** - int **_required_** This should match karpay date of operation.

**op_ins_clave_ord** - digits(5, 5) **_required_** Origin account institution code.

**op_folio** - str **_required_** This should be -1 when category is CARGAR_ODP.

**op_monto** - str **_required_** Order amount as **string**.

**op_tp_clave** [int](/spei/types.py#4) **_required_** This should be **1** for third to third payments.

**op_cve_rastreo** - str **_required_** Unique transfer tracking code. (?)

**op_estado** - [int](/spei/types.py#74)  **_required_** Order status.

**op_tipo_orden** - [int](/spei/types.py#31) **_required_** Order type.

**op_prioridad** - [int](/spei/types.py#56) **_required_** Order priority.

**op_me_clave** - [int](/spei/types.py#89) **_required_** Order transmission method

**op_topologia** - str **_required_** Order SPEI notification mechanism.

**op_usu_clave** - str **_required_** Username who generated the order and should be defined in karpay catalog.

**op_fecha_cap** - int Order captured timestamp inside E-Karpay (yyyymmdd)

Optional depending on order type

**op_clave** - int Unique E-Karpay identifier

**op_nom_ord** - str Origin full name.

**op_tc_clave_ord** - [int](/spei/types.py#36) Origin account type.

**op_cuenta_ord** - int Origin account number

**op_rfc_curp_ord** - str Origin identification number

**op_nom_ben** - str  Beneficiary full name

**op_tc_clave_ben** - [int](/spei/types.py#36) Beneficiary account type

**op_cuenta_ben** - str Beneficiary Account number

**op_rfc_curp_ben** str Beneficiary identification number

**op_ins_clave_ben** - digits(5, 5) **_required_** Beneficiary account institution code.

**op_nom_ben_2** - str Additional beneficiary name

**op_tc_clave_ben_2** - [int](/spei/types.py#36) Additional beneficiary account type

**op_cuenta_ben_2** - str Additional beneficiary Account number

**op_rfc_curp_ben_2** - str Additional beneficiary identification number

**op_concepto_pago** - str Used when op_tp_clave requires a concept of maximum length of 210.

**op_concepto_pag_2** - str Used when op_tp_clave requires a concept of maximum length of 40.

**op_iva** float - Order correspinding taxes (if applicable)

**op_ref_numerica** str Order reference number

**op_ref_cobranza** - str Only used for root account payments reference.

**op_to_clave** - [int](/spei/types.py#4) Operation type that the ordering client wishes to settle with the bank.

**op_cd_clave** - [int] Devolution cause

**op_folio_servidor** - int Server invoice number

**op_usu_autoriza** - str Order's user authorization name

**op_err_clave** - [int](/spei/errors.py) Order error code

**op_razon_rechazo** - str Order rejection description

**op_hora_cap** - int Order captured hour timestamp (hhmmss)

**op_hora_liq_bm** - int Order settlement hour timestamp on BANXICO (hhmmss)

**op_hora_liq_sist** - int Order settlement hour timestamp on E-Karpay

**op_cde** - string ODP Original encryption code

**op_cuenta_dev** - string Property only used by scotiaBank

**op_hora_lecturaHost** - int Order read at hour timestamp on E-Karpay (hhmmss)

**op_hora_insercion** - int Order saved at hour timestamp on E-Karpay (hhmmss)

**hr_deposito_acuse_banxico** - int  Order settled at hour timestamp on E-Karpay (hhmmss)

**paq_folio** - int Invoice package number

**ah_ar_clave** - int Area code

**emp_clave** - int Company code

**paq_folio_ori** - int Original invoice package number

**op_folio_ori** - int Original invoice number

**op_rastreo_ori** - str Original tracking code

**op_monto_intereses** - float Gross order amount

**op_info_factura** - str Bill information

**op_indica_ben_rec** - str Beneficiary name

**op_firma_dig** - str Order signature generated through algorithm.

<--- CODI --->

**op_num_cel_ord** - int Origin phone number

**op_digito_ver_ord** - int Origin verification digit number

**op_num_cel_ben** - int Beneficiary phone number

**op_digito_ver_ben** - int Beneficiary verification digit number

**op_folio_codi** - str Digital invoice scheme

**op_comision_trans** - int Operation comission

**op_monto_comision** - float Comission Amount

**op_cert_comer_env** - int certificate serial number

**op_digito_ver_comer** - int Merchant verification digit number


## Order Types
You must use one of our available order types.

- [Tercero A Tercero](/spei/resources/orden.py#107)

## Request

```python
orden = client.registra_orden({
    'op_fecha_oper': 20230309,
    'op_folio': 1
    'op_ins_clave_ord': 90699,
    'op_monto': 1000,
    'op_tp_clave': 1,
    'op_cve_rastreo': 'TERCERO001',
    'op_estado': 'A',
    'op_tipo_orden': 'E',
    'op_prioridad': 0,
    'op_me_clave': 2,
    'op_topologia': 'V'
    'op_usu_clave': 'ADMIN',
    'op_ins_clave_ord': '90699',
    'op_nom_ord': 'ORDENANTE',
    'op_tc_clave_ord': '40',
    'op_cuenta_ord': '646731258600008291',
    'op_rfc_curp_ord': 'HEHJ891212MOCRRB04',
    'op_nom_ben': 'BENEFICIARIO',
    'op_tc_clave_ben': '40',
    'op_cuenta_ben': '519526509743147521',
    'op_concepto_pag_2': 'servicios',
    'op_ref_numerica': '567',
    'op_firma_dig': 'FIRMADIGITAL001'
})
```

The actual payload will look something like this.

[Orden XML](../tests/fixtures/orden.xml)

## Response
We **must** always return XML as defined in [respuesta](/spei/resources/respuesta.py#8).

[Respuesta XML](../tests/fixtures/respuesta.xml)
