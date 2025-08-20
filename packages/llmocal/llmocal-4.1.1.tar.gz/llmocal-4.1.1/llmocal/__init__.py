"""
LLMocal: Professional Local AI Client

⚠️  DEVELOPMENT NOTICE ⚠️
This software is currently under active development and is NOT intended for 
production use. Features may change, break, or be removed without notice.
Use at your own risk in development/testing environments only.

A professional-grade, open-source client for running large language models
locally with complete privacy and control. Built for developers who want to
integrate local AI capabilities without vendor lock-in.

🌟 Key Features:
- 🔒 100% Private & Offline: Your data never leaves your machine
- 🚀 High Performance: Optimized for Apple Silicon (M1/M2/M3/M4)
- 🔧 Multiple Model Support: GGUF, Safetensors, and more
- 🎯 Professional API: Clean, intuitive Python interface
- ⚙️  Flexible Configuration: Customize everything to your needs
- 🧪 Developer Friendly: Explicit model management, clear error messages

📦 Installation:
    pip install llmocal

🚀 Quick Start:
    >>> import llmocal
    >>> 
    >>> # First time setup - explicit model download (recommended)
    >>> client = llmocal.LLMocal()
    >>> client.download_model()  # Downloads ~4.4GB Mistral-7B model
    >>> client.setup()           # Load the model into memory
    >>> response = client.chat("Explain quantum computing in simple terms")
    >>> print(response)
    >>> 
    >>> # Alternative: auto-download if needed
    >>> client = llmocal.LLMocal()
    >>> client.setup(auto_download=True)  # Downloads if model missing
    >>> 
    >>> # Use different models
    >>> client = llmocal.LLMocal(
    ...     repo_id="TheBloke/CodeLlama-7B-Instruct-GGUF",
    ...     filename="codellama-7b-instruct.Q4_K_M.gguf"
    ... )
    >>> client.download_model()
    >>> client.setup()
    >>> code = client.chat("Write a Python function to calculate fibonacci")
    >>> print(code)

🔧 Advanced Configuration:
    >>> from llmocal import LLMocalConfig
    >>> 
    >>> # Custom performance settings
    >>> config = LLMocalConfig(
    ...     n_ctx=8192,         # Larger context window
    ...     n_threads=8,        # More CPU threads
    ...     n_gpu_layers=35     # GPU acceleration (if available)
    ... )
    >>> client = llmocal.LLMocal(config=config)
    >>> client.setup(auto_download=True)

💡 Design Philosophy:
    - Explicit is better than implicit: No surprise downloads
    - Developer control: You decide when and what to download
    - Clear error messages: Helpful guidance when things go wrong
    - Professional packaging: Follows modern Python standards

⚠️  IMPORTANT DISCLAIMERS:
    - This is DEVELOPMENT software - not production ready
    - Models are large (4GB+) and require significant system resources
    - First download may take time depending on your internet connection
    - GPU support requires compatible hardware and drivers
    - Some features may be incomplete or subject to change

📚 For more information:
    - GitHub: https://github.com/alexnicita/llmocal
    - Issues: https://github.com/alexnicita/llmocal/issues
    - Documentation: https://github.com/alexnicita/llmocal#readme

Author: Alex Nicita <alex@llmocal.dev>
License: MIT
Version: 4.1.1
"""

__version__ = "4.1.1"
__author__ = "Alex Nicita"
__email__ = "alex@llmocal.dev"
__description__ = "Professional open source client for running large language models locally"

# Public API - Import main classes for easy access
try:
    from .core.engine import LLMEngine
    from .core.config import LLMocalConfig
    from .models.manager import ModelManager
    from .core.chat import ChatInterface
except ImportError:
    # Handle import errors gracefully during installation
    pass

# Convenience class for easy usage
class LLMocal:
    """High-level interface to LLMocal for easy usage.
    
    This class provides a simple way to get started with LLMocal
    without needing to understand the internal architecture.
    """
    
    def __init__(self, repo_id=None, filename=None, config=None):
        """Initialize LLMocal client.
        
        Args:
            repo_id: Hugging Face repository ID (e.g., "TheBloke/Mistral-7B-Instruct-v0.2-GGUF")
            filename: Model filename (e.g., "mistral-7b-instruct-v0.2.Q4_K_M.gguf")
            config: LLMocalConfig instance for advanced configuration
        """
        try:
            from .core.config import LLMocalConfig
            from .models.manager import ModelManager
            from .core.engine import LLMEngine
            from .core.chat import ChatInterface
        except ImportError as e:
            raise ImportError(
                f"Failed to import LLMocal components: {e}\n"
                "Please ensure all dependencies are installed: pip install llmocal"
            )
            
        self.config = config or LLMocalConfig()
        if repo_id:
            self.config.model_repo_id = repo_id
        if filename:
            self.config.model_filename = filename
            
        self.model_manager = ModelManager()
        self.engine = None
        self.chat_interface = None
        self._model_path = None
    
    def setup(self, auto_download=False):
        """Set up the engine with a model.
        
        Args:
            auto_download: If True, downloads model if not found locally.
                         If False (default), requires model to exist locally.
        
        Returns:
            Self for method chaining
            
        Raises:
            RuntimeError: If model is not found and auto_download=False
            FileNotFoundError: If specified model file doesn't exist locally
        """
        # Check if model exists locally first
        model_path = self.model_manager.get_model_path(
            self.config.model_repo_id, 
            self.config.model_filename
        )
        
        if model_path.exists():
            self._model_path = model_path
        elif auto_download:
            self._model_path = self.model_manager.download_model_if_needed(
                self.config.model_repo_id, 
                self.config.model_filename
            )
            if not self._model_path:
                raise RuntimeError("Failed to download model")
        else:
            raise FileNotFoundError(
                f"Model not found at {model_path}\n\n"
                f"To download the model automatically, use:\n"
                f"  client.setup(auto_download=True)\n\n"
                f"Or download manually:\n"
                f"  client.download_model()\n"
                f"  client.setup()\n\n"
                f"Or specify a different model:\n"
                f"  client = LLMocal(repo_id='your-repo', filename='your-file.gguf')"
            )
        
        self.engine = LLMEngine(self._model_path, self.config)
        self.engine.load_model()
        return self
    
    def download_model(self):
        """Download the configured model.
        
        Returns:
            Path to the downloaded model
        """
        from rich.console import Console
        console = Console()
        
        console.print(f"[bold blue]📥 Downloading model...[/bold blue]")
        console.print(f"  Repository: {self.config.model_repo_id}")
        console.print(f"  Filename: {self.config.model_filename}")
        
        model_path = self.model_manager.download_model_if_needed(
            self.config.model_repo_id,
            self.config.model_filename
        )
        
        if model_path:
            console.print(f"[bold green]✅ Model downloaded successfully![/bold green]")
            console.print(f"  Location: {model_path}")
            return model_path
        else:
            raise RuntimeError("Failed to download model")
    
    def chat(self, message):
        """Send a message and get a response.
        
        Args:
            message: The message to send to the AI
            
        Returns:
            The AI's response as a string
        """
        if not self.engine:
            raise RuntimeError("Please call setup() first")
            
        # Format the message for the model
        formatted_prompt = f"[INST] {message} [/INST]"
        
        # Collect the streaming response
        response_parts = []
        for token in self.engine.generate_response(formatted_prompt):
            response_parts.append(token)
        
        return "".join(response_parts).strip()
    
    def start_interactive_chat(self):
        """Start an interactive chat session."""
        if not self.engine:
            raise RuntimeError("Please call setup() first")
            
        if not self.chat_interface:
            self.chat_interface = ChatInterface(self.config)
            self.chat_interface.setup(self._model_path)
        
        self.chat_interface.start_chat_loop()

__all__ = [
    "__version__",
    "__author__",
    "__description__",
    "LLMocal",
    "LLMEngine", 
    "LLMocalConfig",
    "ModelManager",
    "ChatInterface",
]
