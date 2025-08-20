# Mind Terminal

## Overview

Terminal large language model client implemented using Python with a modular architecture.

## Technology Stack
  * Use UV to manage development environments and third-party dependencies.
  * Use the [prompt-toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit) to handle user input and interaction.
  * Interact with the backend large language model service using [openai-python](https://github.com/openai/openai-python)
  * Use the [rich](https://github.com/Textualize/rich) library to beautify terminal display.
  * Use [Pytest testing](https://github.com/pytest-dev/pytest) ensures the correctness of each module and function.

## Features

  * [x] Handle user input
  * [x] Interact with the backend large language model
  * [x] Write unit tests for interacting with LLM
  * [x] Beautify terminal display with Rich formatting
  * [x] Modular code structure
  * [x] Configuration management
  * [x] Error handling

## Installation

Ensure you are using Python 3.11 or later (but less than 4.0).

``` shell
pip install mindterm --user
```

## Usage

Set your OpenAI API key as an environment variable:

``` shell
export OPENAI_API_KEY=your-api-key-here
```

Then run the application:

``` shell
mt
```

### Commands

- `\chat` - Start a chat session (default mode)
- `\bye` - Exit the application
- `\help` - Show available commands

## Testing

Tests for the app are included using [pytest](https://docs.pytest.org/). To run the tests, simply execute:

```bash
uv run pytest
```

## Project Structure

```
src/
├── mindterm/
│   ├── __init__.py
│   ├── config.py      # Configuration management
│   ├── client.py      # LLM client
│   ├── ui.py          # Terminal UI components
│   ├── commands.py    # Command handling
│   └── main.py        # Main application logic
tests/
├── test_config.py     # Tests for configuration
└── test_commands.py   # Tests for command handling
```

## Contributing

Contributions are welcome! If you have ideas for improvements, bug fixes, or additional features, feel free to open an issue or submit a pull request.

## License

This App is open-source software released under the [MIT License](./LICENSE).
