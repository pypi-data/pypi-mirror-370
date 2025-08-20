from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime
from .log_parser import add_parser_to_provider
import json
import requests
from dataclasses import asdict
import threading
import traceback


import agentops

agentops.init()


# Define a dataclass to structure the logging of LLM interactions
@dataclass
class LLMEvent:
    """
    Records a single interaction between the agent and the LLM.
    This class structures the data before being processed by the log parser.
    """
    event_type: str = "llms"
    prompt: Optional[Union[str, List]] = None
    completion: Optional[Union[str, Dict]] = None
    model: Optional[str] = None
    timestamp: str = None
    metadata: Dict = None

class OpenAIProvider:
    """
    Handles the interception and logging of OpenAI API interactions.
    Supports the new client-based OpenAI API (v1.0.0+).
    """
    def __init__(self, trace_id, client=None, api_key=None, tags=None):
        """
        Initialize the provider with tracking parameters.
        
        Args:
            trace_id (str): Unique identifier for the tracking session
            client (str, optional): Client identifier
            api_key (str, optional): API key for authentication
            tags (dict, optional): Dictionary of tags to associate with the tracking session
        """
        self.original_openai_class = None  # Original OpenAI class
        self.original_async_openai_class = None  # Original AsyncOpenAI class
        self.conversation_ring = []
        self.max_history = 100  # Store last 100 conversations in memory
        self.client = client
        self.trace_id = trace_id
        self.api_key = api_key
        self.tags = tags or []
        self._patched = False

    def override(self):
        """
        Override OpenAI's completion methods to enable logging.
        This method patches the original completion functions with our logging versions.
        Supports the new client-based OpenAI API (v1.0.0+).
        """
        if self._patched:
            print("OpenAI provider already patched. Skipping...")
            return
            
        try:
            # Try to import OpenAI module
            from openai import OpenAI, AsyncOpenAI
            
            # Store original classes
            self.original_openai_class = OpenAI
            self.original_async_openai_class = AsyncOpenAI
            
            # Create a patched OpenAI class
            class PatchedOpenAI(OpenAI):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)
                    # Patch the chat completions method
                    original_chat_create = self.chat.completions.create
                    
                    def patched_chat_create(*args, **kwargs):
                        """
                        Wrapped version of chat.completions.create that includes logging.
                        """
                        print("\n===== OpenAI Chat Input =====")
                        print("\nArgs (Positional Arguments):")
                        if args:
                            for i, arg in enumerate(args):
                                print(f"Arg {i}: {arg}")
                        else:
                            print("No positional arguments")

                        print("\nKwargs (Keyword Arguments):")
                        if kwargs:
                            for key, value in kwargs.items():
                                print(f"{key}: {value}")
                        else:
                            print("No keyword arguments")
                            
                        # Call original method to get response
                        try:
                            response = original_chat_create(*args, **kwargs)
                        except Exception as e:
                            # Get the provider instance from the global scope
                            provider = getattr(PatchedOpenAI, '_provider', None)
                            if provider:
                                provider.handle_error(e, kwargs)
                            raise e
                        
                        print("\n===== OpenAI Chat Output =====")
                        print(f"Response: {response}")
                        print("=" * 50 + "\n")
                        
                        # Log the interaction and return the response
                        provider = getattr(PatchedOpenAI, '_provider', None)
                        if provider:
                            return provider._log_interaction(kwargs, response)
                        return response
                    
                    self.chat.completions.create = patched_chat_create
                    
                    # Patch the completions method
                    original_completion_create = self.completions.create
                    
                    def patched_completion_create(*args, **kwargs):
                        """
                        Wrapped version of completions.create that includes logging.
                        """
                        print("\n===== OpenAI Completion Input =====")
                        print("\nArgs (Positional Arguments):")
                        if args:
                            for i, arg in enumerate(args):
                                print(f"Arg {i}: {arg}")
                        else:
                            print("No positional arguments")

                        print("\nKwargs (Keyword Arguments):")
                        if kwargs:
                            for key, value in kwargs.items():
                                print(f"{key}: {value}")
                        else:
                            print("No keyword arguments")
                            
                        # Call original method to get response
                        try:
                            response = original_completion_create(*args, **kwargs)
                        except Exception as e:
                            provider = getattr(PatchedOpenAI, '_provider', None)
                            if provider:
                                provider.handle_error(e, kwargs)
                            raise e
                        
                        print("\n===== OpenAI Completion Output =====")
                        print(f"Response: {response}")
                        print("=" * 50 + "\n")
                        
                        # Log the interaction and return the response
                        provider = getattr(PatchedOpenAI, '_provider', None)
                        if provider:
                            return provider._log_interaction(kwargs, response)
                        return response
                    
                    self.completions.create = patched_completion_create
            
            # Create a patched AsyncOpenAI class
            class PatchedAsyncOpenAI(AsyncOpenAI):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)
                    # Patch the async chat completions method
                    original_chat_create = self.chat.completions.create
                    
                    async def patched_chat_create(*args, **kwargs):
                        """
                        Wrapped version of async chat.completions.create that includes logging.
                        """
                        print("\n===== OpenAI Async Chat Input =====")
                        print("\nArgs (Positional Arguments):")
                        if args:
                            for i, arg in enumerate(args):
                                print(f"Arg {i}: {arg}")
                        else:
                            print("No positional arguments")

                        print("\nKwargs (Keyword Arguments):")
                        if kwargs:
                            for key, value in kwargs.items():
                                print(f"{key}: {value}")
                        else:
                            print("No keyword arguments")
                            
                        # Call original method to get response
                        try:
                            response = await original_chat_create(*args, **kwargs)
                        except Exception as e:
                            provider = getattr(PatchedAsyncOpenAI, '_provider', None)
                            if provider:
                                provider.handle_error(e, kwargs)
                            raise e
                        
                        print("\n===== OpenAI Async Chat Output =====")
                        print(f"Response: {response}")
                        print("=" * 50 + "\n")
                        
                        # Log the interaction and return the response
                        provider = getattr(PatchedAsyncOpenAI, '_provider', None)
                        if provider:
                            return provider._log_interaction(kwargs, response)
                        return response
                    
                    self.chat.completions.create = patched_chat_create
                    
                    # Patch the async completions method
                    original_completion_create = self.completions.create
                    
                    async def patched_completion_create(*args, **kwargs):
                        """
                        Wrapped version of async completions.create that includes logging.
                        """
                        print("\n===== OpenAI Async Completion Input =====")
                        print("\nArgs (Positional Arguments):")
                        if args:
                            for i, arg in enumerate(args):
                                print(f"Arg {i}: {arg}")
                        else:
                            print("No positional arguments")

                        print("\nKwargs (Keyword Arguments):")
                        if kwargs:
                            for key, value in kwargs.items():
                                print(f"{key}: {value}")
                        else:
                            print("No keyword arguments")
                            
                        # Call original method to get response
                        try:
                            response = await original_completion_create(*args, **kwargs)
                        except Exception as e:
                            provider = getattr(PatchedAsyncOpenAI, '_provider', None)
                            if provider:
                                provider.handle_error(e, kwargs)
                            raise e
                        
                        print("\n===== OpenAI Async Completion Output =====")
                        print(f"Response: {response}")
                        print("=" * 50 + "\n")
                        
                        # Log the interaction and return the response
                        provider = getattr(PatchedAsyncOpenAI, '_provider', None)
                        if provider:
                            return provider._log_interaction(kwargs, response)
                        return response
                    
                    self.completions.create = patched_completion_create
            
            # Store provider reference in the patched classes
            PatchedOpenAI._provider = self
            PatchedAsyncOpenAI._provider = self
            
            # Replace the original classes with our patched versions
            import openai
            openai.OpenAI = PatchedOpenAI
            openai.AsyncOpenAI = PatchedAsyncOpenAI
            
            self._patched = True
            print("OpenAI API successfully patched!")
                
        except ImportError:
            print("OpenAI module not found. Please install openai package.")
            return
        except Exception as e:
            print(f"Error patching OpenAI API: {e}")
            print(traceback.format_exc())
            return

    def _log_interaction(self, kwargs: dict, response: Any):
        """
        Pre-processing hook that structures data before the log parser processes it.
        """
        # Extract basic information
        save_data_in_neat_logs(kwargs, response, self.trace_id, self.api_key, tags=self.tags)
        
        # Extract prompt from messages or prompt field
        prompt = kwargs.get("messages", kwargs.get("prompt", "N/A"))
        
        # Extract model name
        model = kwargs.get("model", "unknown")
        
        # Extract completion text
        if hasattr(response, 'choices') and response.choices:
            if hasattr(response.choices[0], 'message'):
                completion = response.choices[0].message.content
            elif hasattr(response.choices[0], 'text'):
                completion = response.choices[0].text
            else:
                completion = str(response.choices[0])
        else:
            completion = str(response)

        # Create event object
        event = LLMEvent(
            prompt=prompt,
            completion=completion,
            model=model,
            timestamp=datetime.now().isoformat(),
            metadata={
                "total_tokens": response.usage.total_tokens if hasattr(response, "usage") and hasattr(response.usage, "total_tokens") else 0,
                "tags": self.tags
            }
        )
        
        # Update conversation ring buffer
        if len(self.conversation_ring) >= self.max_history:
            self.conversation_ring.pop(0)
        self.conversation_ring.append(event)
        
        return response

    def undo_override(self):
        """
        Restore the original OpenAI completion methods.
        Should be called when logging is no longer needed.
        """
        if not self._patched:
            print("OpenAI provider not patched. Nothing to restore.")
            return
            
        try:
            import openai
            
            if self.original_openai_class:
                openai.OpenAI = self.original_openai_class
                
            if self.original_async_openai_class:
                openai.AsyncOpenAI = self.original_async_openai_class
            
            self._patched = False
            print("OpenAI API patches restored successfully.")
            
        except Exception as e:
            print(f"Error restoring OpenAI API: {e}")
            print(traceback.format_exc())

    def get_conversation_history(self, limit: int = None) -> List[Dict]:
        """
        Returns recent conversation history with optional limit.
        """
        history = self.conversation_ring[-limit:] if limit else self.conversation_ring
        return [
            {
                "timestamp": event.timestamp,
                "model": event.model,
                "prompt": event.prompt,
                "completion": event.completion,
                "metadata": event.metadata
            }
            for event in history
        ]
    
    def handle_error(self, e, kwargs):
        """
        Handle errors in the original method.
        """
        print(f"Error in original OpenAI method: {e}")
        save_data_in_neat_logs(kwargs, None, self.trace_id, self.api_key, error=e, tags=self.tags)
        return None


# Apply the parser decorator to the provider class
add_parser_to_provider(OpenAIProvider)


def _save_data_in_background(kwargs: dict, response: Any, trace_id, api_key, error=None, tags=None):
    """Background thread function to send data to server."""
    url = "https://app.neatlogs.com/api/data"
    headers = {"Content-Type": "application/json"}
    try:
        print("**************************************************")
        print("kwargs: ", kwargs, response, trace_id, api_key, error, tags)
        print("**************************************************")
        if hasattr(response, "dict"):
            json_data = response.dict()  # Pydantic v1
        elif hasattr(response, "model_dump"):
            json_data = response.model_dump()  # Pydantic v2
        elif hasattr(response, "__dict__"):
            json_data = vars(response)  # Regular class
        elif isinstance(response, tuple):  # NamedTuple
            json_data = response._asdict()
        elif hasattr(response, "__dataclass_fields__"):  # Dataclass
            json_data = asdict(response)
        else:
            raise TypeError("Cannot serialize object")

        trace_data = {
            "kwargs": json.dumps(kwargs),
            "response": json.dumps(json_data)
        }

        error_info = None
        if error is not None:
            error_info = {
                "type": type(error).__name__,
                "message": str(error),
                "args": getattr(error, 'args', None)
            }

        if tags:
            trace_data["tags"] = tags

        if error_info:
            trace_data["error"] = error_info

        
        api_data = {
            "dataDump": json.dumps(trace_data),
            "projectAPIKey": api_key,
            "externalTraceId": trace_id,
            "timestamp": datetime.now().timestamp()
        }

        # requests.post(url, json=api_data, headers=headers)

        print("**************************************************")
        print("API DATA: ", api_data)
        print("**************************************************")

    except Exception as e:
        print("Error in sending logs:", e)
        # Print the full traceback
        print(traceback.format_exc())

def save_data_in_neat_logs(kwargs: dict, response: Any, trace_id, api_key, error=None, tags=None):
    """
    Non-blocking function that sends data to the server in a background thread.
    The thread will continue running even after the main program exits.
    
    Args:
        kwargs (dict): The input arguments for the LLM call
        response (Any): The response from the LLM
        trace_id (str): Unique identifier for the tracking session
        api_key (str): API key for authentication
        error (Exception, optional): Any error that occurred
        tags (dict, optional): Dictionary of tags to associate with the tracking session
    """
    thread = threading.Thread(
        target=_save_data_in_background,
        args=(kwargs, response, trace_id, api_key, error, tags),
        daemon=False  # Set to False so the thread continues after main program exits
    )
    thread.start()

# Example usage
# if __name__ == "__main__":
#     # Create a provider instance
#     provider = OpenAIProvider(trace_id="test-123", api_key="your-api-key")
#
#     # Enable logging
#     provider.override()
#
#     # At this point, any OpenAI client calls will be logged
#     # Example:
#     # from openai import OpenAI
#     # client = OpenAI()
#     # response = client.chat.completions.create(
#     #     model="gpt-3.5-turbo",
#     #     messages=[{"role": "user", "content": "Hello!"}]
#     # )
#
#     # To get conversation history:
#     # history = provider.get_conversation_history()
#
#     # To disable logging:
#     # provider.undo_override() 