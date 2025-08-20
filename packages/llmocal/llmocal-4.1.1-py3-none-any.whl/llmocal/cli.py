"""
Command-Line Interface for LLMocal.

This module provides the main entry point for the command-line interface,
allowing users to interact with the chat application.
"""

import click
from rich.console import Console

from .core.chat import ChatInterface
from .core.config import LLMocalConfig
from .models.manager import ModelManager
from . import __version__

@click.group()
@click.version_option(version=__version__)
def main():
    """
    LLMocal: Professional Local AI Client
    """
    pass

@main.command()
@click.option("--model", default=None, help="The model to use.")
@click.option("--repo-id", default=None, help="The Hugging Face repository ID.")
@click.option("--filename", default=None, help="The model filename.")
def chat(model, repo_id, filename):
    """
    Starts an interactive chat session.
    """
    console = Console()
    config = LLMocalConfig()

    if model:
        # Here you would have logic to select a model from the config
        pass

    repo_id = repo_id or config.model_repo_id
    filename = filename or config.model_filename

    model_manager = ModelManager()
    model_path = model_manager.download_model_if_needed(repo_id, filename)

    if not model_path:
        console.print("[bold red]Failed to download the model. Exiting.[/bold red]")
        return

    chat_interface = ChatInterface(config)
    chat_interface.setup(model_path)
    chat_interface.start_chat_loop()

if __name__ == "__main__":
    main()

