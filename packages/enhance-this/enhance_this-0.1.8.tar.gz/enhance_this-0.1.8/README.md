# ENHANCE ✨ Your AI Prompts, Instantly.

[![PyPI - Version](https://img.shields.io/pypi/v/enhance-this?style=for-the-badge)](https://pypi.org/project/enhance-this/)
[![npm - Version](https://img.shields.io/npm/v/enhance-this?style=for-the-badge)](https://www.npmjs.com/package/enhance-this)
[![Homebrew - Version](https://img.shields.io/github/v/release/hariharen9/enhance-this?style=for-the-badge&label=homebrew)](https://github.com/hariharen9/homebrew-tap)

[![License](https://img.shields.io/github/license/hariharen9/enhance-this?style=for-the-badge)](LICENSE)

Are you tired of generic AI responses? Do you wish your AI models understood exactly what you need? **`enhance-this`** is your secret weapon. This lightning-fast command-line tool transforms your simple ideas into rich, detailed prompts, ensuring you get the best possible output from any AI model. And the best part? It runs locally, keeping your data private and your workflow smooth.

Whether you're a developer, a student, a writer, or just curious about AI, `enhance-this` makes interacting with AI more powerful and intuitive.

-----

## 🚀 Why `enhance-this` Will Be Your Go-To Tool

In today's fast-paced world, getting quick, accurate, and high-quality results from AI is crucial. `enhance-this` is built for **speed** and **simplicity**, allowing you to:

  * **Elevate Your AI Interactions**: Go from a basic idea like "write a blog post about AI" to a meticulously crafted prompt that guides the AI for a superior output.
  * **Boost Productivity**: No more manual prompt engineering! Get the perfect prompt copied to your clipboard in seconds, ready to paste.
  * **Maintain Privacy**: All enhancements are powered by **Ollama** models running directly on your machine. Your data never leaves your computer.
  * **Save Time & Effort**: Automate the process of creating effective prompts, freeing you up to focus on the core task.

-----

## ✨ Features That Make a Difference

`enhance-this` is packed with smart features designed to make your AI interactions effortless and powerful:

  * **Instant Enhancement, Live**: See your prompt being enhanced in real-time. It's like watching a master prompt engineer at work, right in your terminal.
  * **Interactive Mode**: Start an interactive session with `enhance --interactive` to refine your prompts iteratively.
  * **Smart Model Management**: `enhance-this` intelligently finds and uses the best local Ollama model available. No model? It can even download a recommended one for you, with a clear progress bar.
  * **Tailor-Made Prompts**: Choose from built-in styles like `detailed`, `creative`, `technical`, `json`, `bullets`, `summary`, `formal`, and `casual`. Want something unique? You can easily create your **own custom prompt templates**!
  * **See the Difference**: Use the `--diff` flag to instantly compare your original prompt with the enhanced version, highlighting exactly what's been added for clarity and depth.
  * **Seamless Workflow**: Once enhanced, your refined prompt is automatically copied to your clipboard, ready for immediate use in any AI interface.
  * **History**: Keep track of your enhancements with the `enhance --history` command.
  * **Highly Customizable**: A simple YAML configuration file lets you fine-tune everything from the AI's creativity (temperature) to default settings.

-----

## ⚡ Get Started in Minutes!

### Prerequisite: Get Ollama

`enhance-this` works hand-in-hand with **Ollama**, a fantastic tool that lets you run large language models locally. If you haven't already, download and install [Ollama](https://ollama.com/) for your operating system. Make sure it's running before you use `enhance-this`!

### Installation: Pick Your Favorite!

We've made `enhance-this` available through your preferred package manager:

**PyPI**: The most common way to install Python tools.

```bash
pip install enhance-this
```

**NPM**: If you're a Node.js user, this is for you!

```bash
npm install -g enhance-this
```

**Homebrew (macOS & Linux)**: Mac and Linux users can grab it with one command.

```bash
brew install hariharen9/tap/enhance-this
```

-----

## 💡 How to Use `enhance-this`

Using `enhance-this` is incredibly straightforward. Just tell it what you want to enhance!

**Basic Enhancement:**

```bash
enhance "write a blog post about AI"
# Output: "Create a comprehensive blog post about artificial intelligence that educates readers about current AI developments, applications, and implications. Structure the content with: an engaging introduction that hooks the reader, clear explanations of key AI concepts, real-world examples and case studies, discussion of both benefits and challenges, and actionable insights for the target audience. Ensure the tone is accessible to non-technical readers while maintaining accuracy and depth."
```

**Interactive Mode:**

```bash
enhance --interactive
```

**See the Magic with `--diff`:**

```bash
enhance "review my code" --diff
# Shows a side-by-side comparison of your original prompt and the new, improved version!
```

**Choose a Style:**

```bash
enhance "a logo for a coffee shop" -s creative
```

**View Your History:**

```bash
enhance --history
```

-----

## 🚀 Performance Tips

To get the fastest response times, you can preload a model into your computer's memory. This keeps the model ready to go, so you don't have to wait for it to load every time.

**Preload a Model:**

```bash
enhance --preload-model
```

This will load the best available model into memory and keep it there. For the best performance, we recommend using a fast and capable model like `llama3.1:8b` or `mistral`.

You can also configure Ollama to keep models alive for a specific duration. See the Ollama documentation for more details on the `keep_alive` parameter in your Modelfiles.

-----

## 📚 Dive Deeper & Get More!

Ready to unlock even more potential?

  * **[Configuration Guide](./docs/CONFIGURATION.md)**: Master customization! Learn how to define your own prompt styles and tweak `enhance-this` to perfectly fit your workflow.
  * **[Troubleshooting Guide](./docs/TROUBLESHOOTING.md)**: Quick solutions to common questions and issues.
  * **[Examples](./examples)**: Explore more real-world use cases and see `enhance-this` in action!

-----

## 🤝 Join Our Community!

We're always looking to make `enhance-this` even better! If you have ideas, spot a bug, or just want to chat about prompt engineering, come join us. Check out our [CONTRIBUTING.md](./CONTRIBUTING.md) for details on how you can get involved. Your contributions help shape the future of this tool!

-----

## 📄 License

This project is open-source and available under the MIT License - see the [LICENSE](./LICENSE) file for more details.

---
*This README was crafted and enhanced by Gemini to make `enhance-this` even more accessible and exciting!*
