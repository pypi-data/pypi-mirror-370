import os
import sys
import requests
import click
from rich.console import Console

console = Console()

API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemma-3n-e2b-it:generateContent"

@click.command()
@click.argument("prompt", nargs=-1)
@click.option("--limit", default=100, help="Max output tokens")
def main(prompt, limit):
    """Gemini CLI: Ask Google Gemini from your terminal."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        console.print("[red]Error:[/red] Set GEMINI_API_KEY environment variable.")
        sys.exit(1)

    text = " ".join(prompt)
    payload = {
        "contents": [{"parts": [{"text": text}]}],
        "generationConfig": {"maxOutputTokens": limit},
    }

    response = requests.post(
        f"{API_URL}?key={api_key}",
        headers={"Content-Type": "application/json"},
        json=payload,
    )

    if response.status_code == 200:
        data = response.json()
        output = data["candidates"][0]["content"]["parts"][0]["text"]
        console.print(output)
    else:
        console.print(f"[red]Error {response.status_code}[/red]: {response.text}")
