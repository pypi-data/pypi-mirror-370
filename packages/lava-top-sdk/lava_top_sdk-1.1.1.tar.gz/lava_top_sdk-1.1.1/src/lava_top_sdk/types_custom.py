from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


# Enums based on API schemas
class Currency(str, Enum):
    RUB = "RUB"
    USD = "USD"
    EUR = "EUR"


class PaymentMethod(str, Enum):
    BANK131 = "BANK131"
    UNLIMINT = "UNLIMINT"
    PAYPAL = "PAYPAL"
    STRIPE = "STRIPE"


class Periodicity(str, Enum):
    ONE_TIME = "ONE_TIME"
    MONTHLY = "MONTHLY"
    PERIOD_90_DAYS = "PERIOD_90_DAYS"
    PERIOD_180_DAYS = "PERIOD_180_DAYS"
    PERIOD_YEAR = "PERIOD_YEAR"


class Language(str, Enum):
    EN = "EN"
    RU = "RU"
    ES = "ES"


class FeedItemType(str, Enum):
    POST = "POST"
    PRODUCT = "PRODUCT"


class ProductType(str, Enum):
    COURSE = "COURSE"
    DIGITAL_PRODUCT = "DIGITAL_PRODUCT"
    BOOK = "BOOK"
    GUIDE = "GUIDE"
    SUBSCRIPTION = "SUBSCRIPTION"
    AUDIO = "AUDIO"
    MODS = "MODS"
    CONSULTATION = "CONSULTATION"


class FeedVisibility(str, Enum):
    ALL = "ALL"
    ONLY_VISIBLE = "ONLY_VISIBLE"
    ONLY_HIDDEN = "ONLY_HIDDEN"


class InvoiceStatus(str, Enum):
    NEW = "new"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SUBSCRIPTION_ACTIVE = "subscription-active"
    SUBSCRIPTION_EXPIRED = "subscription-expired"
    SUBSCRIPTION_CANCELLED = "subscription-cancelled"
    SUBSCRIPTION_FAILED = "subscription-failed"


class InvoiceType(str, Enum):
    ONE_TIME = "ONE_TIME"
    RECURRING = "RECURRING"


class SubscriptionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"


class WebhookEventType(str, Enum):
    PAYMENT_SUCCESS = "payment.success"
    PAYMENT_FAILED = "payment.failed"
    SUBSCRIPTION_RECURRING_PAYMENT_SUCCESS = "subscription.recurring.payment.success"
    SUBSCRIPTION_RECURRING_PAYMENT_FAILED = "subscription.recurring.payment.failed"
    SUBSCRIPTION_CANCELLED = "subscription.cancelled"


# UTM and Client Data
class ClientUtm(BaseModel):
    """UTM покупки"""

    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    utm_term: Optional[str] = None
    utm_content: Optional[str] = None


# Core API Request/Response Types
class InvoiceRequestDto(BaseModel):
    """Описание покупки контента"""

    email: str
    offerId: str
    periodicity: Optional[Periodicity] = None
    currency: Currency
    paymentMethod: Optional[PaymentMethod] = None
    buyerLanguage: Optional[Language] = None
    clientUtm: Optional[ClientUtm] = None


class AmountTotalDto(BaseModel):
    """Продажи в валюте"""

    currency: Currency
    amount: float


class InvoicePaymentParamsResponse(BaseModel):
    """Описание созданного контракта"""

    id: str
    status: InvoiceStatus
    amountTotal: AmountTotalDto
    paymentUrl: Optional[str] = None


class PriceDto(BaseModel):
    """Сумма"""

    amount: Optional[float] = None
    currency: Currency
    periodicity: Optional[Periodicity] = None


class OfferResponse(BaseModel):
    """Предложения для покупки продукта"""

    id: str
    name: Optional[str] = None
    description: Optional[str] = None
    prices: List[PriceDto]
    recurrent: Optional[str] = None


class ProductItemResponse(BaseModel):
    """Продукт"""

    id: str
    title: Optional[str] = None
    description: Optional[str] = None
    type: ProductType
    offers: Optional[List[OfferResponse]] = None


class ProductsResponse(BaseModel):
    """Ответ со списком продуктов"""

    items: List[ProductItemResponse]
    nextPage: Optional[str] = None


# Invoice Response Types
class ReceiptResponse(BaseModel):
    """Чек"""

    amount: float
    currency: Currency
    fee: float


class BuyerResponse(BaseModel):
    """Покупатель"""

    email: str
    cardMask: Optional[str] = None


class ProductResponse(BaseModel):
    """Информация о продукте в инвойсе"""

    name: str
    offer: str


class ParentInvoiceResponse(BaseModel):
    """Родительский контракт"""

    id: str


class SubscriptionDetails(BaseModel):
    """Детали подписки"""

    expiredAt: Optional[datetime] = None
    terminatedAt: Optional[datetime] = None
    cancelledAt: Optional[datetime] = None


class InvoiceClientUtm(BaseModel):
    """UTM для инвойса"""

    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    utm_term: Optional[str] = None
    utm_content: Optional[str] = None


class InvoiceResponseV2(BaseModel):
    """Полная информация об инвойсе"""

    id: str
    type: InvoiceType
    datetime: datetime
    status: InvoiceStatus
    receipt: ReceiptResponse
    buyer: BuyerResponse
    product: ProductResponse
    parentInvoice: Optional[ParentInvoiceResponse] = None
    subscriptionStatus: Optional[SubscriptionStatus] = None
    subscriptionDetails: Optional[SubscriptionDetails] = None
    clientUtm: Optional[InvoiceClientUtm] = None


# Webhook Types
class WebhookBuyer(BaseModel):
    """Информация о покупателе в вебхуке"""

    email: str


class PurchaseWebhookLog(BaseModel):
    """Тело вебхука, отправляемого партнёру"""

    eventType: WebhookEventType
    product: Dict[str, Any]  # {id: str, title: str}
    contractId: str
    parentContractId: Optional[str] = None
    buyer: WebhookBuyer
    amount: float
    currency: Currency
    status: InvoiceStatus
    timestamp: datetime
    clientUtm: Optional[ClientUtm] = None
    errorMessage: Optional[str] = None


class WebhookEvent(BaseModel):
    """Событие вебхука"""

    type: WebhookEventType
    data: Dict[str, Any]
    created_at: datetime


# Configuration Types
class WebhookConfig(BaseModel):
    """Конфигурация вебхука"""

    url: str
    secret: str
    events: List[str]


class Config(BaseModel):
    """Конфигурация клиента"""

    api_key: str
    api_url: str
    env: Optional[str] = "production"  # sandbox или production
    webhook_config: Optional[WebhookConfig] = None
    timeout: int = 30
    max_retries: int = 3


# Error Response
class ErrorResponse(BaseModel):
    """Тело ошибки"""

    error: str
    details: Optional[Dict[str, str]] = None
    timestamp: datetime


# Donation Response
class DonateResponse(BaseModel):
    """Тело доната"""

    url: str


# Legacy types for backward compatibility (deprecated)
class PaymentCreateRequest(BaseModel):
    """Deprecated: use InvoiceRequestDto instead"""

    offer_id: str
    email: str
    currency: Currency
    periodicity: Optional[Periodicity] = None
    payment_method: Optional[PaymentMethod] = None
    buyer_language: Optional[Language] = None
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    utm_term: Optional[str] = None
    utm_content: Optional[str] = None


class PaymentUpdateRequest(BaseModel):
    """Deprecated"""

    status: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


# Aliases for compatibility
Product = ProductItemResponse
Payment = InvoiceResponseV2
PaymentInitResponse = InvoicePaymentParamsResponse
PaymentStatus = InvoiceStatus
PaymentInitAmount = AmountTotalDto
