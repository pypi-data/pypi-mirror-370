"""Tests for the client module."""
from unittest.mock import Mock, patch

import pytest
from mindterm.client import LLMClient
from mindterm.config import config


@patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
@patch("mindterm.client.OpenAI")
def test_llm_client_initialization(mock_openai) -> None:
    """Test LLMClient initialization."""
    # Mock config validation to return True
    with patch.object(config, "validate", return_value=True):
        with patch.object(config, "api_key", "test-key"):
            with patch.object(config, "base_url", "http://test-url"):
                with patch.object(config, "model", "test-model"):
                    client = LLMClient()
                    assert isinstance(client, LLMClient)
                    assert hasattr(client, "client")
                    assert hasattr(client, "model")
                    assert client.model == "test-model"
                    mock_openai.assert_called_once_with(
                        api_key="test-key", base_url="http://test-url"
                    )


@patch.dict("os.environ", {}, clear=True)
def test_llm_client_initialization_failure() -> None:
    """Test LLMClient initialization failure with invalid config."""
    # Mock config validation to return False
    with patch.object(config, "validate", return_value=False):
        with pytest.raises(
            ValueError,
            match="Invalid configuration. Please set the OPENAI_API_KEY environment variable.",
        ):
            LLMClient()


@patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
@patch("mindterm.client.OpenAI")
def test_llm_client_get_completion(mock_openai) -> None:
    """Test LLMClient get_completion method."""
    # Mock config validation to return True
    with patch.object(config, "validate", return_value=True):
        with patch.object(config, "api_key", "test-key"):
            with patch.object(config, "base_url", "http://test-url"):
                with patch.object(config, "model", "test-model"):
                    # Create mock response chunks
                    mock_chunk1 = Mock()
                    mock_chunk1.choices = [Mock()]
                    mock_chunk1.choices[0].delta.content = "Hello"

                    mock_chunk2 = Mock()
                    mock_chunk2.choices = [Mock()]
                    mock_chunk2.choices[0].delta.content = " World"

                    mock_chunk3 = Mock()
                    mock_chunk3.choices = [Mock()]
                    mock_chunk3.choices[0].delta.content = None

                    mock_response = Mock()
                    mock_response.__iter__ = Mock(
                        return_value=iter([mock_chunk1, mock_chunk2, mock_chunk3])
                    )

                    # Configure the mock OpenAI client
                    mock_client_instance = Mock()
                    mock_openai.return_value = mock_client_instance
                    mock_client_instance.chat.completions.create.return_value = (
                        mock_response
                    )

                    # Create client and test
                    client = LLMClient()
                    result = list(client.get_completion("Hello"))

                    assert result == ["Hello", " World"]
                    mock_client_instance.chat.completions.create.assert_called_once_with(
                        model="test-model",
                        messages=[
                            {
                                "role": "system",
                                "content": "You are a helpful assistant.",
                            },
                            {"role": "user", "content": "Hello"},
                        ],
                        stream=True,
                    )


@patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
@patch("mindterm.client.OpenAI")
@patch("builtins.print")
def test_llm_client_get_completion_exception(mock_print, mock_openai) -> None:
    """Test LLMClient get_completion method handles exceptions."""
    # Mock config validation to return True
    with patch.object(config, "validate", return_value=True):
        with patch.object(config, "api_key", "test-key"):
            with patch.object(config, "base_url", "http://test-url"):
                with patch.object(config, "model", "test-model"):
                    # Configure the mock OpenAI client to raise an exception
                    mock_client_instance = Mock()
                    mock_openai.return_value = mock_client_instance
                    mock_client_instance.chat.completions.create.side_effect = (
                        Exception("Test error")
                    )

                    # Create client and test
                    client = LLMClient()
                    result = list(client.get_completion("Hello"))

                    assert result == []
                    mock_print.assert_called_once_with(
                        "Error getting completion: Test error"
                    )
