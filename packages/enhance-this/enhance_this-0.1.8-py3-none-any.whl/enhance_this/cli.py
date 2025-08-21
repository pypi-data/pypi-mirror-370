import click
import questionary
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
from .history import save_enhancement, load_history

@click.command()
@click.argument('prompt', required=False)
@click.option('-m', '--model', 'model_name', help='Ollama model to use (auto-selects optimal if not specified)')
@click.option('-t', '--temperature', type=click.FloatRange(0.0, 2.0), help='Temperature for generation (0.0-2.0)')
@click.option('-l', '--length', 'max_tokens', type=int, help='Max tokens for enhancement')
@click.option('-c', '--config', 'config_path', type=click.Path(), help='Configuration file path')
@click.option('-v', '--verbose', is_flag=True, help='Enable verbose output')
@click.option('-n', '--no-copy', is_flag=True, help="Don't copy to clipboard")
@click.option('-o', '--output', 'output_file', type=click.File('w'), help='Save enhanced prompt to file')
@click.option('-s', '--style', type=click.Choice(['detailed', 'concise', 'creative', 'technical', 'json', 'bullets', 'summary', 'formal', 'casual']), help='Enhancement style')
@click.option('--diff', is_flag=True, help='Show a diff between the original and enhanced prompt')
@click.option('--list-models', is_flag=True, help='List available Ollama models')
@click.option('--download-model', 'download_model_name', help='Download specific model from Ollama')
@click.option('--auto-setup', is_flag=True, help='Automatically setup Ollama with optimal model')
@click.option('--history', 'show_history', is_flag=True, help='Show enhancement history.')
@click.option('--interactive', 'is_interactive', is_flag=True, help='Start an interactive enhancement session.')
@click.option('--preload-model', is_flag=True, help='Preload a model to keep it in memory for faster responses.')
@click.version_option()
@click.help_option('-h', '--help')
def enhance(prompt, model_name, temperature, max_tokens, config_path, verbose, no_copy, output_file, style, diff, list_models, download_model_name, auto_setup, show_history, is_interactive, preload_model):
    """
    Enhances a simple prompt using Ollama AI models, displays the enhanced version,
    and automatically copies it to the clipboard.
    """
    console = Console()
    config = load_config(config_path)
    client = OllamaClient(host=config['ollama_host'], timeout=config['timeout'])

    if preload_model:
        available_models = client.list_models()
        if not available_models:
            console.print("[red]✖[/red] No models available to preload. Please run `enhance --auto-setup` first.")
            sys.exit(1)

        preferred_models = config.get('preferred_models', ["llama3.1:8b", "llama3", "mistral"])
        model_to_preload = None
        for model in preferred_models:
            if model in available_models:
                model_to_preload = model
                break
        
        if not model_to_preload:
            model_to_preload = available_models[0]

        client.preload_model(model_to_preload)
        return

    if show_history:
        history_entries = load_history()
        if not history_entries:
            console.print("[yellow]No history found.[/yellow]")
            return

        choices = [
            {
                'name': f"{entry['original_prompt']} -> {entry['enhanced_prompt'][:50]}...",
                'value': entry
            }
            for entry in history_entries
        ]

        selected_entry = questionary.select(
            "Select a history entry to view:",
            choices=choices
        ).ask()

        if selected_entry:
            console.print(Panel(
                f"[bold]Original Prompt:[/bold]\n{selected_entry['original_prompt']}\n\n"
                f"[bold]Enhanced Prompt:[/bold]\n{selected_entry['enhanced_prompt']}\n\n"
                f"[bold]Style:[/bold] {selected_entry['style']} | [bold]Model:[/bold] {selected_entry['model']}",
                title="History Details",
                border_style="green"
            ))

            if questionary.confirm("Copy enhanced prompt to clipboard?").ask():
                copy_to_clipboard(selected_entry['enhanced_prompt'])
                console.print("[green]✔ Copied to clipboard.[/green]")
        return

    if is_interactive:
        console.print("[bold green]Welcome to interactive mode![/bold green]")
        console.print("Type 'quit' or 'exit' to end the session.")

        enhancer = PromptEnhancer(config.get('enhancement_templates'))
        available_styles = list(enhancer.templates.keys())
        
        if not client.is_running():
            console.print("[red]✖[/red] Ollama service is not running or is unreachable.")
            sys.exit(1)

        available_models = client.list_models()
        if not available_models:
            console.print("[red]✖[/red] No models available. Please run `enhance --auto-setup` first.")
            sys.exit(1)

        if model_name and model_name not in available_models:
            console.print(f"[red]✖[/red] Model '{model_name}' not found.")
            sys.exit(1)
        
        final_model = model_name or config.get('preferred_models', ["llama3.1:8b", "llama3", "mistral"])[0]

        console.print(f"Using model: [cyan]{final_model}[/cyan]")
        
        current_prompt = ""
        enhanced_prompt = ""
        current_style = config.get('default_style', 'detailed')

        while True:
            try:
                if not current_prompt:
                    current_prompt = console.input("[bold cyan]Enter initial prompt: [/bold cyan]")
                    if current_prompt.lower() in ['quit', 'exit']:
                        break

                system_prompt = enhancer.enhance(current_prompt, current_style)
                
                enhanced_prompt = ""
                with console.status("[bold green]Enhancing..."):
                    for chunk in client.generate_stream(final_model, system_prompt, 0.7, 2000):
                        enhanced_prompt += chunk
                
                console.print("\n[bold magenta]✨ Enhanced Prompt ✨[/bold magenta]")
                console.print(Panel(Markdown(enhanced_prompt), border_style="green"))

                action = console.input(
                    "[bold]Choose action: (r)efine, (s)tyle, (c)opy, (q)uit: [/bold]"
                ).lower()

                if action == 'r':
                    current_prompt = console.input("[bold cyan]Refine prompt: [/bold cyan]")
                elif action == 's':
                    console.print(f"Available styles: {', '.join(available_styles)}")
                    new_style = console.input(f"[bold cyan]New style ({current_style}): [/bold cyan]")
                    if new_style in available_styles:
                        current_style = new_style
                    elif new_style:
                        console.print(f"[yellow]Invalid style. Sticking with {current_style}.[/yellow]")
                elif action == 'c':
                    copy_to_clipboard(enhanced_prompt)
                    console.print("[green]✔ Copied to clipboard.[/green]")
                elif action == 'q':
                    break
                else:
                    console.print("[yellow]Invalid action.[/yellow]")

            except (KeyboardInterrupt, EOFError):
                break

        console.print("\n[bold green]Exiting interactive mode. Goodbye![/bold green]")
        return

    create_default_config_if_not_exists()
    
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

        preferred_models = config.get('preferred_models', ["llama3.1:8b", "llama3", "mistral"])
        final_model = None
        for model in preferred_models:
            if model in available_models:
                final_model = model
                break
        
        if not final_model:
            if available_models:
                final_model = available_models[0]
            else:
                console.print("[red]✖[/red] No models available. Please download a model first, e.g.:")
                console.print("`enhance --download-model llama3.1:8b` or run `enhance --auto-setup`")
                sys.exit(1)

        if verbose:
            console.print(f"No model specified. Using best available model: [cyan]{final_model}[/cyan]")

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
    with console.status("[bold green]Loading model and enhancing prompt...[/bold green]") as status:
        try:
            stream_generator = client.generate_stream(final_model, system_prompt, final_temperature, final_max_tokens)

            # Stop the status message before starting live display for streaming output
            status.stop()

            # Only use Live for streaming output if a prompt is provided or in interactive mode
            if is_interactive or prompt:
                with Live(console=console, auto_refresh=False) as live:
                    for chunk in stream_generator:
                        enhanced_prompt += chunk
                        live.update(Markdown(enhanced_prompt), refresh=True)
            else: # If not interactive and no prompt, just collect the output
                for chunk in stream_generator:
                    enhanced_prompt += chunk

        except Exception as e:
            console.print(f"\n[red]✖[/red] Error during enhancement: {e}")
            sys.exit(1)

    if enhanced_prompt:
        save_enhancement(prompt, enhanced_prompt, final_style, final_model)
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
    enhance()