import os
import json
from typing import Optional
from .types_custom import Config, WebhookConfig
from dotenv import load_dotenv


class Configuration:
    def __init__(
        self,
        config_path: Optional[str] = None,
        api_key: Optional[str] = None,
        env: Optional[str] = None,
    ):
        load_dotenv()
        self.config = self._load_config(config_path, api_key, env)

    def _load_config(
        self,
        config_path: Optional[str] = None,
        api_key: Optional[str] = None,
        env: Optional[str] = None,
    ) -> Config:
        # First try to load from parameters
        api_key_value = api_key or os.getenv("LAVA_API_KEY")
        env_value = env or os.getenv("LAVA_ENV", "production")
        api_url = os.getenv("LAVA_API_URL")

        # Determine API URL based on environment
        if not api_url:
            if env_value == "sandbox":
                api_url = (
                    "https://gate.sandbox.lava.top"  # Replace with actual sandbox URL
                )
            else:
                api_url = "https://gate.lava.top"

        # If config file is provided, load from it
        webhook_config = None
        if config_path and os.path.exists(config_path):
            with open(config_path, "r") as f:
                file_config = json.load(f)
                api_key_value = file_config.get("api_key", api_key_value)
                api_url = file_config.get("api_url", api_url)
                env_value = file_config.get("env", env_value)

                if "webhook" in file_config:
                    webhook = file_config["webhook"]
                    webhook_config = WebhookConfig(
                        url=webhook["url"],
                        secret=webhook["secret"],
                        events=webhook.get("events", []),
                    )

        if not api_key_value:
            raise ValueError(
                "API key is required. Set it via LAVA_API_KEY environment variable, config file, or constructor parameter."
            )

        if not api_url:
            raise ValueError(
                "API URL is required. Set it via LAVA_API_URL environment variable or config file."
            )

        return Config(
            api_key=api_key_value,
            api_url=api_url,
            env=env_value,
            webhook_config=webhook_config,
        )

    def get_api_key(self) -> str:
        return self.config.api_key

    def get_api_url(self) -> str:
        return self.config.api_url

    def get_env(self) -> str:
        return self.config.env or "production"

    def get_webhook_config(self) -> Optional[WebhookConfig]:
        return self.config.webhook_config

    def get_timeout(self) -> int:
        return self.config.timeout

    def get_max_retries(self) -> int:
        return self.config.max_retries
