# enhance-this ✨

[![PyPI - Version](https://img.shields.io/pypi/v/enhance-this?style=for-the-badge)](https://pypi.org/project/enhance-this/)
[![npm - Version](https://img.shields.io/npm/v/enhance-this?style=for-the-badge)](https://www.npmjs.com/package/enhance-this)
[![Homebrew - Version](https://img.shields.io/github/v/release/hariharen9/enhance-this?style=for-the-badge&label=homebrew)](https://github.com/hariharen9/homebrew-tap)

[![License](https://img.shields.io/github/license/hariharen9/enhance-this?style=for-the-badge)](LICENSE)

<!-- **`enhance-this`** is a powerful and reliable command-line tool designed to elevate your prompts for AI models. It takes your initial ideas, enhances them into rich and specific instructions using local AI models (Ollama), and then instantly copies the refined prompt to your clipboard. It acts as your personal prompt engineering assistant, running directly on your computer. -->

## 🚀 What is `enhance-this`?

At its core, `enhance-this` helps you achieve superior results from AI. By transforming your basic input into a comprehensive, well-structured prompt, it ensures the AI understands your intent precisely. This leads to higher quality and more useful responses, all powered by AI models running locally on your machine for speed and privacy.

## ✨ Key Features

-   **Live Streaming Output**: Witness your prompt being crafted in real-time, character by character, directly in your terminal.
-   **Flexible Enhancement Styles**: Choose from predefined styles (like `detailed`, `creative`, or `technical`) to tailor your prompt's output. This allows you to guide the AI precisely for your needs.
-   **Customizable Templates**: Define and use your own prompt enhancement templates, allowing for highly personalized AI interactions.
-   **Diff View**: Easily compare your original prompt with the enhanced version using a clear, color-coded diff display.
-   **Local Ollama Integration**: Seamlessly connect with your local Ollama instance to leverage powerful AI models directly on your machine, ensuring fast responses and data privacy.
-   **Intelligent Model Management**:
    -   Automatically detects running Ollama instances and available models.
    -   Automatically selects an optimal AI model if not specified.
    -   Facilitates model downloads: If a recommended model is missing, `enhance-this` can download it for you with progress indication.
    -   Resilient Network Handling: Includes retry logic for network requests to ensure robust communication.
-   **Automated Setup**: A single command (`enhance --auto-setup`) can automatically configure Ollama with a recommended AI model.
-   **Rich Terminal Output**: Utilizes `rich` for clear, color-coded, and well-formatted terminal output, including markdown rendering.
-   **Clipboard Integration**: Automatically copies the enhanced prompt to your system's clipboard for immediate use.
-   **Highly Configurable**: Customize behavior through a simple YAML configuration file, controlling aspects like model creativity and prompt enhancement logic.


## 🚀 Prequisite

**Get Ollama**: If you don't have it, download and install [Ollama](https://ollama.com/) for your operating system. Make sure it's running!


## 📦 Installation

`enhance-this` is available through popular package managers:

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

**For Developers & Contributors**

If you're looking to contribute or develop locally, clone the repository and install in editable mode:

```bash
git clone https://github.com/hariharen9/enhance-this.git
cd enhance-this
pip install -e .
```

## 💡 How to Use

Once installed and set up, using `enhance-this` is straightforward:

**Basic Prompt Enhancement:**

```bash
enhance "write a blog post about AI"
```

**See the Changes with Diff View:**

```bash
enhance "review my code" --diff
```

**Use a Custom Prompt Style:**

(First, define your custom style in your `~/.enhance-this/config.yaml` file)

```bash
enhance "a logo for a coffee shop" -s my-logo-style
```

### Command-Line Options

| Option | Short | What it Does |
|---|---|---|
| `<prompt>` | | Your initial idea or request. |
| `--model <MODEL>` | `-m` | Choose which Ollama AI model to use. |
| `--temperature <T>` | `-t` | Adjust the AI's creativity (0.0-2.0, higher is more creative). |
| `--length <LENGTH>` | `-l` | Set the maximum length for the enhanced prompt. |
| `--style <STYLE>` | `-s` | Pick an enhancement style (like `detailed`, `creative`, `technical`). |
| `--diff` | | Show you the differences between your original and enhanced prompt. |
| `--output <FILE>` | `-o` | Save the enhanced prompt to a file. |
| `--no-copy` | `-n` | Don't copy the prompt to your clipboard. |
| `--verbose` | `-v` | Show more details about what's happening behind the scenes. |
| `--list-models` | | See all the AI models you have available in Ollama. |
| `--download-model <MODEL>`| | Download a specific AI model from Ollama. |
| `--auto-setup` | | Automatically sets up Ollama with a recommended model. |
| `--version` | | Show the tool's version. |
| `--help` | `-h` | Display this helpful message. |

## 📚 More Information

-   **[Configuration Guide](./docs/CONFIGURATION.md)**: Learn how to customize `enhance-this` to fit your exact needs, including setting up your own prompt styles.
-   **[Troubleshooting Guide](./docs/TROUBLESHOOTING.md)**: Find quick solutions to common questions and issues.
-   **[Examples](./examples)**: Discover more ways to use `enhance-this` with practical examples.

## 🤝 Get Involved!

We love contributions! Whether it's reporting a bug, suggesting a new feature, or helping with code, your input is welcome. Check out our [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to get started.

## 📄 License

This project is open-source and available under the MIT License - see the [LICENSE](LICENSE) file for more details.

---
*This README was crafted and enhanced by Gemini to make `enhance-this` even more accessible and exciting!*