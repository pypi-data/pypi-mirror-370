"""
Chat Interface for LLMocal.

Provides the interactive chat functionality with professional
command handling and user experience.
"""

from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.markdown import Markdown

from .config import LLMocalConfig
from .engine import LLMEngine


class ChatInterface:
    """Professional chat interface for LLMocal."""

    def __init__(self, config: Optional[LLMocalConfig] = None):
        """Initializes the chat interface with configuration."""
        self.config = config or LLMocalConfig()
        self.console = Console(highlight=False)
        self.engine: Optional[LLMEngine] = None

    def setup(self, model_path: Path) -> None:
        """Sets up the LLM engine and loads the model."""
        self.engine = LLMEngine(model_path, self.config, self.console)
        self.engine.load_model()

    def display_welcome_message(self) -> None:
        """
        Displays a welcome message and instructions to the user.
        Uses Rich for beautiful rendering.
        """
        welcome_text = f"""
        # 🤖 Welcome to LLMocal!
        
        You are now chatting with an AI model running entirely on your machine.
        
        - **Model:** `{self.config.model_repo_id}` (`{self.config.model_filename}`)
        - **Privacy:** 100% offline and private. No data leaves your computer.
        - **Open Source:** Both the model and client are completely open source.
        
        Type `/exit` or `/quit` to end the chat. Use `/help` for more commands.
        """
        self.console.print(Markdown(welcome_text))

    def handle_command(self, user_input: str) -> bool:
        """
        Handles special commands prefixed with '/'.

        Returns:
            True if the application should exit, False otherwise.
        """
        if user_input.lower() in ["/exit", "/quit", "/bye"]:
            return True
        if user_input.lower() == "/help":
            help_text = """
            **Available Commands:**
            - `/exit`, `/quit`: Exit the chat.
            - `/help`: Show this help message.
            - `/model`: Display information about the current model.
            """
            self.console.print(Markdown(help_text))
        elif user_input.lower() == "/model":
            model_info = f"""
            **Current Model Information:**
            - **Repo ID:** {self.config.model_repo_id}
            - **Filename:** {self.config.model_filename}
            - **Local Path:** {self.engine.model_path if self.engine else 'N/A'}
            - **Context Window:** {self.config.n_ctx} tokens
            - **Threads:** {self.config.n_threads}
            """
            self.console.print(Markdown(model_info))
        else:
            self.console.print(f"[yellow]Unknown command:[/yellow] {user_input}")
        return False

    def start_chat_loop(self) -> None:
        """Starts the main interactive chat session."""
        if not self.engine:
            raise RuntimeError("Chat interface has not been set up.")

        self.display_welcome_message()

        while True:
            try:
                user_input = self.console.input("\n[bold green]You:[/bold green] ").strip()

                if not user_input:
                    continue

                if user_input.startswith("/"):
                    if self.handle_command(user_input):
                        break
                    continue
                
                # Format the prompt for Mistral Instruct models
                prompt = f"[INST] {user_input} [/INST]"
                
                # Header for assistant response
                self.console.print("\n[bold cyan]AI:[/bold cyan] ", end="")
                
                # Generate and stream the response (no spinner/live status for clean output)
                full_response = ""
                response_stream = self.engine.generate_response(prompt)
                for token in response_stream:
                    full_response += token
                    # Write raw tokens directly to stdout for continuous streaming
                    self.console.file.write(token)
                    self.console.file.flush()
                
                # Ensure we end the streamed line cleanly
                self.console.print("")
                
                # For now, we printed the raw response above. Optionally keep full_response for future use.

            except KeyboardInterrupt:
                self.console.print("\n[yellow]Interrupted by user.[/yellow]")
                break
            except Exception as e:
                self.console.print(f"\n[bold red]❌ An unexpected error occurred:[/bold red] {e}")
                # Continue the loop

        self.console.print("\n[bold yellow]👋 Goodbye! Thanks for using LLMocal.[/bold yellow]")
