"""
WebhookServer implementation for handling LavaTop webhooks

This module provides a simple HTTP server for handling webhooks,
similar to the Node.js WebhookServer implementation.
"""
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Optional, Callable, Dict, Any
from .logger import Logger, LogLevel
from .types_custom import PurchaseWebhookLog, WebhookEventType


class WebhookRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for webhook endpoints"""

    def __init__(self, webhook_server_instance, *args, **kwargs):
        self.webhook_server = webhook_server_instance
        super().__init__(*args, **kwargs)

    def do_POST(self):
        """Handle POST requests to webhook endpoint"""
        if self.path != "/webhook":
            self.send_error(404, "Not found")
            return

        try:
            # Get signature from headers
            signature = self.headers.get("signature", "")
            if not signature:
                self.webhook_server.logger.warning("Missing signature header")
                self.send_error(400, "Missing signature header")
                return

            # Read request body
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")

            # Process webhook
            self.webhook_server.handle_webhook(signature, body)

            # Send success response
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"success": True}).encode())

        except Exception as e:
            self.webhook_server.logger.error(f"Error processing webhook: {e}")
            self.send_error(500, "Internal server error")

    def log_message(self, format, *args):
        """Override to use our logger instead of stderr"""
        self.webhook_server.logger.debug(f"HTTP: {format % args}")


class WebhookServer:
    """
    Simple HTTP server for handling LavaTop webhooks
    
    Example usage:
        from lava_top_sdk import LavaClient, WebhookServer
        
        client = LavaClient(config)
        
        def on_payment_success(webhook_data):
            print(f"Payment successful: {webhook_data.contractId}")
        
        server = WebhookServer(
            client=client,
            port=3000,
            on_payment_success=on_payment_success
        )
        
        # Server runs until stopped
        server.start()
    """

    def __init__(
        self,
        client,
        port: int = 3000,
        host: str = "localhost",
        logger: Optional[Logger] = None,
        on_payment_success: Optional[Callable[[PurchaseWebhookLog], None]] = None,
        on_payment_failed: Optional[Callable[[PurchaseWebhookLog], None]] = None,
        on_subscription_recurring_payment_success: Optional[Callable[[PurchaseWebhookLog], None]] = None,
        on_subscription_recurring_payment_failed: Optional[Callable[[PurchaseWebhookLog], None]] = None,
        on_subscription_cancelled: Optional[Callable[[PurchaseWebhookLog], None]] = None,
    ):
        self.client = client
        self.port = port
        self.host = host
        self.logger = logger or Logger(level=LogLevel.INFO)
        self.server: Optional[HTTPServer] = None
        
        # Event handlers
        self.on_payment_success = on_payment_success
        self.on_payment_failed = on_payment_failed
        self.on_subscription_recurring_payment_success = on_subscription_recurring_payment_success
        self.on_subscription_recurring_payment_failed = on_subscription_recurring_payment_failed
        self.on_subscription_cancelled = on_subscription_cancelled

    def handle_webhook(self, signature: str, body: str) -> None:
        """Handle incoming webhook request"""
        self.logger.debug("Received webhook request", {
            "signature_length": len(signature),
            "body_length": len(body)
        })

        # Verify signature
        if not self.client.verify_webhook_signature(body, signature):
            self.logger.warning("Invalid webhook signature")
            raise ValueError("Invalid webhook signature")

        # Parse webhook data
        try:
            data = json.loads(body)
            webhook = self.client.parse_webhook(data)
        except Exception as e:
            self.logger.error(f"Error parsing webhook data: {e}")
            raise

        # Handle different event types
        self._dispatch_webhook_event(webhook)

    def _dispatch_webhook_event(self, webhook: PurchaseWebhookLog) -> None:
        """Dispatch webhook event to appropriate handler"""
        event_type = webhook.eventType
        
        if event_type == WebhookEventType.PAYMENT_SUCCESS and self.on_payment_success:
            self.logger.debug("Processing payment success event")
            self.on_payment_success(webhook)
        elif event_type == WebhookEventType.PAYMENT_FAILED and self.on_payment_failed:
            self.logger.debug("Processing payment failed event")
            self.on_payment_failed(webhook)
        elif (event_type == WebhookEventType.SUBSCRIPTION_RECURRING_PAYMENT_SUCCESS 
              and self.on_subscription_recurring_payment_success):
            self.logger.debug("Processing subscription recurring payment success event")
            self.on_subscription_recurring_payment_success(webhook)
        elif (event_type == WebhookEventType.SUBSCRIPTION_RECURRING_PAYMENT_FAILED 
              and self.on_subscription_recurring_payment_failed):
            self.logger.debug("Processing subscription recurring payment failed event")
            self.on_subscription_recurring_payment_failed(webhook)
        elif (event_type == WebhookEventType.SUBSCRIPTION_CANCELLED 
              and self.on_subscription_cancelled):
            self.logger.debug("Processing subscription cancelled event")
            self.on_subscription_cancelled(webhook)
        else:
            self.logger.debug(f"No handler for event type: {event_type}")

    def start(self) -> None:
        """Start the webhook server"""
        def handler_factory(*args, **kwargs):
            return WebhookRequestHandler(self, *args, **kwargs)

        self.server = HTTPServer((self.host, self.port), handler_factory)
        self.logger.info(f"Webhook server listening on {self.host}:{self.port}")
        
        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            self.logger.info("Webhook server stopped by user")
            self.stop()

    def stop(self) -> None:
        """Stop the webhook server"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.logger.info("Webhook server stopped")
