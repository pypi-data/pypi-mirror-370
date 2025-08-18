# Lava.top API Python Client Library

[🇷🇺 Русская версия](README.ru.md)

A Python client library for interacting with the Lava.top API. This library provides a simple and intuitive interface for creating and managing payments, subscriptions, and handling webhooks.

## Features

- ✅ Type-safe API interactions
- ✅ Modern async/await syntax  
- ✅ Comprehensive error handling
- ✅ Support for sandbox and production environments
- ✅ Support for multiple currencies (RUB, USD, EUR)
- ✅ Support for various payment methods (BANK131, UNLIMINT, PAYPAL, STRIPE)
- ✅ Webhook signature verification
- ✅ Subscription management
- ✅ Configurable logging with different levels

## Installation

```bash
pip install lava-top-sdk
```

## Quick Start

### 1. Initialize Client

```python
from lava_top_sdk import LavaClient, LavaClientConfig, Currency, PaymentMethod, LogLevel

# Recommended way (with explicit configuration)
config = LavaClientConfig(
    api_key='your-api-key',
    env='sandbox',  # or 'production'
    webhook_secret_key='your-webhook-secret',
    logging_level=LogLevel.DEBUG
)

client = LavaClient(config)
```

### 2. Create One-time Payment

```python
# Create one-time payment
payment = client.create_one_time_payment(
    email="customer@example.com",
    offer_id="836b9fc5-7ae9-4a27-9642-592bc44072b7",
    currency=Currency.RUB,
    payment_method=PaymentMethod.BANK131,
    utm_source="google",
    utm_campaign="summer_sale"
)

print(f"Payment created: {payment.id}")
print(f"Payment URL: {payment.paymentUrl}")
```

### 3. Create Subscription

```python
from lava_top_sdk import Periodicity

# Create subscription
subscription = client.create_subscription(
    email="subscriber@example.com",
    offer_id="836b9fc5-7ae9-4a27-9642-592bc44072b7",
    currency=Currency.RUB,
    periodicity=Periodicity.MONTHLY,
    payment_method=PaymentMethod.BANK131
)

print(f"Subscription created: {subscription.id}")
```

### 4. Cancel Subscription

```python
# Cancel subscription
client.cancel_subscription(
    contract_id="subscription-contract-id",
    email="subscriber@example.com"
)

print("Subscription cancelled successfully")
```

### 5. Handle Webhooks

```python
from fastapi import FastAPI, Request, HTTPException
from lava_top_sdk import WebhookEventType

app = FastAPI()

@app.post('/webhook')
async def handle_webhook(request: Request):
    # Get signature and body
    body = await request.body()
    signature = request.headers.get('signature', '')
    
    # Verify webhook signature
    if not client.verify_webhook_signature(body.decode(), signature):
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Parse webhook data
    webhook_data = await request.json()
    webhook = client.parse_webhook(webhook_data)
    
    # Handle different event types
    if webhook.eventType == WebhookEventType.PAYMENT_SUCCESS:
        print(f"Payment successful: {webhook.contractId}")
        # Add your business logic here
    
    return {"status": "ok"}
```

### 6. Simple Webhook Server

For quick webhook handling, you can use the built-in WebhookServer:

```python
from lava_top_sdk import WebhookServer

def handle_payment_success(webhook):
    print(f"Payment successful: {webhook.contractId}")

def handle_payment_failed(webhook):
    print(f"Payment failed: {webhook.errorMessage}")

# Create and start webhook server
server = WebhookServer(
    client=client,
    port=3000,
    on_payment_success=handle_payment_success,
    on_payment_failed=handle_payment_failed
)

# Start server (blocks until stopped)
server.start()
```

## Configuration

The client can be configured in several ways:

### 1. Direct Configuration (recommended)
```python
from lava_top_sdk import LavaClient, LavaClientConfig, LogLevel, LogFormat

config = LavaClientConfig(
    api_key='your-api-key',
    env='sandbox',  # or 'production'
    webhook_secret_key='your-webhook-secret',
    timeout=30,
    max_retries=3,
    logging_level=LogLevel.INFO,
    logging_format=LogFormat.JSON
)

client = LavaClient(config)
```

### 2. Environment Variables
```bash
export LAVA_API_KEY="your-api-key"
export LAVA_ENV="sandbox"
```

```python
from lava_top_sdk import LavaClient

# Will use environment variables
client = LavaClient()
```

### 3. Configuration File
```json
{
    "api_key": "your-api-key",
    "env": "sandbox",
    "webhook_secret_key": "your-webhook-secret",
    "timeout": 30,
    "webhook": {
        "url": "https://your-domain.com/webhook",
        "secret": "your-webhook-secret",
        "events": ["payment.success", "payment.failed"]
    }
}
```

```python
client = LavaClient(config_path="config.json")
```

## Available Methods

### Payments and Subscriptions

- `create_invoice()` - Create invoice for content purchase
- `create_one_time_payment()` - Create one-time payment
- `create_subscription()` - Create subscription
- `get_invoice(invoice_id)` - Get invoice details
- `cancel_subscription(contract_id, email)` - Cancel subscription

### Products

- `get_products()` - Get list of products
- `get_product(product_id)` - Get product by ID
- `get_donations_url()` - Get URL for donations

### Webhooks

- `verify_webhook_signature(payload, signature)` - Verify webhook signature
- `parse_webhook(payload)` - Parse webhook data

## Supported Currencies

- `Currency.RUB` - Russian Ruble (BANK131 only)
- `Currency.USD` - US Dollar (UNLIMINT, PAYPAL, STRIPE)
- `Currency.EUR` - Euro (UNLIMINT, PAYPAL, STRIPE)

## Supported Payment Methods

- `PaymentMethod.BANK131` - For RUB payments
- `PaymentMethod.UNLIMINT` - For USD/EUR
- `PaymentMethod.PAYPAL` - For USD/EUR
- `PaymentMethod.STRIPE` - For USD/EUR (products only)

## Subscription Types

- `Periodicity.ONE_TIME` - One-time payment
- `Periodicity.MONTHLY` - Monthly subscription
- `Periodicity.PERIOD_90_DAYS` - 90-day subscription
- `Periodicity.PERIOD_180_DAYS` - 180-day subscription
- `Periodicity.PERIOD_YEAR` - Yearly subscription

## Error Handling

```python
from lava_top_sdk import APIError, SubscriptionNotFoundError, SubscriptionValidationError

try:
    payment = client.create_one_time_payment(
        email="invalid-email",
        offer_id="invalid-offer-id",
        currency=Currency.RUB
    )
except APIError as e:
    print(f"API Error: {e.message}")
    print(f"Details: {e.details}")
except SubscriptionNotFoundError as e:
    print(f"Subscription not found: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Logging

The library supports different logging levels:

```python
from lava_top_sdk import LogLevel, LogFormat

config = LavaClientConfig(
    api_key='your-api-key',
    logging_level=LogLevel.DEBUG,  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    logging_format=LogFormat.JSON  # JSON or TEXT
)
```

## Examples

More examples are available in the `examples/` folder:

- `basic_usage.py` - Basic client usage
- `webhook_server.py` - Webhook server implementation

## Testing

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=html
```

## Code Formatting and Linting

```bash
# Format code
black src/ tests/

# Check style
pylint src/
```

## License

MIT

## Links

- [API Documentation](https://gate.lava.top/docs)
- [Official Website](https://lava.top)
- [GitHub Repository](https://github.com/lava-top/python-sdk)