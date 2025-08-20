from enum import Enum


class TipoPagoOrdenPago(str, Enum):
    devolucion_no_acreditada = '0'
    tercero_a_tercero = '1'
    tercero_a_ventanilla = '2'
    tercero_a_tercero_vostro = '3'
    tercero_a_participante = '4'
    participante_a_tercero = '5'
    participante_a_tercero_vostro = '6'
    participante_a_participante = '7'
    tercero_a_tercero_fsw = '8'
    tercero_a_tercero_vostro_fsw = '9'
    participante_a_tercero_fsw = '10'
    participante_a_tercero_vostro_fsw = '11'
    nomina = '12'
    pago_por_celular = '14'
    pago_factura = '15'
    devolucion_extemporanea_no_acreditada = '16'
    devolucion_acreditada = '17'
    devolucion_extemporanea_acreditada = '18'
    cobros_presenciales_de_una_ocasion = '19'
    cobros_no_presenciales_de_una_ocasion = '20'
    cobros_no_presenciales_recurrentes = '21'
    cobros_no_presenciales_a_nombre_de_tercero = '22'
    devolucion_especial_acreditada = '23'
    devolucion_extemporanea_especial_acreditada = '24'
    tercero_a_tercero_fsw_cls = '25'
    tercero_a_tercero_vostro_fsw_cls = '26'
    participante_a_tercero_fsw_cls = '27'
    participante_a_tercero_vostro_fsw_cls = '28'
    participante_a_participante_fsw_cls = '29'
    tercero_indirecto_a_tercero = '30'
    tercero_indirecto_a_participante = '31'
    presencial_de_una_ocasion_indirecto = '32'
    no_presencial_de_una_ocasion_indirecto = '33'
    no_presencial_recurrente_indirecto = '34'
    remesa_saliente = '35'
    remesa_entrante = '36'


class TipoOrdenPago(str, Enum):
    envio = 'E'
    recepcion = 'R'


class TipoCuentaOrdenPago(str, Enum):
    inexsitente = '-1'
    desconocida = '0'
    desconocida_1 = '1'
    desconocida_2 = '2'
    tarjeta_debito = '3'
    cuenta_vostro = '4'
    custodia_de_valores = '5'
    cuenta_vostro_1 = '6'
    cuenta_vostro_2 = '7'
    cuenta_vostro_3 = '8'
    cuenta_vostro_4 = '9'
    telefono = '10'
    descripcion_11 = '11'
    clabe = '40'
    cuenta_subvostro_1 = '41'
    cuenta_subvostro_2 = '42'
    horario = '43'


class PrioridadOrdenPago(str, Enum):
    normal = 0
    alta = 1


class CategoriaOrdenPago(str, Enum):
    unknown = ''
    ensesion = 'ENSESION'
    respuesta = 'RESPUESTA'
    cargar_odp = 'CARGAR_ODP'
    cargar_odp_respuesta = 'CARGAR_ODP_RESPUESTA'
    odps_liquidadas_cargos = 'ODPS_LIQUIDADAS_CARGOS'
    odps_liquidadas_cargos_respuesta = 'ODPS_LIQUIDADAS_CARGOS_RESPUESTA'
    odps_liquidadas_abonos = 'ODPS_LIQUIDADAS_ABONOS'
    odps_liquidadas_abonos_respuesta = 'ODPS_LIQUIDADAS_ABONOS_RESPUESTA'
    odps_canceladas_local = 'ODPS_CANCELADAS_LOCAL'
    odps_canceladas_local_respuesta = 'ODPS_CANCELADAS_LOCAL_RESPUESTA'
    odps_canceladas_x_banxico = 'ODPS_CANCELADAS_X_BANXICO'
    odps_canceladas_x_banxico_respuesta = 'ODPS_CANCELADAS_X_BANXICO_RESPUESTA'
    ensesion_respuesta = 'ENSESION_RESPUESTA'
    cambio_conexion = 'AVISOCAMBIACONEC'


class EstadoOrdenPago(str, Enum):
    liquidada = 'LQ'
    liberada = 'L'
    capturada = 'C'
    autorizada = 'A'
    cancelada = 'CN'
    cancelada_local = 'CL'


class ClaveOrdenanteOrdenPago(int, Enum):
    AMU = 90699
    GEMELA = 699


class FolioOrdenPago(int, Enum):
    cargar_odp = -1


class MedioEntregaOrdenPago(str, Enum):
    local = '1'
    spei = '2'
    archivos = '3'
    devoluciones = '4'
    devoluciones_abono = '5'
    ce = '6'
    cei = '7'
    hsbc = '8'
    htvf = '9'
    dtp = '10'
    ifai = '13'
    swift = '17'
    nomina = '18'
    threats = '19'
    ghss = '20'
    nts = '21'
    continuous_linked_settlement = '23'
    depto = '24'
    another_ghss = '25'
    cp = '26'
    cpn = '27'
    opee = '28'
    pagos_md = '29'
    pib = '31'
    summit = '32'
    devext = '33'
    int = '99'


class TopologiaOrdenPago(str, Enum):
    notify_on_payment_settlement = 'V'
    notify_on_payment_instruction = 'T'


class TipoDevolucionOrdenPago(str, Enum):
    account_not_found = 1
    account_blocked = 2
    account_canceled = 3
    wrong_account_currency = 5
    account_number_does_not_belong = 6
    beneficiary_e_firma_revoked = 11
    beneficiary_unrecognized_payment = 13
    missing_required_data = 14
    invalid_payment_type = 15
    invalid_operation_type = 16
    invalid_account_type = 17
    requested_by_origin = 18
    invalid_character = 19
    authorized_limit_exceeded = 20
    deposit_limit_exceeded = 21
    phone_not_registered = 22
    additional_account_can_not_receive_payments = 23
    payment_information_malformed = 24
    missing_dispersion_instruction = 25
    resolution_not_approved_by_origin = 26
    invalid_optional_payment_type = 27
    codi_payment_notification_timeout = 28
    duplicated_tracking_code = 30
    origin_institution_certificate_expired = 31
