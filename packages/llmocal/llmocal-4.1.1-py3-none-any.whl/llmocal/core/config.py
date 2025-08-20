"""
Configuration management for LLMocal.

This module uses Pydantic for robust and type-safe configuration management.
Settings can be loaded from environment variables or a .env file.
"""

import os
from pydantic import Field
from pydantic_settings import BaseSettings

# Default values for the model if not set in the environment
DEFAULT_REPO_ID = "TheBloke/Mistral-7B-Instruct-v0.2-GGUF"
DEFAULT_FILENAME = "mistral-7b-instruct-v0.2.Q4_K_M.gguf"

class LLMocalConfig(BaseSettings):
    """Configuration settings for LLMocal."""
    
    # Model Configuration
    model_repo_id: str = Field(DEFAULT_REPO_ID, env="MODEL_REPO_ID")
    model_filename: str = Field(DEFAULT_FILENAME, env="MODEL_FILENAME")

    # Llama.cpp Engine Settings
    n_ctx: int = Field(4096, env="N_CTX")
    n_threads: int = Field(os.cpu_count() or 4, env="N_THREADS")
    n_gpu_layers: int = Field(0, env="N_GPU_LAYERS")
    n_batch: int = Field(512, env="N_BATCH")
    use_mlock: bool = Field(True, env="USE_MLOCK")
    use_mmap: bool = Field(True, env="USE_MMAP")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

