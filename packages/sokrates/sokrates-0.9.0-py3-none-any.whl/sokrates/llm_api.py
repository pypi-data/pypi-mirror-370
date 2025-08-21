# This script defines the `LLMApi` class, which serves as an interface
# for interacting with OpenAI-compatible Large Language Model (LLM) APIs.
# It provides functionalities for listing available models, sending prompts
# for text generation, and managing chat completions, including streaming
# responses and performance metrics.

import logging
import sys
import time
from typing import List
import requests

from openai import OpenAI
from .colors import Colors
from .config import Config

class LLMApi:
    """
    Handles interactions with OpenAI-compatible LLM APIs.
    Provides methods for model listing, text generation, and chat completions.
    """
    def __init__(self, verbose: bool = False, api_endpoint: str = Config.DEFAULT_API_ENDPOINT, api_key: str = Config.DEFAULT_API_KEY):
        """
        Initializes the LLMApi client.

        Args:
            verbose (bool): If True, enables verbose output for API interactions.
            api_endpoint (str): The URL of the LLM API endpoint. Defaults to Config.DEFAULT_API_ENDPOINT.
            api_key (str): The API key for authentication. Defaults to Config.DEFAULT_API_KEY.
        """
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.verbose = verbose
        self.api_endpoint = api_endpoint
        self.api_key = api_key
        
    def get_openai_client(self) -> OpenAI:
        """
        Creates and returns an OpenAI client instance configured with the
        specified API endpoint and key.

        Returns:
            OpenAI: An initialized OpenAI client object.
        """
        if self.verbose:
            print(f"{Colors.BLUE}{Colors.BOLD}Initializing openai client for endpoint {self.api_endpoint}...{Colors.RESET}")
        
        return OpenAI(
            base_url=self.api_endpoint,
            api_key=self.api_key
        )

    def list_models(self) -> List[str]:
        """
        Lists available models from the configured OpenAI-compatible endpoint.

        Returns:
            List[str]: A sorted list of model IDs available at the endpoint.

        Raises:
            Exception: If there is an error while listing models.
        """
        try:
            client = self.get_openai_client()
            models = client.models.list()
            ret_array = []
            for model in models.data:
                ret_array.append(model.id)
            ret_array.sort()
            return ret_array
            
        except Exception as e:
            print(f"{Colors.RED}{Colors.BOLD}Error listing models: {str(e)}{Colors.RESET}")
            raise(e)

    def send(self, prompt: str, model: str = Config.DEFAULT_MODEL, context: str = None, context_array: List[str] = None, max_tokens: int = 2000, temperature: float = 0.7, system_prompt: str = None) -> str:
        """
        Sends a text prompt to the LLM server for generation and returns the response.
        Context can be provided as a single string or a list of strings, which will be
        prepended to the main prompt.

        Args:
            prompt (str): The main text prompt to send to the LLM.
            model (str): The name of the model to use for generation. Defaults to Config.DEFAULT_MODEL.
            system_prompt (str): A system prompt to use for processing the sent prompt (Default: None)
            context (str, optional): A single string of context to prepend to the prompt.
                                     Defaults to None.
            context_array (List[str], optional): A list of context text fragments to prepend.
                                                 Defaults to None.
            max_tokens (int): The maximum number of tokens to generate in the response. Defaults to 2000.
            temperature (float): Controls the randomness of the output. Higher values (e.g., 0.8)
                                 make the output more random, while lower values (e.g., 0.2)
                                 make it more focused and deterministic. Defaults to 0.7.

        Returns:
            str: The generated content from the LLM.

        Raises:
            Exception: If the API call to the LLM server fails.
        """
        print(f"{Colors.CYAN}{Colors.BOLD}Generating with model {model} ...{Colors.RESET}", file=sys.stderr)
        
        if self.verbose and system_prompt:
            print(f"{Colors.CYAN}{Colors.BOLD}Using provided system prompt:\n{system_prompt}{Colors.RESET}", file=sys.stderr)
        
        if context_array:
            print(f"{Colors.CYAN}{Colors.BOLD}Added provided context array to the prompt.{Colors.RESET}", file=sys.stderr)
            prompt = f"{self.combine_context(context_array)}\n{prompt}"
            
        if context:
            print(f"{Colors.CYAN}{Colors.BOLD}Added provided text context to the prompt.{Colors.RESET}", file=sys.stderr)
            prompt = f"{self.combine_context([context])}\n{prompt}"

        try:
            client = self.get_openai_client()
            if self.verbose:
                print(f"{Colors.BLUE}{'-'*20}{Colors.RESET}")
                print()
                print(f"{Colors.BLUE}{Colors.BOLD}Prompt:{Colors.RESET}")
                print()
                print(prompt)
                print()
                print(f"{Colors.BLUE}{'-'*20}{Colors.RESET}")
                print()
                
            messages = []
            
            if system_prompt:
                messages.append(
                    {
                        "role": "system", 
                        "content": system_prompt
                    }
                )
            
            messages.append(
                {
                    "role": "user",
                    "content": prompt
                }
            )

            stream = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True
            )

            start_time = time.time()
            first_token_time = None
            print(f"{Colors.GREEN}{'-'*30}{Colors.RESET}")
            print()
            print(f"{Colors.GREEN}{Colors.BOLD}Streaming generation ...{Colors.RESET}")
            print()
            print(f"{Colors.GREEN}{'-'*30}{Colors.RESET}")
            response_content = ""
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    if first_token_time is None:
                        first_token_time = time.time()
                    print(content, end="", flush=True)
                    response_content += content

            end_time = time.time()
            if self.verbose:
                print(f"{Colors.GREEN}{'-'*30}{Colors.RESET}")

            print()
            print(f"{Colors.CYAN}{Colors.BOLD}Done generating using model {model}{Colors.RESET}")
            if self.verbose:
                print(f"{Colors.CYAN}Received response ({len(response_content)} characters){Colors.RESET}", file=sys.stderr)
                
            if first_token_time is not None:
                duration_to_first = first_token_time - start_time
                duration_last_to_first = end_time - first_token_time
                total_duration = end_time - start_time
                print(f"{Colors.YELLOW}Time to first token: {duration_to_first:.4f}s")
                print(f"{Colors.YELLOW}Time between first and last token: {duration_last_to_first:.4f}s")
                print(f"{Colors.YELLOW}Total duration: {total_duration:.4f}s")
                
                tops = len(response_content) / duration_last_to_first
                print(f"{Colors.YELLOW}Tokens / second: {tops:.4f}")
                
            
            return response_content
        except Exception as e:
            raise Exception(f"{Colors.RED}{Colors.BOLD}Error calling LLM API at {self.api_endpoint}: {e}{Colors.RESET}")

    def chat_completion(self, messages: List[dict], model: str = Config.DEFAULT_MODEL, max_tokens: int = 2000, temperature: float = 0.7) -> str:
        """
        Sends a list of messages (conversation history) to the LLM server for chat completion.
        The response is streamed back, and performance metrics are calculated.

        Args:
            messages (List[dict]): A list of message dictionaries representing the conversation history.
                                   Each dictionary should have "role" (e.g., "user", "assistant")
                                   and "content" keys.
            model (str): The name of the model to use for chat completion. Defaults to Config.DEFAULT_MODEL.
            max_tokens (int): The maximum number of tokens to generate in the response. Defaults to 2000.
            temperature (float): Controls the randomness of the output. Defaults to 0.7.

        Returns:
            str: The generated content from the LLM for the chat completion.

        Raises:
            Exception: If the API call to the LLM server fails.
        """
        print(f"{Colors.CYAN}{Colors.BOLD}Generating chat completion with model {model} ...{Colors.RESET}", file=sys.stderr)

        try:
            client = self.get_openai_client()
            if self.verbose:
                print(f"{Colors.BLUE}{'-'*20}{Colors.RESET}")
                print()
                print(f"{Colors.BLUE}{Colors.BOLD}Messages:{Colors.RESET}")
                print()
                for message in messages:
                    print(f"  Role: {message['role']}, Content: {message['content'][:100]}...") # Print first 100 chars
                print()
                print(f"{Colors.BLUE}{'-'*20}{Colors.RESET}")
                print()

            stream = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True
            )

            start_time = time.time()
            first_token_time = None
            print(f"{Colors.GREEN}{'-'*30}{Colors.RESET}")
            print()
            print(f"{Colors.GREEN}{Colors.BOLD}Streaming generation ...{Colors.RESET}")
            print()
            print(f"{Colors.GREEN}{'-'*30}{Colors.RESET}")
            response_content = ""
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    if first_token_time is None:
                        first_token_time = time.time()
                    print(content, end="", flush=True)
                    response_content += content

            end_time = time.time()
            if self.verbose:
                print(f"{Colors.GREEN}{'-'*30}{Colors.RESET}")

            print()
            print(f"{Colors.CYAN}{Colors.BOLD}Done generating using model {model}{Colors.RESET}")
            if self.verbose:
                print(f"{Colors.CYAN}Received response ({len(response_content)} characters){Colors.RESET}", file=sys.stderr)
                
            if first_token_time is not None:
                duration_to_first = first_token_time - start_time
                duration_last_to_first = end_time - first_token_time
                total_duration = end_time - start_time
                print(f"{Colors.YELLOW}Time to first token: {duration_to_first:.4f}s")
                print(f"{Colors.YELLOW}Time between first and last token: {duration_last_to_first:.4f}s")
                print(f"{Colors.YELLOW}Total duration: {total_duration:.4f}s")
                
                tops = len(response_content) / duration_last_to_first
                print(f"{Colors.YELLOW}Tokens / second: {tops:.4f}")
                
            return response_content
        except Exception as e:
            raise Exception(f"{Colors.RED}{Colors.BOLD}Error calling LLM API at {self.api_endpoint}: {e}{Colors.RESET}")

    def combine_context(self, context: List[str]) -> str:
        """
        Combines a list of context strings into a single string,
        separated by a '---' delimiter.

        Args:
            context (List[str]): A list of context strings to combine.

        Returns:
            str: A single string containing the combined context.
        """
        return "\n---\n".join(context)