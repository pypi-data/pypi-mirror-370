#!/usr/bin/env python3
"""
LLMocal Core Engine Module

⚠️  DEVELOPMENT SOFTWARE - NOT FOR PRODUCTION USE ⚠️

This module provides the core LLMEngine class for loading and interacting with
large language models using llama-cpp-python. Designed for high performance
and reliability with explicit error handling and professional logging.

🎯 Key Features:
- 🚀 High-performance model loading with llama.cpp backend
- 🔧 Configurable parameters for optimal performance
- 🎛️  Hardware-specific optimizations (Apple Silicon, GPU, etc.)
- 📊 Detailed logging and error reporting
- 🔄 Streaming response generation
- 🛡️  Robust error handling and recovery

🔧 Usage:
    from llmocal.core.engine import LLMEngine
    from llmocal.core.config import LLMocalConfig
    from pathlib import Path
    
    config = LLMocalConfig(n_ctx=4096, n_threads=8)
    engine = LLMEngine(Path("model.gguf"), config)
    engine.load_model()
    
    for token in engine.generate_response("[INST] Hello! [/INST]"):
        print(token, end="", flush=True)

⚠️  Important Notes:
- This is development software - expect bugs and changes
- Models require significant RAM (4GB+ for typical models)
- First load may take time depending on model size
- GPU support requires compatible hardware and drivers
- Apple Silicon optimization enabled by default

Author: Alex Nicita <alex@llmocal.dev>
License: MIT
"""

import sys
from pathlib import Path
from typing import Generator, Any, Optional

# --- Third-party Imports ---
try:
    from llama_cpp import Llama
    from rich.console import Console
except ImportError as e:
    print(f"❌ Missing essential dependencies: {e}", file=sys.stderr)
    print("   Please run './scripts/start.sh' or 'uv pip sync pyproject.toml' to install them.", file=sys.stderr)
    sys.exit(1)

# --- Local Imports ---
from .config import LLMocalConfig

# --- Core LLM Engine Class ---

class LLMEngine:
    """Professional LLM engine for loading and interacting with language models."""

    def __init__(self, model_path: Path, config: Optional[LLMocalConfig] = None, console: Optional[Console] = None):
        """Initializes the LLM engine with the specified model path and configuration."""
        self.model_path = model_path
        self.config = config or LLMocalConfig()
        self.console = console or Console()
        self.llm: Optional[Llama] = None

    def load_model(self) -> None:
        """Loads the GGUF model into memory using llama-cpp-python."""
        self.console.print("[bold cyan]🚀 Loading model into memory...[/bold cyan]")
        self.console.print(f"   [cyan]Model:[/cyan] {self.model_path.name}")
        self.console.print(f"   [cyan]Context:[/cyan] {self.config.n_ctx} tokens")
        self.console.print(f"   [cyan]Threads:[/cyan] {self.config.n_threads}")
        self.console.print("   This might take a moment...")

        try:
            self.llm = Llama(
                model_path=str(self.model_path),
                n_ctx=self.config.n_ctx,
                n_threads=self.config.n_threads,
                n_gpu_layers=self.config.n_gpu_layers,
                n_batch=self.config.n_batch,
                use_mlock=self.config.use_mlock,
                use_mmap=self.config.use_mmap,
                verbose=False,  # Set to True for detailed llama.cpp output
            )
            self.console.print("[bold green]✅ Model loaded successfully![/bold green]")
        except Exception as e:
            self.console.print(f"[bold red]❌ Fatal Error: Failed to load model.[/bold red]")
            self.console.print(f"   [red]Path:[/red] {self.model_path}")
            self.console.print(f"   [red]Error:[/red] {e}")
            self.console.print("   [yellow]Troubleshooting Tips:[/yellow]")
            self.console.print("   - Ensure the model file is not corrupted.")
            self.console.print("   - If you have an older CPU, it may not support the instructions required by this build.")
            sys.exit(1)

    def generate_response(self, prompt: str) -> Generator[str, Any, None]:
        """
        Generates a streaming response from the model.

        Args:
            prompt: The formatted prompt to send to the model.

        Yields:
            A stream of response tokens from the model.
        """
        if not self.llm:
            raise RuntimeError("Model is not loaded. Cannot generate response.")

        # These settings control the generation process.
        # They are tuned for a good chat experience.
        generation_params = {
            "max_tokens": self.config.n_ctx,      # Max tokens to generate
            "stop": ["[INST]", "</s>"], # Stop generation on these tokens
            "echo": False,             # Don't echo the prompt in the output
            "temperature": 0.7,        # Controls randomness. Lower is more predictable.
            "top_p": 0.9,              # Nucleus sampling
            "repeat_penalty": 1.1,     # Penalize repeating tokens
            "stream": True,            # Enable streaming output
        }

        try:
            stream = self.llm(prompt, **generation_params)
            for chunk in stream:
                if 'choices' in chunk and len(chunk['choices']) > 0:
                    token = chunk['choices'][0].get('text', "")
                    yield token
        except Exception as e:
            self.console.print(f"[bold red]❌ Error during response generation:[/bold red] {e}")
            yield "Sorry, an error occurred while processing your request."
