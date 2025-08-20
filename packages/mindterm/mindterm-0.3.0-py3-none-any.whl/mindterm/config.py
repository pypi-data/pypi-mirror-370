"""Configuration management for Mind Terminal."""
import os


class Config:
    """Configuration class for Mind Terminal."""

    def __init__(self) -> None:
        """Initialize configuration with environment variables."""
        self.api_key: str | None = os.getenv("OPENAI_API_KEY")
        self.base_url: str = os.getenv(
            "OPENAI_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        self.model: str = os.getenv("OPENAI_MODEL", "qwen-plus")

    def validate(self) -> bool:
        """Validate that required configuration is present."""
        return self.api_key is not None and len(self.api_key) > 0


# Global config instance
config = Config()
