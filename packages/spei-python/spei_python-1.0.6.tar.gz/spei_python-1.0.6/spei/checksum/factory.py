from spei.checksum.generator import (
    ChecksumGenerator,
    ChecksumGeneratorBeneficiary,
    ChecksumGeneratorBeneficiaryAndAdditionalBeneficiary,
    ChecksumGeneratorDefault,
    ChecksumGeneratorEveryField,
    ChecksumGeneratorIndirect,
    ChecksumGeneratorIndirectToParticipant,
    ChecksumGeneratorOrigin,
    ChecksumGeneratorOriginAndBeneficiary,
    ChecksumGeneratorRemittance,
)
from spei.checksum.types import (
    INDIRECT_PAYMENT_TYPES,
    PAYMENT_TYPES_WITH_BENEFICIARY_ACCOUNT,
    PAYMENT_TYPES_WITH_BENEFICIARY_AND_ADDITIONAL_BENEFICIARY_ACCOUNT,
    PAYMENT_TYPES_WITH_DEFAULT_FIELDS,
    PAYMENT_TYPES_WITH_ORIGIN_ACCOUNT,
    PAYMENT_TYPES_WITH_ORIGIN_AND_BENEFICIARY_ACCOUNT,
    PAYMENT_TYPES_WITH_ORIGIN_BENEFICIARY_AND_ADDITIONAL_BENEFICIARY_ACCOUNT,
    REMITTANCE_PAYMENT_TYPES,
)
from spei.types import TipoPagoOrdenPago


def get_checksum_generator(payment_type: TipoPagoOrdenPago) -> ChecksumGenerator:  # noqa: C901, WPS212, E501
    if payment_type in PAYMENT_TYPES_WITH_DEFAULT_FIELDS:
        return ChecksumGeneratorDefault()

    if payment_type in PAYMENT_TYPES_WITH_ORIGIN_ACCOUNT:
        return ChecksumGeneratorOrigin()

    if payment_type in PAYMENT_TYPES_WITH_BENEFICIARY_ACCOUNT:
        return ChecksumGeneratorBeneficiary()

    if payment_type in PAYMENT_TYPES_WITH_ORIGIN_AND_BENEFICIARY_ACCOUNT:
        return ChecksumGeneratorOriginAndBeneficiary()

    if payment_type in PAYMENT_TYPES_WITH_BENEFICIARY_AND_ADDITIONAL_BENEFICIARY_ACCOUNT:  # noqa: E501
        return ChecksumGeneratorBeneficiaryAndAdditionalBeneficiary()

    if payment_type in REMITTANCE_PAYMENT_TYPES:
        return ChecksumGeneratorRemittance()

    if payment_type in INDIRECT_PAYMENT_TYPES:
        return ChecksumGeneratorIndirect()

    if payment_type == TipoPagoOrdenPago.tercero_indirecto_a_participante:
        return ChecksumGeneratorIndirectToParticipant()

    if payment_type in PAYMENT_TYPES_WITH_ORIGIN_BENEFICIARY_AND_ADDITIONAL_BENEFICIARY_ACCOUNT:  # noqa: E501
        return ChecksumGeneratorEveryField()

    raise NotImplementedError
