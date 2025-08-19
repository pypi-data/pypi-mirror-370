import json
from pathlib import Path
from rich.console import Console

console = Console()
CONFIG_FILE = Path.home() / ".cli_agent_config.json"


def get_api_key(env_var: str = "GEMINI_API_KEY") -> str:
    """
    Retrieves the API key from a config file or prompts the user if missing.
    Saves it for future runs.
    """
    # 1️⃣ Check if environment variable exists
    import os

    api_key = os.getenv(env_var)
    if api_key:
        console.print("[green]✅ Using API key from environment variable[/green]")
        return api_key

    # 2️⃣ Check if config file exists
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                api_key = config.get(env_var)
                if api_key:
                    console.print("[green]✅ Using saved API key[/green]")
                    return api_key
        except Exception:
            pass  # fallback to prompt

    # 3️⃣ Prompt user
    api_key = console.input("[bold blue]Enter your Gemini API key: [/bold blue]")

    # 4️⃣ Save for future use
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump({env_var: api_key}, f)
        console.print(f"[green]✅ API key saved to {CONFIG_FILE}[/green]")
    except Exception as e:
        console.print(f"[red]⚠️ Failed to save API key: {e}[/red]")

    return api_key
