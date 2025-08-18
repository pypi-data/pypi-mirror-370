from enum import StrEnum


class PaymentProviderName(StrEnum):
    YOOKASSA = "YooKassa"
    YANDEXPAY = "YandexPay"


class OrderStatus(StrEnum):
    NEW = "new"
    CANCELED = "canceled"
    PAID = "paid"
    REFUNDED = "refunded"


class PaymentMethodName(StrEnum):
    CARD = "bank_card"
    MIR = "mir_pay"
    SBER = "sber_pay"
    TPAY = "t_pay"
    SBP = "sbp"
    YOOMONEY = "yoo_money"


class CardNetwork(StrEnum):
    AMEX = "AMEX"
    DISCOVER = "DISCOVER"
    JCB = "JCB"
    MASTERCARD = "MASTERCARD"
    MAESTRO = "MAESTRO"
    VISAELECTRON = "VISAELECTRON"
    VISA = "VISA"
    MIR = "MIR"
    UNIONPAY = "UNIONPAY"
    UZCARD = "UZCARD"
    HUMOCARD = "HUMOCARD"
    UNKNOWN = "UNKNOWN"
    UNDEFINED = "UNDEFINED"


class PaymentStatus(StrEnum):
    CREATED = "created"
    PENDING = "pending"
    FAILED = "failed"
    DECLINED = "declined"
    SUCCESS = "success"
    REFUNDED = "refunded"


class RefundStatus(StrEnum):
    CREATED = "created"
    PENDING = "pending"
    UNKNOWN = "unknown"
    FAILED = "failed"
    DECLINED = "declined"
    SUCCESS = "success"
