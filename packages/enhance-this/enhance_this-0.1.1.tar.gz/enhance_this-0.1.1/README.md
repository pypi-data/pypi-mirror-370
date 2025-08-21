# enhance-this ✨

[![PyPI - Version](https://img.shields.io/pypi/v/enhance-this?style=for-the-badge)](https://pypi.org/project/enhance-this/)
[![npm - Version](https://img.shields.io/npm/v/enhance-this?style=for-the-badge)](https://www.npmjs.com/package/enhance-this)
[![Homebrew - Version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fformulae.brew.sh%2Fapi%2Fformula%2Fenhance-this.json&query=%24.versions.stable&label=homebrew&style=for-the-badge)](https://formulae.brew.sh/formula/enhance-this)
[![License](https://img.shields.io/github/license/hariharen9/enhance-this?style=for-the-badge)](LICENSE)

**`enhance-this`** is a powerful, fast, and reliable CLI tool designed to elevate your prompts. It takes a simple idea, enhances it using local Ollama AI models, and delivers a comprehensive, structured prompt ready to generate superior AI responses. The enhanced prompt is streamed directly to your terminal and automatically copied to your clipboard for immediate use.

## 🚀 Overview

The core mission of `enhance-this` is to bridge the gap between a simple user query and a high-quality, detailed prompt that AI models can understand and act upon effectively. By leveraging a sophisticated and customizable templating system, the power of local language models via Ollama, and a rich terminal interface, it transforms basic inputs into professional-grade prompts.

## ✨ Features

-   **Live Streaming Output**: Get instant feedback as the enhanced prompt is generated token by token, providing a dynamic user experience.
-   **Powerful Prompt Enhancement**: Utilizes a system of style-based templates (`detailed`, `concise`, `creative`, `technical`) to convert simple prompts into comprehensive, actionable ones.
-   **Fully Customizable Templates**: Extend the tool with your own unique enhancement styles by simply adding paths to your custom template files in `config.yaml`.
-   **Diff View**: Use the `--diff` flag to see a clear, color-coded comparison between your original prompt and the enhanced version, highlighting the changes.
-   **Full Ollama Integration**: Seamlessly connects to your local Ollama instance (`http://localhost:11434`) to manage and interact with AI models directly on your machine.
-   **Intelligent Model Management**:
    -   Automatically detects if the Ollama service is running.
    -   Lists all available local models with `enhance --list-models`.
    -   Auto-selects an optimal model if one is not specified.
    -   Features resilient retry logic for network requests, ensuring robust communication.
-   **Automatic Setup**: A simple `enhance --auto-setup` command downloads a recommended model (e.g., `llama3.1:8b`) if no models are found locally, with intelligent fallbacks.
-   **Rich Terminal UI**: Employs the `rich` library for beautiful, color-coded output, elegant markdown rendering, and informative progress bars during operations.
-   **Cross-Platform Clipboard**: Automatically copies the final enhanced prompt to your system's clipboard, ready for pasting into your AI interface. Works seamlessly across macOS, Linux, and Windows.
-   **Highly Configurable**: Control everything from the Ollama host and default styles to temperature and maximum token length via a simple YAML configuration file.
-   **Robust Testing**: Includes a comprehensive testing suite covering unit, integration, and end-to-end scenarios to ensure reliability and correctness.

## 📦 Installation

`enhance-this` is designed for easy installation across multiple platforms.

**PyPI (Python Package Index)**

```bash
pip install enhance-this
```

**NPM (Node.js Package Manager)**

```bash
npm install -g enhance-this
```

**Homebrew (macOS & Linux)**

```bash
brew install hariharen9/tap/enhance-this
```

**For Local Development**

If you want to contribute or develop locally, clone the repository and install in editable mode:

```bash
git clone https://github.com/hariharen9/enhance-this.git
cd enhance-this
pip install -e .
```

## 💡 Usage

First, ensure you have [Ollama](https://ollama.com/) installed and running. If you don't have any models downloaded, run:

```bash
enhance --auto-setup
```

Then, you can start enhancing your prompts:

**Basic Enhancement:**

```bash
enhance "write a blog post about AI"
```

**Using the Diff View:**

```bash
enhance "review my code" --diff
```

**Using a Custom Style:**

(First, define your custom style in `~/.enhance-this/config.yaml`)

```bash
enhance "a logo for a coffee shop" -s my-logo-style
```

### Command-Line Options

| Option | Short | Description |
|---|---|---|
| `<prompt>` | | The initial prompt to enhance. |
| `--model <MODEL>` | `-m` | Ollama model to use. |
| `--temperature <T>` | `-t` | Temperature for generation (0.0-2.0). |
| `--length <LENGTH>` | `-l` | Max tokens for the enhanced prompt. |
| `--style <STYLE>` | `-s` | Enhancement style (e.g., `detailed`, `creative`). |
| `--diff` | | Show a diff between the original and enhanced prompt. |
| `--output <FILE>` | `-o` | Save the enhanced prompt to a file. |
| `--no-copy` | `-n` | Disable automatic copying to the clipboard. |
| `--verbose` | `-v` | Enable verbose output. |
| `--list-models` | | List all available Ollama models. |
| `--download-model <MODEL>`| | Download a specific model from Ollama. |
| `--auto-setup` | | Automatically download a recommended model. |
| `--version` | | Show the application version. |
| `--help` | `-h` | Show the help message. |

## 🧪 Testing

The project includes a comprehensive test suite to ensure reliability and correctness.

**Running Tests Locally**

To run all tests, navigate to the project root and execute:

```bash
pytest tests/
```

**Test Strategy**

-   **Unit Tests**: Verify individual functions and components in isolation.
-   **Integration Tests**: Ensure different modules and external services (like Ollama, with proper mocking or live checks) work together correctly.
-   **End-to-End Tests**: Simulate real-world usage scenarios through the CLI to confirm the entire workflow functions as expected.

## 📚 Documentation

-   **[Configuration Guide](./docs/CONFIGURATION.md)**: Learn how to customize every aspect of the tool, including setting up custom templates.
-   **[Troubleshooting Guide](./docs/TROUBLESHOOTING.md)**: Find solutions to common problems and error messages.
-   **[Examples](./examples)**: Explore more real-world usage examples and prompt enhancement scenarios.

## 🤝 Contributing

Contributions are welcome! Please feel free to open issues, submit pull requests, or suggest new features. See the [CONTRIBUTING.md](CONTRIBUTING.md) (coming soon) for more details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
*This README was generated and enhanced by Gemini based on the project's development specification and implemented features.*