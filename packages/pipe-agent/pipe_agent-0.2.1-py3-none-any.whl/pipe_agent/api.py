import json
import requests
import sseclient
import random
import sys
from typing import Dict, List, Iterator, Generator, Optional

from .config import Model, ApiKeyConfig
from .exceptions import APIError

def _byte_iterator_to_generator(iterator: Iterator[bytes]) -> Generator[bytes, None, None]:
    yield from iterator

class ApiKeyManager:
    """Manages API key selection, rotation, and retry logic."""
    def __init__(self, config: ApiKeyConfig):
        self.config = config
        self.keys = config.keys
        self.current_index = 0
        self.retry_count = 0

        if config.mode == 'random':
            random.shuffle(self.keys)

    def get_key(self) -> Optional[str]:
        """Gets the current API key based on the mode and retry count."""
        if not self.keys:
            return None

        if self.config.max_retries != -1 and self.retry_count >= self.config.max_retries:
            return None
        
        # For sequential mode, advance the key index
        if self.config.mode == 'sequential':
            key_index = self.current_index
            self.current_index = (self.current_index + 1) % len(self.keys)
            # Stop if we've cycled through all keys once
            if self.retry_count > 0 and key_index == 0 and self.config.max_retries == -1:
                 return None
            return self.keys[key_index]
        
        # For random mode, just pick one based on the retry attempt
        # (The list is already shuffled)
        if self.retry_count >= len(self.keys): # Exhausted all keys
             return None
        return self.keys[self.retry_count]


    def record_attempt(self):
        """Records that an API call attempt was made."""
        self.retry_count += 1

class ApiClient:
    def __init__(self, model: Model):
        self.model = model
        self.session = requests.Session()
        self.api_key_manager = ApiKeyManager(self.model.api_key_config)
        self.session.headers.update({
            "Content-Type": "application/json"
        })

    def _update_auth_header(self, api_key: str):
        self.session.headers.update({"Authorization": f"Bearer {api_key}"})

    def call(self, messages: List[Dict[str, str]], use_sse: bool) -> Iterator[str]:
        body = {
            "model": self.model.model_id,
            "messages": messages,
            "stream": use_sse
        }
        
        if 0 <= self.model.temperature <= 2:
            body["temperature"] = self.model.temperature

        while True:
            api_key = self.api_key_manager.get_key()
            if api_key is None:
                raise APIError("All API keys failed or max retries reached.")
            
            self._update_auth_header(api_key)
            self.api_key_manager.record_attempt()

            try:
                response = self.session.post(
                    self.model.api_base_url,
                    json=body,
                    stream=use_sse
                )
                response.raise_for_status()

                # If successful, we return the generator
                if use_sse:
                    return self._process_sse_stream(response)
                else:
                    return self._process_json_response(response)

            except requests.RequestException as e:
                # Log the error and try the next key
                error_message = str(e)
                print(f"API request failed with key ending in '...{api_key[-4:]}': {error_message}", file=sys.stderr)
                continue # Loop to the next key

    def _process_sse_stream(self, response: requests.Response) -> Iterator[str]:
        """Processes a Server-Sent Events (SSE) stream."""
        client = sseclient.SSEClient(_byte_iterator_to_generator(response.iter_content()))
        is_sse_done = False
        for event in client.events():
            if event.data == "[DONE]":
                is_sse_done = True
                break
            try:
                chunk = json.loads(event.data)
                delta = chunk['choices'][0]['delta']
                content = delta.get('content')
                if content:
                    yield content
            except (json.JSONDecodeError, KeyError, IndexError):
                continue
        if not is_sse_done:
            raise APIError("SSE stream ended unexpectedly. Check API key or base URL.")

    def _process_json_response(self, response: requests.Response) -> Iterator[str]:
        """Processes a standard JSON response."""
        try:
            data = response.json()
            content = data['choices'][0]['message']['content']
            yield content
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            raise APIError(f"Failed to parse API response: {e}") from e
