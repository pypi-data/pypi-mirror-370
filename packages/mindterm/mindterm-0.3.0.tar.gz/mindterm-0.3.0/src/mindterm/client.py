"""OpenAI client for Mind Terminal."""
from collections.abc import Generator

from openai import OpenAI

from mindterm.config import config


class LLMClient:
    """Client for interacting with the LLM."""

    def __init__(self) -> None:
        """Initialize the LLM client."""
        if not config.validate():
            raise ValueError(
                "Invalid configuration. Please set the OPENAI_API_KEY environment variable."
            )

        self.client = OpenAI(
            api_key=config.api_key,
            base_url=config.base_url,
        )
        self.model = config.model

    def get_completion(self, content: str) -> Generator[str, None, None]:
        """Get completion from the LLM and stream it to the console."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": content},
                ],
                stream=True,
            )
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            print(f"Error getting completion: {e}")
            return
