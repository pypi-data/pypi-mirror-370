"""UI components for Mind Terminal."""
from collections.abc import Generator

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.rule import Rule


class CommandCompleter(Completer):
    """Custom completer that only works at the beginning of the line."""

    def __init__(self) -> None:
        self.commands = ["\\chat", "\\bye", "\\help"]

    def get_completions(
        self, document: Document, complete_event: object
    ) -> Generator[Completion, None, None]:
        """Generate completions only at the beginning of the line."""
        # Only provide completions at the beginning of the line
        if document.text.startswith("\\") and document.cursor_position == len(
            document.text
        ):
            for command in self.commands:
                if command.startswith(document.text):
                    yield Completion(command, start_position=-len(document.text))


class TerminalUI:
    """Terminal UI for Mind Terminal."""

    def __init__(self) -> None:
        """Initialize the terminal UI."""
        self.completer = CommandCompleter()

        # Define a custom style for the prompt - professional dark theme
        style = Style.from_dict(
            {
                "prompt": "#5D87BF bold",  # Professional blue for prompt
                "command": "#70C0BA",  # Teal for commands
                "separator": "#6C757D",  # Gray for separators
            }
        )

        self.session: PromptSession[str] = PromptSession(
            completer=self.completer, style=style
        )
        self.console = Console()

    def display_welcome(self) -> None:
        """Display welcome message."""
        # Professional header with rule
        self.console.print()
        self.console.print(Rule("Mind Terminal", style="blue", characters="─"))
        self.console.print()
        self.console.print(
            "Welcome to Mind Terminal - Your AI Coding Assistant", style="bold blue"
        )
        self.console.print("Type '\\help' for available commands", style="dim")
        self.console.print()

    def display_response(self, response: str | None) -> None:
        """Display the LLM response."""
        if response:
            # Professional response display
            self.console.print()
            self.console.print("Assistant:", style="bold #70C0BA")
            self.console.print(Markdown(response))
            self.console.print()
        else:
            self.console.print()
            self.console.print("No response received.", style="red")
            self.console.print()

    def display_streamed_response(
        self, content_generator: Generator[str, None, None]
    ) -> None:
        """Display streamed response from the LLM."""
        # Initialize with a waiting message
        markdown_text = ""

        self.console.print()
        self.console.print("Assistant:", style="bold #70C0BA")

        with Live("", refresh_per_second=15, console=self.console) as live:
            try:
                for chunk in content_generator:
                    if chunk is not None:
                        markdown_text += chunk
                        # Update live display with rendered markdown
                        live.update(Markdown(markdown_text))
                    else:
                        markdown_text += "\nError occurred during streaming."
                        live.update(Markdown(markdown_text))
                        return
            except Exception as e:
                markdown_text += f"\nError displaying streamed response: {e}"
                live.update(Markdown(markdown_text))

        # Add a newline after the response
        self.console.print()

    def get_user_input(self) -> str:
        """Get input from the user."""
        # Professional prompt with clear visual separation
        try:
            text = self.session.prompt(
                HTML("<prompt>MindTerm</prompt><separator>:</separator> "),
                completer=self.completer,
            )
            return str(text)
        except KeyboardInterrupt:
            return ""  # Return empty string on Ctrl+C

    def display_goodbye(self) -> None:
        """Display goodbye message."""
        self.console.print()
        self.console.print(Rule("Session Ended", style="blue", characters="─"))
        self.console.print("Thank you for using Mind Terminal!", style="dim")
        self.console.print()

    def display_help(self) -> None:
        """Display help message."""
        self.console.print()
        self.console.print("Available Commands:", style="bold #70C0BA")
        self.console.print()
        self.console.print("  \\chat  - Start a new conversation")
        self.console.print("  \\bye   - Exit the application")
        self.console.print("  \\help  - Show this help message")
        self.console.print()
        self.console.print(
            "Tip: You can start typing your query directly without any command",
            style="dim",
        )
        self.console.print()
