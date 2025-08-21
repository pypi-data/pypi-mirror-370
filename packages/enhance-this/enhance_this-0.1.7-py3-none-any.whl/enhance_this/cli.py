import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.live import Live
import sys
import difflib

from .config import load_config, create_default_config_if_not_exists
from .ollama_client import OllamaClient
from .enhancer import PromptEnhancer
from .clipboard import copy_to_clipboard

@click.command()
@click.argument('prompt', required=False)
@click.option('-m', '--model', 'model_name', help='Ollama model to use (auto-selects optimal if not specified)')
@click.option('-t', '--temperature', type=click.FloatRange(0.0, 2.0), help='Temperature for generation (0.0-2.0)')
@click.option('-l', '--length', 'max_tokens', type=int, help='Max tokens for enhancement')
@click.option('-c', '--config', 'config_path', type=click.Path(), help='Configuration file path')
@click.option('-v', '--verbose', is_flag=True, help='Enable verbose output')
@click.option('-n', '--no-copy', is_flag=True, help="Don't copy to clipboard")
@click.option('-o', '--output', 'output_file', type=click.File('w'), help='Save enhanced prompt to file')
@click.option('-s', '--style', type=click.Choice(['detailed', 'concise', 'creative', 'technical']), help='Enhancement style')
@click.option('--diff', is_flag=True, help='Show a diff between the original and enhanced prompt')
@click.option('--list-models', is_flag=True, help='List available Ollama models')
@click.option('--download-model', 'download_model_name', help='Download specific model from Ollama')
@click.option('--auto-setup', is_flag=True, help='Automatically setup Ollama with optimal model')
@click.option('--version', is_flag=True, help='Show version information')
@click.help_option('-h', '--help')
def main(prompt, model_name, temperature, max_tokens, config_path, verbose, no_copy, output_file, style, diff, list_models, download_model_name, auto_setup, version):
    """
    Enhances a simple prompt using Ollama AI models, displays the enhanced version,
    and automatically copies it to the clipboard.
    """
    if version:
        from importlib.metadata import version as get_version
        pkg_version = get_version("enhance-this")
        click.echo(f"enhance-this version {pkg_version}")
        return

    create_default_config_if_not_exists()
    config = load_config(config_path)
    
    console = Console()
    client = OllamaClient(host=config['ollama_host'], timeout=config['timeout'])

    if not client.is_running():
        console.print("[red]✖[/red] Ollama service is not running or is unreachable.")
        console.print("Please start Ollama and try again.")
        sys.exit(1)

    if list_models:
        models = client.list_models()
        if models:
            console.print("[bold green]Available Ollama models:[/bold green]")
            for model in models:
                console.print(f"- {model}")
        else:
            console.print("[yellow]No Ollama models found.[/yellow]")
        return

    if download_model_name:
        console.print(f"Starting download for '{download_model_name}'...")
        client.download_model(download_model_name)
        return
        
    available_models = client.list_models()

    if auto_setup or not available_models:
        if not available_models:
            console.print("[yellow]No models found. Starting auto-setup.[/yellow]")
        else:
            console.print("Starting auto-setup...")
        
        recommended_models = ["llama3.1:8b", "llama3", "mistral"]
        for model_to_try in recommended_models:
            if model_to_try not in available_models:
                console.print(f"Downloading recommended model: {model_to_try}")
                if client.download_model(model_to_try):
                    available_models.append(model_to_try)
                    break 
            else:
                console.print(f"Recommended model '{model_to_try}' is already available.")
                break
        else:
            console.print("[red]✖[/red] Auto-setup failed. Could not download a recommended model.")
            sys.exit(1)

        if auto_setup:
             return

    if not prompt:
        ctx = click.get_current_context()
        click.echo(ctx.get_help())
        ctx.exit()

    if model_name:
        if model_name not in available_models:
            console.print(f"[red]✖[/red] Model '{model_name}' not found. Available models:")
            for model in available_models:
                console.print(f"- {model}")
            sys.exit(1)
        final_model = model_name
    else:
        if not available_models:
            console.print("[red]✖[/red] No models available. Please download a model first, e.g.:")
            console.print("`enhance --download-model llama3.1:8b` or run `enhance --auto-setup`")
            sys.exit(1)
        final_model = available_models[0]
        if verbose:
            console.print(f"No model specified. Using first available model: [cyan]{final_model}[/cyan]")

    final_style = style or config.get('default_style', 'detailed')
    final_temperature = temperature if temperature is not None else config.get('default_temperature', 0.7)
    final_max_tokens = max_tokens or config.get('max_tokens', 2000)
    auto_copy_enabled = not no_copy and config.get('auto_copy', True)

    enhancer = PromptEnhancer(config.get('enhancement_templates'))

    system_prompt = enhancer.enhance(prompt, final_style)

    if verbose:
        console.print("\n[bold]System Prompt:[/bold]")
        console.print(Panel(system_prompt, title="System Prompt", border_style="dim"))

    enhanced_prompt = ""
    console.print("\n[bold magenta]✨ Enhanced Prompt ✨[/bold magenta]")

    status_obj = console.status("[bold green]Enhancing prompt...")
    status_obj.start()

    try:
        stream_generator = client.generate_stream(final_model, system_prompt, final_temperature, final_max_tokens)

        # Stop the status as soon as the generator is ready
        status_obj.stop()

        with Live(console=console, auto_refresh=False) as live:
            for chunk in stream_generator:
                enhanced_prompt += chunk
                live.update(Markdown(enhanced_prompt), refresh=True)
    finally:
        status_obj.stop()

    if enhanced_prompt:
        if diff:
            console.print("\n[bold yellow]↔️  Diff View ↔️[/bold yellow]")
            diff_result = difflib.unified_diff(
                prompt.splitlines(keepends=True),
                enhanced_prompt.splitlines(keepends=True),
                fromfile='Original',
                tofile='Enhanced',
            )
            for line in diff_result:
                if line.startswith('+'):
                    console.print(f"[green]{line}[/green]", end="")
                elif line.startswith('-'):
                    console.print(f"[red]{line}[/red]", end="")
                elif line.startswith('@'):
                    console.print(f"[dim]{line}[/dim]", end="")
                else:
                    console.print(line, end="")

        if output_file:
            output_file.write(enhanced_prompt)
            console.print(f"\n[green]✔[/green] Saved to {output_file.name}")

        if auto_copy_enabled:
            copy_to_clipboard(enhanced_prompt)
    else:
        console.print("\n[red]✖[/red] Failed to generate enhanced prompt.")
        sys.exit(1)

if __name__ == '__main__':
    main()
