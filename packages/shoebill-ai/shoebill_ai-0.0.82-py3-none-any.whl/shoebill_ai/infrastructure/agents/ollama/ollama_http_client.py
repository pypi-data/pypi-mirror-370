import logging

import httpx
import ollama
from typing import Dict, Any, Optional


class OllamaHttpClient:
    """
    Base HTTP client for the Ollama API using the ollama-python library.
    Handles authentication and common request functionality.
    """

    def __init__(self, api_url: str, api_token: str = None, timeout: Optional[int] = None):
        """
        Initialize a new OllamaHttpClient.

        Args:
            api_url: The base URL of the Ollama API.
            api_token: Optional API token for authentication.
            timeout: Optional timeout in seconds for API requests.
        """
        self.api_url = api_url.rstrip('/')
        self.api_token = api_token
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)


        # Set up headers if API token is provided
        self.headers = {}
        if self.api_token:
            self.headers["Authorization"] = f"Bearer {self.api_token}"

        # Configure the ollama client with the API URL and timeout

        self.client = ollama.Client(host=self.api_url, headers=self.headers, timeout=120)

    def _get_headers(self) -> Dict[str, str]:
        """
        Get the headers for the request, including authentication if available.

        Returns:
            Dict[str, str]: The headers for the request.
        """
        return self.headers

    def post(self, endpoint: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Send a POST request to the Ollama API using the ollama-python library.

        Args:
            endpoint: The endpoint to send the request to (without the base URL).
            payload: The payload to send with the request.

        Returns:
            Optional[Dict[str, Any]]: The JSON response from the API, or None if the request failed.
        """
        self.logger.info(f"OllamaHttpClient: Sending request to {endpoint} endpoint")
        self.logger.debug(f"OllamaHttpClient: Headers: {self.headers}")
        self.logger.debug(f"OllamaHttpClient: Payload: {payload}")

        try:

            # Route to the appropriate ollama-python method based on the endpoint
            if endpoint == "chat":
                # Extract required parameters for chat
                model = payload.get("model")
                messages = payload.get("messages", [])
                options = {
                    "temperature": 0.7,
                    "top_p": 0.8,
                    "top_k": 20,
                    "min_p": 0.0,
                    "num_predict": 32768,
                    "seed": 20240628,
                    "num_ctx": 250000,
                    "stream": True
                }
                # Remove None values from options, but keep 0 values for temperature
                options = {k: v for k, v in options.items() if v is not None or (k == "temperature" and v == 0)}

                # Add images if present
                if "images" in payload:
                    options["images"] = payload.get("images", [])

                self.logger.debug(f"OllamaHttpClient: Options: {options}")
                # Initialize response_json
                response_json = {
                    "message": {
                        "role": "assistant",
                        "content": ""
                    }
                }
                # Extract stream parameter and ensure it's a boolean
                stream_value = options.pop("stream", False) if "stream" in options else False
                # Convert to boolean - handle string values like "true"/"false"
                if isinstance(stream_value, str):
                    is_stream = stream_value.lower() == "true"
                else:
                    is_stream = bool(stream_value)

                is_stream = True
                # Call the chat method with explicit Literal[True] or Literal[False]
                if is_stream:
                    try:
                        response = self.client.chat(
                            model=model,
                            messages=messages,
                            options=options,
                            stream=True
                        )
                        # Accumulate chunks
                        try:
                            for chunk in response:
                                #self.logger.debug(f"OllamaHttpClient: Chunk: {chunk}")
                                if "message" in chunk and "content" in chunk["message"]:
                                    response_json["message"]["content"] += chunk["message"]["content"]
                                if chunk.get("done", False):
                                    break
                        except Exception as e:
                            self.logger.error(f"OllamaHttpClient: Error during streaming chunk response: {e}")
                    except Exception as e:
                        self.logger.error(f"OllamaHttpClient: Error during streaming chat response: {e}")

                else:
                    response = self.client.chat(
                        model=model,
                        messages=messages,
                        options=options,
                        stream=False
                    )
                    # Format response to match the expected structure
                    response_json["message"]["content"] = response.get("message", {}).get("content", "")

            elif endpoint == "generate":
                # Extract required parameters for generate
                model = payload.get("model")
                prompt = payload.get("prompt", "")
                system = payload.get("system")
                options = {
                    "temperature": payload.get("temperature"),
                    "seed": payload.get("seed"),
                    "num_ctx": payload.get("num_ctx"),
                    "stream": payload.get("stream", False)
                }
                # Remove None values from options, but keep 0 values for temperature
                options = {k: v for k, v in options.items() if v is not None or (k == "temperature" and v == 0)}

                # Extract stream parameter and ensure it's a boolean
                stream_value = options.pop("stream", False) if "stream" in options else False
                # Convert to boolean - handle string values like "true"/"false"
                if isinstance(stream_value, str):
                    is_stream = stream_value.lower() == "true"
                else:
                    is_stream = bool(stream_value)

                # Call the generate method with explicit Literal[True] or Literal[False]
                if is_stream:
                    response = self.client.generate(
                        model=model,
                        prompt=prompt,
                        system=system,
                        options=options,
                        stream=True
                    )
                else:
                    response = self.client.generate(
                        model=model,
                        prompt=prompt,
                        system=system,
                        options=options,
                        stream=False
                    )

                # Format response to match the expected structure
                response_json = {
                    "response": response.get("response", "")
                }

            elif endpoint == "embeddings":
                # Extract required parameters for embeddings
                model = payload.get("model")
                prompt = payload.get("prompt", "")

                # Call the embeddings method
                response = self.client.embeddings(
                    model=model,
                    prompt=prompt,
                )

                # Format response to match the expected structure
                response_json = {
                    "embedding": response.get("embedding", [])
                }

            else:
                self.logger.error(f"OllamaHttpClient: Unsupported endpoint: {endpoint}")
                return None

            self.logger.info(f"OllamaHttpClient: Received successful response from {endpoint} endpoint")
            self.logger.debug(f"OllamaHttpClient: Response body: {response_json}")
            # Log a truncated version of the response to avoid excessive logging
            # if isinstance(response_json, dict):
            #     truncated_response = {k: str(v)[:100] + '...' if isinstance(v, str) and len(v) > 100 else v
            #                          for k, v in response_json.items()}
            #     self.logger.debug(f"OllamaHttpClient: Response body (truncated): {truncated_response}")

            return response_json

        except Exception as e:
            self.logger.error(f"OllamaHttpClient: Error during API call to {endpoint}: {e}")
            return None
