import os
import yaml
from dataclasses import dataclass, field
from dotenv import load_dotenv
from typing import Optional, List, Dict, Any, Union

from .exceptions import ConfigError

@dataclass
class ApiKeyConfig:
    """Configuration for API key usage."""
    keys: List[str] = field(default_factory=list)
    mode: str = "sequential"  # "sequential" or "random"
    max_retries: int = 1

@dataclass
class Model:
    """Represents a fully configured model, after merging provider and model-specific settings."""
    # Identity
    provider_name: str
    model_id: str  # The identifier used in API calls (e.g., gpt-4-turbo)
    model_name: str  # User-facing name for selection, defaults to model_id
    model_alias: List[str]

    # Provider Info
    api_base_url: str
    api_key_config: ApiKeyConfig

    # Behavior settings
    enable_sse: bool = True
    enable_cot: bool = False
    cot_tag: Optional[str] = None
    temperature: float = -1.0

@dataclass
class MetricLevel:
    """A level within a metric, containing models."""
    level: Union[int, str]
    models: List[str]
    description: Optional[str] = None

@dataclass
class ModelRegistry:
    """Structure of the main models.yaml file."""
    enabled_providers: List[str] = field(default_factory=list)
    metrics: Dict[str, List[MetricLevel]] = field(default_factory=dict)

@dataclass
class Config:
    system_prompt: Optional[str] = None
    enable_cot: Optional[bool] = None
    cot_tag: Optional[str] = None
    enable_sse: Optional[bool] = None
    prompt_before: Optional[str] = None
    prompt_after: Optional[str] = None
    prompt_concat_nl: bool = True
    prompt_concat_sp: bool = True
    stop_at_newline: bool = False
    
    # New structured model configuration
    model_registry: ModelRegistry = field(default_factory=ModelRegistry)
    models: List[Model] = field(default_factory=list)

class ConfigLoader:
    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = os.path.expanduser(
            config_dir or os.getenv("PIPE_AGENT_CONFIG_PATH", "~/.config/pipe-agent")
        )
        os.makedirs(self.config_dir, exist_ok=True)
        os.makedirs(os.path.join(self.config_dir, "models"), exist_ok=True)

    def initialize_default_configs(self):
        conf_path = os.path.join(self.config_dir, "default.conf")
        if not os.path.exists(conf_path):
            conf_template = """# This is the default configuration file for pipe-agent.
# You can copy this file to 'default.local' to override settings safely.

# --- Prompting ---
# SYSTEM_PROMPT: A default system prompt to be used for all conversations.
# SYSTEM_PROMPT=You are a helpful AI assistant.

# PROMPT_BEFORE: Text to prepend to every prompt.
# PROMPT_BEFORE=

# PROMPT_AFTER: Text to append to every prompt.
# PROMPT_AFTER=

# PROMPT_CONCAT_NL: Whether to join prompt parts (-B, main, -A) with a newline.
# Default: true
# PROMPT_CONCAT_NL=true

# PROMPT_CONCAT_SP: Whether to join positional prompt arguments with a space.
# Default: true
# PROMPT_CONCAT_SP=true

# STOP_AT_NEWLINE: Stop reading from stdin at the first newline.
# Default: false
# STOP_AT_NEWLINE=false

# --- Chain-of-Thought (CoT) ---
# ENABLE_COT: Default setting for CoT filtering (true, false, default).
# 'default' uses the model's own setting.
# ENABLE_COT=default

# COT_TAG: Default tag for CoT filtering if ENABLE_COT is true.
# COT_TAG=

# --- Streaming (SSE) ---
# ENABLE_SSE: Default setting for streaming (true, false, default).
# 'default' uses the model's own setting.
# ENABLE_SSE=default
"""
            with open(conf_path, 'w') as f:
                f.write(conf_template)

        models_yaml_path = os.path.join(self.config_dir, "models.yaml")
        if not os.path.exists(models_yaml_path):
            models_yaml_template = """# This file configures model priorities and metrics.
# It determines which model providers are active and how models are selected by default.

providers:
  # List of enabled provider configuration files (without the .yaml extension).
  # The order determines the priority when a model is requested without a specific provider.
  # The tool will look for files in the 'models/' subdirectory of your config folder.
  # Example: 'OpenAI' corresponds to 'models/OpenAI.yaml'.
  enabled:
    - CONFIG_ME_BEFORE_USE
    - OpenAI

models:
  metrics:
    # 'default' is the primary metric used for selecting a model when none is specified.
    # It ranks models based on general capability.
    default:
      - level: 5
        models:
          # You can specify a model by its name/alias, or name@provider.
          - Railgun
          - gpt-3.5
          - gpt-4@OpenAI
    
    # You can define custom metrics for specific needs.
    # For example, ranking models by cost.
    cost:
      - level: 2
        description: "Low cost models"
        models:
          - CONFIG_OR_REMOVE_ME
"""
            with open(models_yaml_path, 'w') as f:
                f.write(models_yaml_template)

        # Create an example provider config if it doesn't exist
        example_provider_path = os.path.join(self.config_dir, "models", "OpenAI.yaml")
        if not os.path.exists(example_provider_path):
            provider_template = """# This is an example configuration file for the 'OpenAI' provider.
# File name (without .yaml) is used as the provider name.

provider:
  # The base URL for the API.
  api_base_url: "https://api.openai.com/v1/chat/completions"

  # API key configuration.
  openai_api_key:
    # A list of API keys. The tool will cycle through them based on the mode.
    keys:
      - "sk-YOUR_API_KEY_HERE"
    
    # 'sequential' or 'random'.
    mode: "sequential"
    
    # Number of retries before failing. -1 for infinite (iterate through all keys).
    max_retries: 1

  # Default settings for all models from this provider.
  # These can be overridden in the individual model configurations below.
  defaults:
    enable_sse: true
    temperature: 1.0

# A list of models offered by this provider.
models:
  - model_id: "gpt-4-turbo"
    model_name: "gpt4-turbo" # A friendly name for CLI selection
    model_alias: ["gpt4t"] # Optional aliases

  - model_id: "gpt-3.5-turbo"
    model_name: "gpt3.5-turbo"
    model_alias: ["gpt35"]
    # Override a default setting
    enable_sse: false
"""
            with open(example_provider_path, 'w') as f:
                f.write(provider_template)
    
    def _find_valid_path(self, path: str) -> str:
        if os.path.isabs(path):
            if os.path.exists(path):
                return path
        else:
            search_paths = [
                os.path.join(os.getcwd(), path),
                os.path.join(os.getcwd(), f"{path}.local"),
                os.path.join(self.config_dir, path),
                os.path.join(self.config_dir, f"{path}.local"),
            ]
            for p in search_paths:
                if os.path.exists(p):
                    return p
        raise ConfigError(f"Configuration file not found for path: {path}")

    def load(self, conf_files: Optional[List[str]] = None) -> Config:
        # 1. Load default .conf file
        default_local_path = os.path.join(self.config_dir, "default.local")
        if os.path.exists(default_local_path):
            load_dotenv(default_local_path)
        else:
            default_path = os.path.join(self.config_dir, "default.conf")
            if os.path.exists(default_path):
                load_dotenv(default_path)
        
        # 2. Load user-specified .conf files, overriding previous ones
        if conf_files:
            for conf_file in conf_files:
                found_path = self._find_valid_path(conf_file)
                load_dotenv(found_path, override=True)

        # 3. Load model registry and provider configurations
        models_yaml_path = os.path.join(self.config_dir, "models.yaml")
        if not os.path.exists(models_yaml_path):
            raise ConfigError("models.yaml not found. Please run the application once to generate default configs.")

        with open(models_yaml_path, 'r') as f:
            registry_data = yaml.safe_load(f)
        
        registry = ModelRegistry(
            enabled_providers=registry_data.get('providers', {}).get('enabled', []),
            metrics={k: [MetricLevel(**level) for level in v] for k, v in registry_data.get('models', {}).get('metrics', {}).items()}
        )

        all_models = []
        for provider_name in registry.enabled_providers:
            provider_conf_path = os.path.join(self.config_dir, "models", f"{provider_name}.yaml")
            if not os.path.exists(provider_conf_path):
                # Consider warning the user
                continue
            
            with open(provider_conf_path, 'r') as f:
                provider_data = yaml.safe_load(f)

            provider_section = provider_data.get('provider', {})
            api_key_data = provider_section.get('openai_api_key', {})
            api_key_config = ApiKeyConfig(
                keys=api_key_data.get('keys', []),
                mode=api_key_data.get('mode', 'sequential'),
                max_retries=api_key_data.get('max_retries', 1)
            )

            provider_defaults = provider_section.get('defaults', {})

            for model_data in provider_data.get('models', []):
                # Merge provider defaults with model-specific settings
                model_settings = {**provider_defaults, **model_data}
                
                model = Model(
                    provider_name=provider_name,
                    model_id=model_settings.get('model_id'),
                    model_name=model_settings.get('model_name', model_settings.get('model_id')),
                    model_alias=model_settings.get('model_alias', []),
                    api_base_url=provider_section.get('api_base_url'),
                    api_key_config=api_key_config,
                    enable_sse=model_settings.get('enable_sse', True),
                    enable_cot=model_settings.get('enable_cot', False),
                    cot_tag=model_settings.get('cot_tag'),
                    temperature=model_settings.get('temperature', -1.0)
                )
                all_models.append(model)

        # 4. Populate Config object from environment for non-model settings
        enable_cot_str = os.getenv("ENABLE_COT", "default").lower()
        enable_cot = None
        if enable_cot_str == 'true':
            enable_cot = True
        elif enable_cot_str == 'false':
            enable_cot = False

        enable_sse_str = os.getenv("ENABLE_SSE", "default").lower()
        enable_sse = None
        if enable_sse_str == 'true':
            enable_sse = True
        elif enable_sse_str == 'false':
            enable_sse = False
            
        prompt_concat_nl = os.getenv("PROMPT_CONCAT_NL", "true").lower() == 'true'
        prompt_concat_sp = os.getenv("PROMPT_CONCAT_SP", "true").lower() == 'true'
        stop_at_newline = os.getenv("STOP_AT_NEWLINE", "false").lower() == 'true'

        return Config(
            system_prompt=os.getenv("SYSTEM_PROMPT"),
            enable_cot=enable_cot,
            cot_tag=os.getenv("COT_TAG"),
            enable_sse=enable_sse,
            prompt_before=os.getenv("PROMPT_BEFORE"),
            prompt_after=os.getenv("PROMPT_AFTER"),
            prompt_concat_nl=prompt_concat_nl,
            prompt_concat_sp=prompt_concat_sp,
            stop_at_newline=stop_at_newline,
            model_registry=registry,
            models=all_models,
        )
