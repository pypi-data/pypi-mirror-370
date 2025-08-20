# LLMocal: Open Source Local AI Client

> ## ⚠️  **DEVELOPMENT NOTICE** ⚠️
> **This software is currently under active development and is NOT intended for production use.**  
> Features may change, break, or be removed without notice. Use at your own risk in development/testing environments only.

![LLMocal Demo](https://user-images.githubusercontent.com/12345/your-demo-image.gif)  <!-- Replace with your own demo GIF -->

**LLMocal** is a professional-grade, open-source client for running large language models locally. Built on the principle that open source models deserve open source clients, LLMocal provides a complete local AI solution without vendor lock-in or proprietary restrictions.

🎯 **Why Open Source?** The AI ecosystem thrives when both models and clients are open. LLMocal ensures you have full control over your AI infrastructure—no subscriptions, no data collection, no proprietary dependencies.

Optimized for Apple Silicon (M1/M2/M3/M4) with cross-platform support for Linux and Windows.

---

[![CI](https://github.com/alexnicita/llmocal/actions/workflows/ci.yml/badge.svg)](https://github.com/alexnicita/llmocal/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🌟 Features

- **100% Private & Offline**: Your conversations never leave your machine. No APIs, no data collection.
- **High-Performance**: Optimized for Apple Silicon, providing fast, streaming responses.
- **State-of-the-Art Models**: Comes pre-configured with `Mistral-7B-Instruct`, a top-tier open-source model.
- **Easy to Use**: A simple, clean, and intuitive command-line interface.
- **Customizable**: Easily swap out models, adjust performance settings, and extend functionality.
- **Reproducible Setup**: Uses `uv` for fast and reliable dependency management.
- **Cross-Platform**: Works on macOS, Linux, and Windows (WSL recommended).

## 🚀 Quick Start

LLMocal can be used in two ways: as a **pip-installable package** for easy integration into your projects, or by **cloning the repository** for development.

### Option 1: Install as a Python Package (Recommended)

**Prerequisites:** Python 3.11+

```bash
# Install with pip
pip install llmocal

# Or install with uv (faster)
uv add llmocal
```

#### Programmatic Usage

```python
import llmocal

# First time setup - explicit model download
client = llmocal.LLMocal()
client.download_model()  # Downloads ~4.4GB model
client.setup()           # Load the model

# Chat with the AI
response = client.chat("Explain quantum computing in simple terms")
print(response)

# Or start an interactive session
client.start_interactive_chat()

# Alternative: auto-download if needed
client = llmocal.LLMocal()
client.setup(auto_download=True)  # Downloads if model doesn't exist

# Use a custom model
custom_client = llmocal.LLMocal(
    repo_id="TheBloke/CodeLlama-7B-Instruct-GGUF",
    filename="codellama-7b-instruct.Q4_K_M.gguf"
)
custom_client.download_model()  # Explicit download
custom_client.setup()           # Load the model
code_response = custom_client.chat("Write a Python function to sort a list")
print(code_response)
```

#### Advanced Programmatic Usage

```python
import llmocal
from llmocal import LLMocalConfig

# Advanced configuration
config = LLMocalConfig(
    n_ctx=8192,        # Larger context window
    n_threads=8,       # More CPU threads
    n_gpu_layers=35    # Use GPU acceleration (if available)
)

client = llmocal.LLMocal(config=config)
client.setup()

# Access lower-level components
engine = client.engine
model_manager = client.model_manager

# Direct model management
model_path = model_manager.get_model_path(
    "microsoft/DialoGPT-medium", 
    "model.gguf"
)
```

#### Command Line Usage

After installation, you can use the `llmocal` command:

```bash
# Start interactive chat
llmocal chat

# Use a different model
llmocal chat --repo-id "TheBloke/Llama-2-7B-Chat-GGUF" --filename "llama-2-7b-chat.Q4_K_M.gguf"
```

### Option 2: Development Setup

For development or if you want to modify the code:

**Prerequisites:**
- **Python 3.11+**
- **`uv`**: A fast Python package installer. [Installation guide](https://github.com/astral-sh/uv#installation).

```bash
# Clone the repository
git clone https://github.com/alexnicita/llmocal.git
cd llmocal

# Run the startup script
./scripts/start.sh
```

The first time you run `start.sh`, it will download the model (approx. 4.4 GB), so it may take some time.

## 💬 How to Use

Once the application is running, you'll be greeted by the AI assistant. Just type your questions and press Enter.

### Sample Conversation

```
🤖 Welcome to LLMocal!

You are now chatting with an AI model running entirely on your machine.
- Model: TheBloke/Mistral-7B-Instruct-v0.2-GGUF
- Privacy: 100% offline and private. No data leaves your computer.

Type /exit or /quit to end the chat. Use /help for more commands.

You: Can you explain the concept of zero-knowledge proofs in simple terms?

AI:  Of course! Imagine you have a secret, like the password to a treasure chest, but you want to prove to a friend that you know the password without actually revealing it. A zero-knowledge proof is a cryptographic method that lets you do just that. You can convince your friend you have the secret key without them ever learning what it is. It's a fundamental concept in modern cryptography, enabling privacy and security in digital transactions.

You: Write a Python function to find the factorial of a number.

AI:  Certainly! Here is a simple and efficient Python function to calculate the factorial of a non-negative integer using recursion:

```python
def factorial(n):
    """
    Calculates the factorial of a non-negative integer.
    
    Args:
        n: The number to calculate the factorial of.
        
    Returns:
        The factorial of n.
    """
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    elif n == 0:
        return 1
    else:
        return n * factorial(n - 1)

# Example usage:
print(f"The factorial of 5 is: {factorial(5)}")  # Output: 120
```
```

### Special Commands

- `/exit` or `/quit`: Exit the chat application.
- `/help`: Display a list of available commands.
- `/model`: Show details about the currently loaded AI model.

## 🔧 Customization: Changing the Model

This project is designed to be model-agnostic. You can easily switch to any GGUF-compatible model from [Hugging Face](https://huggingface.co/models?search=gguf).

**To change the model, you can either:**

1.  **Use command-line arguments (easiest):**

    ```bash
    uv run python -m llmocal.cli chat --repo-id "TheBloke/Llama-2-7B-Chat-GGUF" --filename "llama-2-7b-chat.Q4_K_M.gguf"
    ```

2.  **Set environment variables:**

    ```bash
    export MODEL_REPO_ID="TheBloke/Llama-2-7B-Chat-GGUF"
    export MODEL_FILENAME="llama-2-7b-chat.Q4_K_M.gguf"
    ./scripts/start.sh
    ```

3.  **Edit the configuration:**

    Change the `DEFAULT_REPO_ID` and `DEFAULT_FILENAME` variables in `llmocal/core/config.py`.

## 🔬 Running Tests

A full suite of unit tests is included to ensure everything is working as expected. To run the tests:

```bash
uv run python -m tests.test_core
```

## 🛠️ Project Structure

```
llmocal/
├── .github/workflows/ci.yml  # GitHub Actions CI/CD workflow
├── .gitignore                # Files to ignore for Git
├── LICENSE                   # MIT License
├── README.md                 # This file
├── pyproject.toml            # Project dependencies and metadata
├── scripts/
│   └── start.sh              # Easy startup script
├── llmocal/                  # Main package
│   ├── __init__.py           # Package initialization
│   ├── cli.py                # Command-line interface
│   ├── core/                 # Core functionality
│   │   ├── __init__.py       # Core module initialization
│   │   ├── config.py         # Configuration management
│   │   ├── engine.py         # AI engine and model loading
│   │   └── chat.py           # Chat interface
│   ├── models/               # Model management
│   │   ├── __init__.py       # Models module initialization
│   │   └── manager.py        # Model downloading and management
│   ├── api/                  # API server components
│   ├── ui/                   # User interface components
│   └── utils/                # Utility functions
├── tests/                    # Test suite
│   └── test_core.py          # Core functionality tests
├── docs/                     # Documentation
└── examples/                 # Usage examples
```

## 🤝 Contributing

Contributions are welcome! Whether it's bug fixes, feature additions, or documentation improvements, please feel free to open a pull request. Please make sure all tests pass before submitting.

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
