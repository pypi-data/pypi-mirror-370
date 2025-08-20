"""Tests for the UI module."""
from unittest.mock import Mock, patch

from mindterm.ui import CommandCompleter, TerminalUI
from prompt_toolkit.document import Document


def test_command_completer_initialization() -> None:
    """Test CommandCompleter initialization."""
    completer = CommandCompleter()
    assert isinstance(completer, CommandCompleter)
    assert hasattr(completer, "commands")
    assert "\\chat" in completer.commands
    assert "\\bye" in completer.commands
    assert "\\help" in completer.commands


def test_command_completer_get_completions_at_beginning() -> None:
    """Test CommandCompleter provides completions at the beginning of the line."""
    completer = CommandCompleter()

    # Test with document starting with backslash and cursor at end
    document = Mock(spec=Document)
    document.text = "\\"
    document.cursor_position = 1

    completions = list(completer.get_completions(document, None))
    assert len(completions) == 3  # Should have all three commands

    # Check that completions have correct text
    completion_texts = [c.text for c in completions]
    assert "\\chat" in completion_texts
    assert "\\bye" in completion_texts
    assert "\\help" in completion_texts


def test_command_completer_get_completions_partial_match() -> None:
    """Test CommandCompleter provides completions for partial matches."""
    completer = CommandCompleter()

    # Test with partial command
    document = Mock(spec=Document)
    document.text = "\\ch"
    document.cursor_position = 3

    completions = list(completer.get_completions(document, None))
    assert len(completions) == 1  # Should have only chat command
    assert completions[0].text == "\\chat"


def test_command_completer_no_completions_not_at_beginning() -> None:
    """Test CommandCompleter doesn't provide completions when not at beginning."""
    completer = CommandCompleter()

    # Test with text not starting with backslash
    document = Mock(spec=Document)
    document.text = "hello \\"
    document.cursor_position = 7

    completions = list(completer.get_completions(document, None))
    assert len(completions) == 0  # Should have no completions


def test_command_completer_no_completions_cursor_not_at_end() -> None:
    """Test CommandCompleter doesn't provide completions when cursor not at end."""
    completer = CommandCompleter()

    # Test with cursor not at the end
    document = Mock(spec=Document)
    document.text = "\\"
    document.cursor_position = 0  # Cursor at beginning, not end

    completions = list(completer.get_completions(document, None))
    assert len(completions) == 0  # Should have no completions


def test_terminal_ui_initialization() -> None:
    """Test TerminalUI initialization."""
    with patch("mindterm.ui.PromptSession"):
        ui = TerminalUI()
        assert isinstance(ui, TerminalUI)
        assert hasattr(ui, "completer")
        assert isinstance(ui.completer, CommandCompleter)
        assert hasattr(ui, "session")
        assert hasattr(ui, "console")


@patch("mindterm.ui.PromptSession")
def test_terminal_ui_get_user_input(mock_prompt_session) -> None:
    """Test TerminalUI get_user_input method."""
    mock_session = Mock()
    mock_prompt_session.return_value = mock_session
    mock_session.prompt.return_value = "\\chat"

    ui = TerminalUI()
    result = ui.get_user_input()

    assert result == "\\chat"
    # Check that prompt was called with HTML formatted prompt
    mock_session.prompt.assert_called_once()
    call_args = mock_session.prompt.call_args[0]
    assert "MindTerm" in str(call_args[0])
    assert ">" in str(call_args[0])
    assert mock_session.prompt.call_args[1]["completer"] == ui.completer
