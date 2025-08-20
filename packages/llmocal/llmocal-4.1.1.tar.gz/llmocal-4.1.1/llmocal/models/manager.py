#!/usr/bin/env python3
"""
LLMocal Model Manager

⚠️  DEVELOPMENT SOFTWARE - NOT FOR PRODUCTION USE ⚠️

Handles the download, management, and organization of local AI models
from Hugging Face and other sources. Provides a centralized, professional
interface for all model operations with robust error handling.

🎯 Key Features:
- 📥 Automatic model downloads from Hugging Face Hub
- 📁 Organized local model storage (~/llmocal_models/)
- ⚙️  Intelligent caching and resumable downloads
- 🛡️  Comprehensive error handling and recovery
- 📊 Progress tracking and user feedback
- 🔄 Resume interrupted downloads automatically

💾 Storage Structure:
    ~/llmocal_models/
    ├── TheBloke_Mistral-7B-Instruct-v0.2-GGUF/
    │   └── mistral-7b-instruct-v0.2.Q4_K_M.gguf
    ├── TheBloke_CodeLlama-7B-Instruct-GGUF/
    │   └── codellama-7b-instruct.Q4_K_M.gguf
    └── ...

🚀 Usage:
    from llmocal.models.manager import ModelManager
    
    manager = ModelManager()
    
    # Download a model
    model_path = manager.download_model_if_needed(
        "TheBloke/Mistral-7B-Instruct-v0.2-GGUF",
        "mistral-7b-instruct-v0.2.Q4_K_M.gguf"
    )
    
    # Check if model exists locally
    path = manager.get_model_path(repo_id, filename)
    if path.exists():
        print(f"Model found at: {path}")

⚠️  Important Notes:
- This is development software - expect bugs and API changes
- Models are large (4GB+) - ensure adequate disk space
- First downloads require internet connection and may take time
- Files are stored permanently until manually deleted
- Hugging Face Hub access required for downloads

Author: Alex Nicita <alex@llmocal.dev>
License: MIT
"""

import sys
from pathlib import Path
from typing import Optional
from rich.console import Console
from huggingface_hub import hf_hub_download
from huggingface_hub.utils import HfHubHTTPError

from ..core.config import DEFAULT_REPO_ID, DEFAULT_FILENAME

MODELS_DIR = Path.home() / "llmocal_models"

class ModelManager:
    """Professional model management class for LLMocal."""
    
    def __init__(self, models_dir: Optional[Path] = None):
        self.models_dir = models_dir or MODELS_DIR
        self.console = Console()
    
    def get_model_path(self, repo_id: str = DEFAULT_REPO_ID, filename: str = DEFAULT_FILENAME) -> Path:
        """Constructs the local path for a given model file."""
        # Sanitize the repo_id to create a valid directory name
        safe_repo_name = repo_id.replace("/", "_")
        return self.models_dir / safe_repo_name / filename
    
    def download_model_if_needed(
        self, repo_id: str = DEFAULT_REPO_ID, filename: str = DEFAULT_FILENAME
    ) -> Optional[Path]:
        """
        Downloads the specified model from Hugging Face if it doesn't already exist locally.

        Args:
            repo_id: The repository ID on Hugging Face (e.g., "TheBloke/Mistral-7B-Instruct-v0.2-GGUF").
            filename: The specific model file to download (e.g., "mistral-7b-instruct-v0.2.Q4_K_M.gguf").

        Returns:
            The local path to the downloaded model, or None if an error occurred.
        """
        model_path = self.get_model_path(repo_id, filename)
        
        # Ensure the parent directory for the model exists
        model_path.parent.mkdir(parents=True, exist_ok=True)

        if model_path.exists():
            self.console.print(f"✅ Model already exists at: {model_path}")
            self.console.print(f"   Size: {model_path.stat().st_size / (1024**3):.2f} GB")
            return model_path

        self.console.print(f"📥 Downloading model '{filename}' from '{repo_id}'...")
        self.console.print(f"   This may take a while depending on your internet connection.")
        self.console.print(f"   Destination: {model_path}")

        try:
            # Use hf_hub_download to get the file
            downloaded_path_str = hf_hub_download(
                repo_id=repo_id,
                filename=filename,
                local_dir=str(model_path.parent),
                local_dir_use_symlinks=False,  # Recommended to be False for portability
                resume_download=True,
            )
            
            downloaded_path = Path(downloaded_path_str)
            
            # In new huggingface_hub versions, the file might be downloaded to a different location
            # and then symlinked. We ensure it's at the expected path.
            if downloaded_path.resolve() != model_path.resolve():
                # If the downloaded file is not where we want it, move it.
                # This handles cases where hf_hub_download uses a cache.
                if model_path.exists():
                    model_path.unlink()
                downloaded_path.rename(model_path)

            self.console.print(f"✅ Model downloaded successfully!")
            self.console.print(f"   Size: {model_path.stat().st_size / (1024**3):.2f} GB")
            
            return model_path

        except HfHubHTTPError as e:
            self.console.print(f"❌ HTTP Error downloading model: {e}", file=sys.stderr)
            self.console.print("   Please check the following:", file=sys.stderr)
            self.console.print(f"   1. Your internet connection.", file=sys.stderr)
            self.console.print(f"   2. The model repository ID ('{repo_id}') is correct.", file=sys.stderr)
            self.console.print(f"   3. The filename ('{filename}') exists in the repository.", file=sys.stderr)
            return None
        except Exception as e:
            self.console.print(f"❌ An unexpected error occurred during download: {e}", file=sys.stderr)
            if model_path.exists():
                # Clean up partially downloaded file
                model_path.unlink()
            return None

# Backward compatibility functions (for legacy code)
def get_model_path(repo_id: str = DEFAULT_REPO_ID, filename: str = DEFAULT_FILENAME) -> Path:
    """Legacy function for backward compatibility."""
    manager = ModelManager()
    return manager.get_model_path(repo_id, filename)

def download_model_if_needed(
    repo_id: str = DEFAULT_REPO_ID, filename: str = DEFAULT_FILENAME
) -> Optional[Path]:
    """Legacy function for backward compatibility."""
    manager = ModelManager()
    return manager.download_model_if_needed(repo_id, filename)

if __name__ == "__main__":
    print("--- LLMocal Model Downloader ---")
    manager = ModelManager()
    manager.download_model_if_needed()
