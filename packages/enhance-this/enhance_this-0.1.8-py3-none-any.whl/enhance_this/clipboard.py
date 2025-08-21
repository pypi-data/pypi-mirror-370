import pyperclip
from rich.console import Console

console = Console()

def copy_to_clipboard(text: str):
    """Copies the given text to the clipboard."""
    try:
        pyperclip.copy(text)
        console.print("[green]✔[/green] Enhanced prompt copied to clipboard.")
    except pyperclip.PyperclipException:
        console.print("[yellow]⚠[/yellow] Could not copy to clipboard. `xclip` or `xsel` may be required on Linux.")
