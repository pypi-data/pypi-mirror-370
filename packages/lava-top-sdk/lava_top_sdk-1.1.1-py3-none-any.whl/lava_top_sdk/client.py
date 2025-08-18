import json
import time
from typing import Optional, Dict, Any, List
import requests
from .types_custom import (
    InvoiceRequestDto,
    InvoicePaymentParamsResponse,
    InvoiceResponseV2,
    ProductItemResponse,
    Currency,
    PaymentMethod,
    Periodicity,
    Language,
    ClientUtm,
    FeedItemType,
    ProductType,
    FeedVisibility,
    DonateResponse,
    PurchaseWebhookLog,
)
from .config import Configuration
from .logger import Logger, LogLevel, LogFormat


class LavaClientConfig:
    """Configuration for LavaClient"""

    def __init__(
        self,
        api_key: str,
        env: str = "production",  # sandbox or production
        webhook_secret_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        logging_level: LogLevel = LogLevel.INFO,
        logging_format: LogFormat = LogFormat.TEXT,
    ):
        if not api_key or not api_key.strip():
            raise ValueError("API key cannot be empty")

        self.api_key = api_key
        self.env = env
        self.webhook_secret_key = webhook_secret_key
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.logging_level = logging_level
        self.logging_format = logging_format


class LavaClient:
    """
    Python client for LavaTop API

    Example usage:
        client = LavaClient(LavaClientConfig(
            api_key="your-api-key",
            env="sandbox"
        ))

        # Create invoice
        invoice = client.create_invoice(
            email="customer@example.com",
            offer_id="offer-uuid",
            currency=Currency.RUB
        )
    """

    def __init__(
        self,
        config: Optional[LavaClientConfig] = None,
        config_path: Optional[str] = None,
    ):
        if config:
            self.api_key = config.api_key
            self.env = config.env
            self.base_url = config.base_url or self._get_default_url(config.env)
            self.timeout = config.timeout
            self.max_retries = config.max_retries
            self.webhook_secret_key = config.webhook_secret_key
            self.logger = Logger(
                level=config.logging_level, format_type=config.logging_format
            )
        else:
            # Fallback to old configuration method
            configuration = Configuration(config_path)
            self.api_key = configuration.get_api_key()
            self.base_url = configuration.get_api_url()
            self.env = configuration.get_env()
            self.timeout = configuration.get_timeout()
            self.max_retries = configuration.get_max_retries()
            self.webhook_secret_key = None
            self.logger = Logger()

        self.session = requests.Session()
        self.session.headers.update(
            {"X-Api-Key": self.api_key, "Content-Type": "application/json"}
        )

    def _get_default_url(self, env: str) -> str:
        """Get default API URL based on environment"""
        if env == "sandbox":
            return "https://gate.sandbox.lava.top"  # Replace with actual sandbox URL
        return "https://gate.lava.top"

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic"""
        url = f"{self.base_url}{endpoint}"

        self.logger.debug(
            f"Making {method} request to {url}", {"data": data, "params": params}
        )

        for attempt in range(self.max_retries):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params,
                    timeout=self.timeout,
                )

                self.logger.debug(f"Response status: {response.status_code}")

                if response.status_code == 204:  # No content
                    return {}

                response.raise_for_status()
                result = response.json()

                self.logger.debug("Request successful", {"response": result})
                return result

            except Exception as e:
                if attempt == self.max_retries - 1:
                    self.logger.error(
                        f"Request failed after {self.max_retries} attempts: {str(e)}"
                    )
                    raise APIError("Request failed", {"error": str(e)}) from e

                # Exponential backoff
                wait_time = 2**attempt
                self.logger.warning(
                    f"Request failed, retrying in {wait_time}s",
                    {"attempt": attempt + 1},
                )
                time.sleep(wait_time)

    # Core API Methods

    def create_invoice(
        self,
        email: str,
        offer_id: str,
        currency: Currency,
        periodicity: Optional[Periodicity] = None,
        payment_method: Optional[PaymentMethod] = None,
        buyer_language: Optional[Language] = None,
        utm_source: Optional[str] = None,
        utm_medium: Optional[str] = None,
        utm_campaign: Optional[str] = None,
        utm_term: Optional[str] = None,
        utm_content: Optional[str] = None,
    ) -> InvoicePaymentParamsResponse:
        """
        Create invoice for content purchase

        Args:
            email: Customer email
            offer_id: Offer/product ID
            currency: Payment currency (RUB, USD, EUR)
            periodicity: Payment periodicity (ONE_TIME, MONTHLY, etc.)
            payment_method: Payment provider (BANK131, UNLIMINT, PAYPAL, STRIPE)
            buyer_language: Interface language (EN, RU, ES)
            utm_source: Traffic source
            utm_medium: Traffic channel
            utm_campaign: Campaign name
            utm_term: Keywords
            utm_content: Content variant

        Returns:
            Invoice payment parameters with ID, status, amount and payment URL
        """
        client_utm = None
        if any([utm_source, utm_medium, utm_campaign, utm_term, utm_content]):
            client_utm = ClientUtm(
                utm_source=utm_source,
                utm_medium=utm_medium,
                utm_campaign=utm_campaign,
                utm_term=utm_term,
                utm_content=utm_content,
            )

        request_data = InvoiceRequestDto(
            email=email,
            offerId=offer_id,
            currency=currency,
            periodicity=periodicity,
            paymentMethod=payment_method,
            buyerLanguage=buyer_language,
            clientUtm=client_utm,
        )

        self.logger.info(
            "Creating invoice",
            {"email": email, "offer_id": offer_id, "currency": currency.value},
        )

        response = self._make_request(
            "POST", "/api/v2/invoice", data=request_data.model_dump()
        )
        result = InvoicePaymentParamsResponse(**response)

        self.logger.info("Invoice created successfully", {"invoice_id": result.id})
        return result

    def create_one_time_payment(
        self,
        email: str,
        offer_id: str,
        currency: Currency,
        payment_method: Optional[PaymentMethod] = None,
        buyer_language: Optional[Language] = None,
        utm_source: Optional[str] = None,
        utm_medium: Optional[str] = None,
        utm_campaign: Optional[str] = None,
        utm_term: Optional[str] = None,
        utm_content: Optional[str] = None,
    ) -> InvoicePaymentParamsResponse:
        """Create one-time payment"""
        self.logger.info(
            "Creating one-time payment",
            {"email": email, "offer_id": offer_id, "currency": currency.value},
        )

        return self.create_invoice(
            email=email,
            offer_id=offer_id,
            currency=currency,
            periodicity=Periodicity.ONE_TIME,
            payment_method=payment_method,
            buyer_language=buyer_language,
            utm_source=utm_source,
            utm_medium=utm_medium,
            utm_campaign=utm_campaign,
            utm_term=utm_term,
            utm_content=utm_content,
        )

    def create_subscription(
        self,
        email: str,
        offer_id: str,
        currency: Currency,
        periodicity: Periodicity,  # Must not be ONE_TIME
        payment_method: Optional[PaymentMethod] = None,
        buyer_language: Optional[Language] = None,
        utm_source: Optional[str] = None,
        utm_medium: Optional[str] = None,
        utm_campaign: Optional[str] = None,
        utm_term: Optional[str] = None,
        utm_content: Optional[str] = None,
    ) -> InvoicePaymentParamsResponse:
        """Create subscription"""
        if periodicity == Periodicity.ONE_TIME:
            raise ValueError("Subscription cannot have ONE_TIME periodicity")

        self.logger.info(
            "Creating subscription",
            {
                "email": email,
                "offer_id": offer_id,
                "currency": currency.value,
                "periodicity": periodicity.value,
            },
        )

        return self.create_invoice(
            email=email,
            offer_id=offer_id,
            currency=currency,
            periodicity=periodicity,
            payment_method=payment_method,
            buyer_language=buyer_language,
            utm_source=utm_source,
            utm_medium=utm_medium,
            utm_campaign=utm_campaign,
            utm_term=utm_term,
            utm_content=utm_content,
        )

    def get_invoice(self, invoice_id: str) -> InvoiceResponseV2:
        """Get invoice details by ID"""
        self.logger.info("Fetching invoice details", {"invoice_id": invoice_id})

        response = self._make_request("GET", f"/api/v1/invoices/{invoice_id}")
        result = InvoiceResponseV2(**response)

        self.logger.info("Invoice details retrieved", {"invoice_id": invoice_id})
        return result

    def cancel_subscription(self, contract_id: str, email: str) -> None:
        """
        Cancel subscription

        Args:
            contract_id: Parent contract ID (from first subscription purchase)
            email: Subscription owner email
        """
        self.logger.info(
            "Cancelling subscription", {"contract_id": contract_id, "email": email}
        )

        try:
            self._make_request(
                "DELETE",
                "/api/v1/subscriptions",
                params={"contractId": contract_id, "email": email},
            )
            self.logger.info(
                "Subscription cancelled successfully",
                {"contract_id": contract_id, "email": email},
            )
        except Exception as e:
            self.logger.error(
                "Failed to cancel subscription",
                {"contract_id": contract_id, "email": email, "error": str(e)},
            )
            raise

    def get_products(
        self,
        before_created_at: Optional[str] = None,
        content_categories: Optional[FeedItemType] = None,
        product_types: Optional[ProductType] = None,
        feed_visibility: FeedVisibility = FeedVisibility.ONLY_VISIBLE,
        show_all_subscription_periods: bool = False,
    ) -> List[ProductItemResponse]:
        """Get list of products"""
        params = {
            "feedVisibility": feed_visibility.value,
            "showAllSubscriptionPeriods": str(show_all_subscription_periods).lower(),
        }

        if before_created_at:
            params["beforeCreatedAt"] = before_created_at
        if content_categories:
            params["contentCategories"] = content_categories.value
        if product_types:
            params["productTypes"] = product_types.value

        self.logger.info("Fetching products list", {"params": params})

        response = self._make_request("GET", "/api/v2/products", params=params)
        products = [ProductItemResponse(**item) for item in response.get("items", [])]

        self.logger.info("Products retrieved", {"count": len(products)})
        return products

    def get_product(self, product_id: str) -> ProductItemResponse:
        """Get product by ID"""
        self.logger.info("Fetching product details", {"product_id": product_id})

        response = self._make_request("GET", f"/api/v2/products/{product_id}")
        result = ProductItemResponse(**response)

        self.logger.info("Product details retrieved", {"product_id": product_id})
        return result

    def get_donations_url(self) -> DonateResponse:
        """Get URL for donations"""
        self.logger.info("Fetching donations URL")

        response = self._make_request("GET", "/api/v1/donate")
        result = DonateResponse(**response)

        self.logger.info("Donations URL retrieved")
        return result

    def get_sales_by_product_id(
        self, product_id: str, page: int = 1, per_page: int = 10
    ) -> Dict[str, Any]:
        """
        Get sales data for a specific product

        Args:
            product_id: ID of the product
            page: Page number (default: 1)
            per_page: Number of items per page (default: 10)

        Returns:
            Dictionary containing sales data
        """
        self.logger.info(f"Fetching sales for product {product_id}")

        params = {"page": page, "perPage": per_page}
        response = self._make_request("GET", f"/api/v1/sales/{product_id}", params=params)

        self.logger.info(f"Retrieved sales data for product {product_id}")
        return response

    # Webhook Methods

    def verify_webhook_signature(
        self, payload: str, signature: str, secret: Optional[str] = None
    ) -> bool:
        """Verify webhook signature"""
        webhook_secret = secret or self.webhook_secret_key
        if not webhook_secret:
            raise ValueError("Webhook secret is required for signature verification")

        import hmac
        import hashlib

        expected_signature = hmac.new(
            webhook_secret.encode(), payload.encode(), hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature, expected_signature)

    def parse_webhook(self, payload: Dict[str, Any]) -> PurchaseWebhookLog:
        """Parse webhook payload"""
        return PurchaseWebhookLog(**payload)


class APIError(Exception):
    """Custom exception for API errors"""

    def __init__(self, message: str, details: Optional[Dict[str, str]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class SubscriptionNotFoundError(APIError):
    """Exception for subscription not found"""

    def __init__(self, contract_id: str):
        super().__init__(f"Subscription with contract ID {contract_id} not found")


class SubscriptionValidationError(APIError):
    """Exception for subscription validation errors"""

    def __init__(self, message: str, details: Optional[Dict[str, str]] = None):
        super().__init__(message, details)
