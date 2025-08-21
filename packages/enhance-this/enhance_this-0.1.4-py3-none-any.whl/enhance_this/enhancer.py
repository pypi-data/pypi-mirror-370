import importlib.resources
from typing import Dict, Optional
from pathlib import Path
from rich.console import Console

console = Console()

def load_templates(custom_template_paths: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    templates = {}
    package = 'enhance_this.templates'
    
    # Load built-in templates
    try:
        from importlib.resources import files
    except ImportError:
        from importlib_resources import files

    try:
        template_dir = files(package)
        for style in ["detailed", "concise", "creative", "technical"]:
            template_file = template_dir / f"{style}.txt"
            if template_file.is_file():
                 templates[style] = template_file.read_text(encoding='utf-8')
    except Exception:
        for style in ["detailed", "concise", "creative", "technical"]:
            try:
                with importlib.resources.open_text(package, f"{style}.txt") as f:
                    templates[style] = f.read()
            except FileNotFoundError:
                pass

    # Load custom templates from config
    if custom_template_paths:
        for style, path_str in custom_template_paths.items():
            if not isinstance(path_str, str) or not path_str.strip():
                continue # Skip if path is not a valid string
            try:
                path = Path(path_str).expanduser()
                if path.is_file():
                    templates[style] = path.read_text(encoding='utf-8')
                else:
                    console.print(f"[yellow]⚠[/yellow] Custom template for style '{style}' not found at: {path_str}")
            except Exception as e:
                console.print(f"[red]✖[/red] Error loading custom template for style '{style}': {e}")

    return templates

class PromptEnhancer:
    def __init__(self, custom_template_paths: Optional[Dict[str, str]] = None):
        self.templates = load_templates(custom_template_paths)

    def enhance(self, user_prompt: str, style: str) -> str:
        if style not in self.templates:
            available_styles = list(self.templates.keys())
            raise ValueError(f"Unknown style: '{style}'. Available styles: {available_styles}")
        
        template = self.templates[style]
        return template.format(user_prompt=user_prompt)
