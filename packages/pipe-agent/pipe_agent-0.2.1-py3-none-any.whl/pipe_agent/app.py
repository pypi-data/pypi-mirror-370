import sys
import json
from typing import Optional, List

from .cli import build_parser
from .config import ConfigLoader, Config, Model
from .api import ApiClient
from .processing import ContextManager, CotProcessor, PromptBuilder
from .exceptions import PipeAgentError, ConfigError

class PipeAgentApp:

    def _select_model(self, config: Config, model_identifier: Optional[str], model_provider_identifier: Optional[str]) -> Model:
        if model_identifier and model_provider_identifier:
            raise ConfigError("Cannot use -m and -M at the same time.")

        # --- User-specified model ---
        if model_identifier:
            parts = model_identifier.split('@')
            model_name = parts[0].lower()
            provider_name = parts[1].lower() if len(parts) > 1 else None
            
            candidates = []
            for m in config.models:
                # Match name or alias
                is_model_match = m.model_name.lower() == model_name or model_name in [a.lower() for a in m.model_alias]
                if is_model_match:
                    if provider_name is None or m.provider_name.lower() == provider_name:
                        candidates.append(m)
            
            if not candidates:
                raise ConfigError(f"Model '{model_identifier}' not found.")
            if len(candidates) > 1 and provider_name is None:
                providers = [c.provider_name for c in candidates]
                raise ConfigError(
                    f"Model name '{model_name}' is ambiguous. "
                    f"Please specify a provider: {', '.join(providers)}"
                )
            return candidates[0]

        if model_provider_identifier:
            parts = model_provider_identifier.split('@')
            provider_name = parts[0].lower()
            model_name = parts[1].lower() if len(parts) > 1 else None

            # This case is less common, so a simple loop is fine.
            # In a real-world scenario with many models, you might pre-process into a dict.
            for m in config.models:
                is_provider_match = m.provider_name.lower() == provider_name
                is_model_match = m.model_name.lower() == model_name or model_name in [a.lower() for a in m.model_alias]
                if is_provider_match and is_model_match:
                    return m
            raise ConfigError(f"Model '{model_provider_identifier}' not found.")

        # --- Default model from metrics ---
        default_metric = config.model_registry.metrics.get('default')
        if not default_metric:
            raise ConfigError("No 'default' metric found in models.yaml to select a default model.")
            
        # Levels are assumed to be sorted by preference (e.g., higher is better)
        for level in default_metric:
            for model_ref in level.models:
                # Find the first model in the list that is actually configured
                ref_parts = model_ref.split('@')
                ref_model_name = ref_parts[0]
                ref_provider_name = ref_parts[1] if len(ref_parts) > 1 else None

                for m in config.models:
                    is_model_match = m.model_name == ref_model_name or ref_model_name in m.model_alias
                    is_provider_match = ref_provider_name is None or m.provider_name == ref_provider_name
                    if is_model_match and is_provider_match:
                        return m # Return the first valid model found based on metric order
        
        raise ConfigError("No valid default model could be found from the 'default' metric in models.yaml.")


    def run(self):
        try:
            parser = build_parser()
            args = parser.parse_args()

            # Initialize and Load configuration
            config_loader = ConfigLoader()
            config_loader.initialize_default_configs()
            config = config_loader.load(args.conf_files)

            # Select model
            model = self._select_model(config, args.model_identifier, args.model_provider_identifier)

            if not model.api_key_config.keys or model.api_key_config.keys[0] == "sk-YOUR_API_KEY_HERE":
                raise PipeAgentError(
                    f"API key for model '{model.model_name}' is a placeholder. "
                    f"Please edit your provider configuration file for '{model.provider_name}'."
                )

            # --- Step 1 & 2: Collect and build main prompt from parts ---
            main_prompt_parts = []
            
            if args.prompt:
                positional_separator = " " if config.prompt_concat_sp else ""
                main_prompt_parts.append(positional_separator.join(args.prompt))
                
            if args.prompt_file:
                with open(args.prompt_file, 'r') as f:
                    main_prompt_parts.append(f.read())

            nl_separator = "\n" if config.prompt_concat_nl else ""
            main_prompt_content = nl_separator.join(main_prompt_parts)

            # --- Step 3: Handle stdin ---
            read_single_line = args.stop_at_newline or config.stop_at_newline
            history_json = ""
            if not sys.stdin.isatty():
                if args.context_mode and 'i' in args.context_mode:
                    history_json = sys.stdin.read()  # History always reads the whole file
                else:
                    stdin_content = ""
                    if read_single_line:
                        stdin_content = sys.stdin.readline().strip()
                    else:
                        stdin_content = sys.stdin.read()
                    
                    if stdin_content:
                        if main_prompt_content:
                            main_prompt_content += nl_separator + stdin_content
                        else:
                            main_prompt_content = stdin_content
            
            if not main_prompt_content and sys.stdin.isatty():
                prompt_message = "Enter prompt (Press Enter to send):" if read_single_line else "Enter prompt (Ctrl+D to send):"
                print(prompt_message, file=sys.stderr, flush=True)
                if read_single_line:
                    main_prompt_content = sys.stdin.readline().strip()
                else:
                    main_prompt_content = sys.stdin.read()

            # --- Step 4: Validation ---
            if not main_prompt_content:
                 raise PipeAgentError("Prompt cannot be empty.")

            # Build the final prompt
            prompt_builder = PromptBuilder(config, args)
            final_prompt = prompt_builder.build(main_prompt_content)

            if args.verbose >= 1:
                print("--- Final User Prompt ---", file=sys.stderr)
                print(final_prompt, file=sys.stderr)
                print("-------------------------", file=sys.stderr)

            # Build message list
            context_manager = ContextManager()
            messages = context_manager.build_message_list(
                config.system_prompt, final_prompt, history_json
            )

            if args.verbose >= 2:
                print("--- Full Messages JSON ---", file=sys.stderr)
                print(json.dumps(messages, indent=2, ensure_ascii=False), file=sys.stderr)
                print("--------------------------", file=sys.stderr)

            # Determine SSE
            use_sse = model.enable_sse
            if config.enable_sse is not None:
                use_sse = config.enable_sse
            if args.use_sse is not None:
                use_sse = args.use_sse == 'true'

            # Make API call
            api_client = ApiClient(model)
            response_iterator = api_client.call(messages, use_sse)
            
            # Process and print output
            stream_to_stdout = not (args.context_mode and 'o' in args.context_mode)
            assistant_response = ""
            cot_processor = self._setup_cot_processor(args, config, model)

            for chunk in response_iterator:
                processed_chunk = cot_processor.filter(chunk) if cot_processor else chunk
                if stream_to_stdout:
                    print(processed_chunk, end='', flush=True)
                assistant_response += chunk

            messages.append({"role": "assistant", "content": assistant_response})
            
            if not stream_to_stdout: # This means context mode with output
                final_output = context_manager.format_history_json(messages)
                print(final_output)
            else:
                # For modes that don't output history JSON, add a final newline.
                print()

        except PipeAgentError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.", file=sys.stderr)
            sys.exit(1)

    def _setup_cot_processor(self, args, config, model):
        # Command line arg takes highest precedence
        if args.cot_tag is not None: # This could be True or a string
            tag = args.cot_tag if isinstance(args.cot_tag, str) else None
            return CotProcessor(tag)
        
        # Then config file setting
        if config.enable_cot is not None:
            if config.enable_cot:
                return CotProcessor(config.cot_tag)
            else:
                return None # Explicitly disabled
        
        # Finally model setting
        if model.enable_cot:
            return CotProcessor(model.cot_tag)
            
        return None


