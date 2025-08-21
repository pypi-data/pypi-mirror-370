import importlib.resources
from typing import Dict, Optional
from pathlib import Path
from rich.console import Console

console = Console()

def load_templates(custom_template_paths: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    templates = {}
    package = 'enhance_this.templates'
    
    # Load built-in templates
    for style in ["detailed", "concise", "creative", "technical"]:
        try:
            # Use read_text directly for simplicity and robustness
            content = importlib.resources.read_text(package, f"{style}.txt")
            templates[style] = content
        except FileNotFoundError:
            # Raise a specific error if a built-in template is not found
            raise RuntimeError(f"Built-in template file not found: {package}/{style}.txt. This indicates a packaging issue.")
        except Exception as e:
            # Raise a specific error for other issues
            raise RuntimeError(f"Error reading built-in template {style}.txt: {e}. This indicates a packaging issue or corruption.")

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

    if not templates:
        # This should now be unreachable if the above loop works
        raise RuntimeError("No built-in templates were loaded. Available styles will be empty. This is unexpected.")

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
