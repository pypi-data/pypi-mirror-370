import re
import json
from typing import List, Optional, Dict

class CotProcessor:
    def __init__(self, cot_tag: Optional[str]):
        if cot_tag:
            safe_tag = re.escape(cot_tag)
            self.pattern = re.compile(f"<{safe_tag}>(.*?)</{safe_tag}>", re.DOTALL)
        else:
            self.pattern = re.compile(r"<think>(.*?)</think>|<thinking>(.*?)</thinking>", re.DOTALL)

    def filter(self, text: str) -> str:
        return self.pattern.sub("", text)

class ContextManager:
    def build_message_list(
        self,
        system_prompt: Optional[str],
        prompt: str,
        history_json: str,
    ) -> List[Dict[str, str]]:
        messages = []
        
        if history_json:
            try:
                messages.extend(json.loads(history_json))
            except json.JSONDecodeError:
                pass # Assuming valid JSON per spec.

        if system_prompt and not any(m['role'] == 'system' for m in messages):
            messages.insert(0, {"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        return messages

    def format_history_json(self, history: List[Dict[str, str]]) -> str:
        return json.dumps(history, indent=2)

class PromptBuilder:
    def __init__(self, config, args):
        self.config = config
        self.args = args

    def build(self, main_prompt: str) -> str:
        separator = "\n" if self.config.prompt_concat_nl else ""
        
        parts = []

        if self.config.prompt_before:
            parts.append(self.config.prompt_before)
        
        if self.args.prompt_before:
            parts.extend(self.args.prompt_before)
            
        parts.append(main_prompt)

        if self.args.prompt_after:
            parts.extend(self.args.prompt_after)

        if self.config.prompt_after:
            parts.append(self.config.prompt_after)
            
        return separator.join(p for p in parts if p)
