from _typeshed import Incomplete
from enum import Enum

class OrderProcesses(str, Enum):
    without_payment: str
    tg_payment: str
    ton_payment: str
    life_pay: str

class PaymentTypes(str, Enum):
    manual_payment_request: str
    external_card_payment_provider: str
    crypto_ton: str
    xtr: str
    life_pay: str
    yookassa: str
    tkassa: str

class ShopStatuses(str, Enum):
    deploying: str
    active: str
    unavailable: str
    deleted: str

class TaskStatuses(str, Enum):
    pending: str
    expired: str
    completed: str

class ServiceNames(str, Enum):
    bot: str

class UserRoles(str, Enum):
    user: str
    admin: str
    shop_admin: str
    shop_manager: str

PAYMENTS_PROCESSES_MAPPING: Incomplete
