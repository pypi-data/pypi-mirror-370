import argparse
from typing import List, Optional, Any
import argcomplete

from .config import ConfigLoader, Model
from .exceptions import ConfigError

def get_model_provider_tuples(config_loader: ConfigLoader) -> List[tuple[str, str]]:
    """Helper to load config and get (model_name, provider_name) tuples."""
    try:
        config = config_loader.load()
        tuples = []
        for m in config.models:
            tuples.append((m.model_name, m.provider_name))
            for alias in m.model_alias:
                tuples.append((alias, m.provider_name))
        return tuples
    except ConfigError:
        return []

class ModelCompleter:
    """Completes model[@provider]."""
    def __init__(self, config_loader: ConfigLoader):
        self.config_loader = config_loader

    def __call__(self, prefix: str, **kwargs: Any) -> List[str]:
        parts = prefix.split('@')
        model_prefix = parts[0]
        provider_prefix = parts[1] if len(parts) > 1 else ''
        
        suggestions = []
        for model, provider in get_model_provider_tuples(self.config_loader):
            if model.startswith(model_prefix) and provider.startswith(provider_prefix):
                if len(parts) > 1:
                    suggestions.append(f"{model}@{provider}")
                else:
                    suggestions.append(model)
        return suggestions

class ProviderCompleter:
    """Completes provider[@model]."""
    def __init__(self, config_loader: ConfigLoader):
        self.config_loader = config_loader

    def __call__(self, prefix: str, **kwargs: Any) -> List[str]:
        parts = prefix.split('@')
        provider_prefix = parts[0]
        model_prefix = parts[1] if len(parts) > 1 else ''
        
        suggestions = []
        # Suggest unique provider names first
        unique_providers = sorted(list(set(p for _, p in get_model_provider_tuples(self.config_loader))))
        print(unique_providers)
        if len(parts) == 1:
            for provider in unique_providers:
                if provider.startswith(provider_prefix):
                    suggestions.append(provider)

        # Then suggest full provider@model
        for model, provider in get_model_provider_tuples(self.config_loader):
            if provider.startswith(provider_prefix) and model.startswith(model_prefix):
                suggestions.append(f"{provider}@{model}")
        
        return suggestions


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="A simple command-line tool for GPT interaction.")
    
    config_loader = ConfigLoader()

    parser.add_argument(
        '-f', '--file', 
        dest='conf_files',
        action='append',
        help="Specify configuration files to load. Can be used multiple times. Overrides previous settings."
    )
    
    parser.add_argument(
        '-m', '--model', 
        dest='model_identifier',
        help="Specify model by `model[@provider]`. Matches name or alias."
    ).completer = ModelCompleter(config_loader) # type: ignore

    parser.add_argument(
        '-M', '--model-provider',
        dest='model_provider_identifier',
        help="Specify model by `provider[@model]`. Matches name or alias."
    ).completer = ProviderCompleter(config_loader) # type: ignore

    parser.add_argument(
        '-p', '--prompt-file',
        dest='prompt_file',
        help="Path to a file containing the prompt (relative or absolute)."
    )

    parser.add_argument(
        '-B', '--prompt-before',
        dest='prompt_before',
        action='append',
        help="Add a prompt segment before the main prompt. Can be used multiple times."
    )

    parser.add_argument(
        '-A', '--prompt-after',
        dest='prompt_after',
        action='append',
        help="Add a prompt segment after the main prompt. Can be used multiple times."
    )

    parser.add_argument(
        '-k', '--cot',
        dest='cot_tag',
        nargs='?',
        const=True, # if -k is present without argument
        default=None,
        help="Enable Chain-of-Thought filtering. Optionally specify a custom tag to filter."
    )
    
    parser.add_argument(
        '-sse',
        dest='use_sse',
        choices=['true', 'false'],
        help="Override SSE setting from config files."
    )
    
    parser.add_argument(
        '-c', '--context',
        dest='context_mode',
        nargs='?',
        const='io',
        choices=['i', 'o', 'io'],
        default=None,
        help="Enable context mode. 'i': stdin is history JSON, 'o': stdout is history JSON, 'io': both. Defaults to 'io' if flag is present."
    )

    parser.add_argument(
        '-n', '--stop-at-newline',
        dest='stop_at_newline',
        action='store_true',
        help="Stop reading prompt from stdin at the first newline."
    )

    parser.add_argument(
        '-v', '--verbose',
        action='count',
        default=0,
        help="Increase verbosity. -v prints the final prompt to stderr, -vv prints the full messages JSON to stderr."
    )

    parser.add_argument(
        'prompt',
        nargs='*',
        help="The prompt text. All positional arguments are concatenated. If not provided, reads from stdin."
    )

    argcomplete.autocomplete(parser)
    return parser
