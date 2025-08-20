"""Tests for the main module."""
from unittest.mock import Mock, patch

from mindterm import main


@patch.dict("os.environ", {}, clear=True)
@patch("builtins.print")
def test_run_invalid_config(mock_print) -> None:
    """Test run function with invalid configuration."""
    with patch("mindterm.main.config") as mock_config:
        mock_config.validate.return_value = False
        main.run()
        mock_print.assert_called_once_with(
            "Error: OPENAI_API_KEY environment variable is not set."
        )


@patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
@patch("builtins.print")
def test_run_client_initialization_error(mock_print) -> None:
    """Test run function with client initialization error."""
    with patch("mindterm.main.config") as mock_config:
        with patch("mindterm.main.LLMClient") as mock_llm_client:
            mock_config.validate.return_value = True
            mock_llm_client.side_effect = ValueError("Test error")
            main.run()
            mock_print.assert_called_once_with("Error initializing client: Test error")


@patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
@patch("mindterm.main.LLMClient")
@patch("mindterm.main.TerminalUI")
def test_run_bye_command(mock_terminal_ui, _mock_llm_client) -> None:
    """Test run function with \\bye command."""
    with patch("mindterm.main.config") as mock_config:
        mock_config.validate.return_value = True

        # Setup mocks
        mock_ui_instance = Mock()
        mock_terminal_ui.return_value = mock_ui_instance
        mock_ui_instance.get_user_input.return_value = "\\bye"

        main.run()

        # Verify calls
        mock_ui_instance.display_welcome.assert_called_once()
        mock_ui_instance.get_user_input.assert_called_once()
        mock_ui_instance.display_goodbye.assert_called_once()


@patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
@patch("mindterm.main.LLMClient")
@patch("mindterm.main.TerminalUI")
def test_run_help_command(mock_terminal_ui, _mock_llm_client) -> None:
    """Test run function with \\help command."""
    with patch("mindterm.main.config") as mock_config:
        mock_config.validate.return_value = True

        # Setup mocks to simulate one \\help then \\bye
        mock_ui_instance = Mock()
        mock_terminal_ui.return_value = mock_ui_instance
        mock_ui_instance.get_user_input.side_effect = ["\\help", "\\bye"]

        main.run()

        # Verify calls
        mock_ui_instance.display_welcome.assert_called_once()
        assert mock_ui_instance.get_user_input.call_count == 2
        mock_ui_instance.display_help.assert_called_once()
        mock_ui_instance.display_goodbye.assert_called_once()


@patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
@patch("mindterm.main.LLMClient")
@patch("mindterm.main.TerminalUI")
def test_run_eof_error(mock_terminal_ui, _mock_llm_client) -> None:
    """Test run function with EOFError."""
    with patch("mindterm.main.config") as mock_config:
        mock_config.validate.return_value = True

        # Setup mocks
        mock_ui_instance = Mock()
        mock_terminal_ui.return_value = mock_ui_instance
        mock_ui_instance.get_user_input.side_effect = EOFError()

        main.run()

        # Verify calls
        mock_ui_instance.display_welcome.assert_called_once()
        mock_ui_instance.get_user_input.assert_called_once()
        mock_ui_instance.display_goodbye.assert_called_once()


@patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
@patch("mindterm.main.LLMClient")
@patch("mindterm.main.TerminalUI")
def test_run_keyboard_interrupt(mock_terminal_ui, _mock_llm_client) -> None:
    """Test run function with KeyboardInterrupt."""
    with patch("mindterm.main.config") as mock_config:
        mock_config.validate.return_value = True

        # Setup mocks to simulate KeyboardInterrupt then \\bye
        mock_ui_instance = Mock()
        mock_terminal_ui.return_value = mock_ui_instance
        mock_ui_instance.get_user_input.side_effect = [KeyboardInterrupt(), "\\bye"]

        main.run()

        # Verify calls
        mock_ui_instance.display_welcome.assert_called_once()
        assert mock_ui_instance.get_user_input.call_count == 2
        mock_ui_instance.display_goodbye.assert_called_once()


@patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
@patch("mindterm.main.LLMClient")
@patch("mindterm.main.TerminalUI")
def test_run_normal_command(mock_terminal_ui, mock_llm_client) -> None:
    """Test run function with normal command."""
    with patch("mindterm.main.config") as mock_config:
        mock_config.validate.return_value = True

        # Setup mocks
        mock_ui_instance = Mock()
        mock_terminal_ui.return_value = mock_ui_instance
        mock_ui_instance.get_user_input.side_effect = ["Hello", "\\bye"]

        mock_client_instance = Mock()
        mock_llm_client.return_value = mock_client_instance
        mock_client_instance.get_completion.return_value = []

        main.run()

        # Verify calls
        mock_ui_instance.display_welcome.assert_called_once()
        assert mock_ui_instance.get_user_input.call_count == 2
        mock_client_instance.get_completion.assert_called_once_with("Hello")
        mock_ui_instance.display_streamed_response.assert_called_once_with([])
        mock_ui_instance.display_goodbye.assert_called_once()
