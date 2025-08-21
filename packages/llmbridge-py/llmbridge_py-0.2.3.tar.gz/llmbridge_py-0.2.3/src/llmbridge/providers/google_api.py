"""
Google Gemini API provider implementation using the official SDK.
"""

import asyncio
import base64
import json
import os
from typing import Any, Dict, List, Optional, Union

from dotenv import load_dotenv
from google import genai
from google.genai import types
from llmbridge.base import BaseLLMProvider
from llmbridge.model_refresh.models import ModelInfo
from llmbridge.schemas import LLMResponse, Message

# Load environment variables from .env file
load_dotenv()


class GoogleProvider(BaseLLMProvider):
    """Implementation of Google Gemini API provider using the official google-genai library."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        project_id: Optional[str] = None,
        model: str = "gemini-1.5-pro",
    ):
        """
        Initialize the Google Gemini provider.

        Args:
            api_key: Google API key
            base_url: Optional base URL for the API (not used for Google)
            project_id: Google Cloud project ID (optional, for some use cases)
            model: Default model to use
        """
        super().__init__(api_key=api_key, base_url=base_url)
        self.api_key = (
            api_key
            or os.environ.get("GEMINI_API_KEY", "")
            or os.environ.get("GOOGLE_API_KEY", "")
        )
        self.project_id = project_id or os.environ.get("GOOGLE_PROJECT_ID", "")
        self.default_model = model

        if not self.api_key:
            raise ValueError(
                "Google API key must be provided (GEMINI_API_KEY or GOOGLE_API_KEY)"
            )

        # Initialize the client
        self.client = genai.Client(api_key=self.api_key)

        # List of officially supported models
        self.supported_models = [
            # Latest models
            "gemini-2.5-pro",
            "gemini-2.0-flash",
            "gemini-2.0-flash-lite",
            "gemini-2.0-pro",
            # Legacy models for compatibility
            "gemini-1.5-pro",
            "gemini-1.5-flash",
            "gemini-pro",
            "gemini-pro-vision",
        ]

        # Map database model names to actual API model names
        # Using stable models instead of experimental ones for reliability
        self.model_mapping = {
            "gemini-2.5-pro": "gemini-1.5-pro",  # Use stable model
            "gemini-2.0-flash": "gemini-1.5-flash",
            "gemini-2.0-flash-lite": "gemini-1.5-flash",
            "gemini-2.0-pro": "gemini-1.5-pro",
            # Legacy model mappings - keep for compatibility
            "gemini-1.5-pro": "gemini-1.5-pro",
            "gemini-1.5-flash": "gemini-1.5-flash",
            "gemini-pro": "gemini-1.5-pro",
            "gemini-pro-vision": "gemini-1.5-pro",
        }

    def _convert_content_to_google_format(
        self, content: Union[str, List[Dict[str, Any]]]
    ) -> Union[str, List[types.Part]]:
        """
        Convert OpenAI-style content format to Google genai format.

        Args:
            content: Either a string or list of content objects (OpenAI format)

        Returns:
            String for text-only, or list of types.Part for mixed content
        """
        if isinstance(content, str):
            return content

        if not isinstance(content, list):
            return str(content)

        parts = []
        for item in content:
            if not isinstance(item, dict):
                continue

            content_type = item.get("type", "")

            if content_type == "text":
                text_content = item.get("text", "")
                if text_content:
                    parts.append(types.Part(text=text_content))

            elif content_type == "image_url":
                image_url_data = item.get("image_url", {})
                url = image_url_data.get("url", "")

                # Handle data URL format: data:image/png;base64,<data>
                if url.startswith("data:"):
                    try:
                        # Extract mime type and base64 data
                        header, data = url.split(",", 1)
                        mime_type = header.split(":")[1].split(";")[0]

                        # Decode base64 data
                        image_data = base64.b64decode(data)

                        # Create Google-style image part
                        parts.append(
                            types.Part(
                                inline_data=types.Blob(
                                    mime_type=mime_type, data=image_data
                                )
                            )
                        )
                    except (ValueError, IndexError):
                        # Skip invalid image data
                        continue

            elif content_type == "document":
                # Handle universal document format
                source = item.get("source", {})
                if source.get("type") == "base64":
                    try:
                        mime_type = source.get("media_type", "application/pdf")
                        base64_data = source.get("data", "")

                        # Decode base64 data
                        document_data = base64.b64decode(base64_data)

                        # Create Google-style document part using inlineData
                        parts.append(
                            types.Part(
                                inline_data=types.Blob(
                                    mime_type=mime_type, data=document_data
                                )
                            )
                        )
                    except (ValueError, base64.binascii.Error):
                        # Skip invalid document data
                        continue

        return parts if parts else str(content)

    def validate_model(self, model: str) -> bool:
        """
        Check if the model is supported by Google.

        Args:
            model: Model name to check

        Returns:
            True if supported, False otherwise
        """
        # Strip provider prefix if present
        if model.lower().startswith("google:"):
            model = model.split(":", 1)[1]

        return model in self.supported_models

    def get_supported_models(self) -> List[str]:
        """
        Get list of supported Google model names.

        Returns:
            List of supported model names
        """
        return self.supported_models.copy()

    def get_default_model(self) -> str:
        """
        Get the default model to use.

        Returns:
            Default model name
        """
        return self.default_model

    def get_token_count(self, text: str) -> int:
        """
        Get the token count for a text string.

        Args:
            text: The text to count tokens for

        Returns:
            Number of tokens (estimated)
        """
        # Rough estimate: ~4 characters per token for English text
        return len(text) // 4

    def _convert_type_to_gemini(self, json_type: str) -> types.Type:
        """
        Convert JSON schema type to Gemini Type enum.

        Args:
            json_type: JSON schema type string

        Returns:
            Gemini Type enum value
        """
        type_mapping = {
            "string": types.Type.STRING,
            "integer": types.Type.INTEGER,
            "number": types.Type.NUMBER,
            "boolean": types.Type.BOOLEAN,
            "array": types.Type.ARRAY,
            "object": types.Type.OBJECT,
        }
        return type_mapping.get(json_type.lower(), types.Type.STRING)

    async def chat(
        self,
        messages: List[Message],
        model: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, Any]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        json_response: Optional[bool] = None,
        cache: Optional[Dict[str, Any]] = None,
    ) -> LLMResponse:
        """
        Send a chat request to the Google Gemini API using the official SDK.

        Args:
            messages: List of messages
            model: Model to use (e.g., "gemini-2.5-pro")
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            response_format: Optional response format
            tools: Optional list of tools (not fully supported by Gemini yet)
            tool_choice: Optional tool choice parameter (not fully supported by Gemini yet)

        Returns:
            LLM response
        """
        # Strip provider prefix if present
        if model.lower().startswith("google:"):
            model = model.split(":", 1)[1]

        # Verify model is supported
        if not self.validate_model(model):
            raise ValueError(f"Unsupported model: {model}")

        # Get the actual API model name
        api_model = self.model_mapping.get(model, model)

        # Extract system message and build conversation history
        system_message = None
        conversation_messages = []
        history = []

        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                conversation_messages.append(msg)

        # Prepare config
        config_params = {}

        if system_message:
            config_params["system_instruction"] = system_message

        if temperature is not None:
            config_params["temperature"] = temperature

        if max_tokens is not None:
            config_params["max_output_tokens"] = max_tokens

        # Handle tools if provided (limited support in Gemini)
        if tools:
            # For now, we'll add tools to the system instruction since Gemini's
            # function calling APIs are still evolving
            tools_str = json.dumps(
                [
                    {
                        "name": tool["name"],
                        "description": tool.get("description", ""),
                        "parameters": tool.get("parameters", {}),
                    }
                    for tool in tools
                ],
                indent=2,
            )

            tools_instruction = f"\nAvailable tools:\n{tools_str}\n"
            if "system_instruction" in config_params:
                config_params["system_instruction"] += tools_instruction
            else:
                config_params["system_instruction"] = tools_instruction

        # Handle JSON response format
        if response_format:
            if (
                response_format.get("type") == "json_object"
                or response_format.get("type") == "json"
            ):
                config_params["response_mime_type"] = "application/json"

                # If a schema is provided, we need to convert it to the format expected by google-genai
                if response_format.get("schema"):
                    schema_str = json.dumps(response_format["schema"], indent=2)
                    existing_instruction = config_params.get("system_instruction", "")
                    config_params["system_instruction"] = (
                        f"{existing_instruction}\n\nResponse must follow this JSON schema:\n{schema_str}".strip()
                    )

        config = types.GenerateContentConfig(**config_params) if config_params else None

        # Execute in thread pool since google-genai is synchronous
        loop = asyncio.get_event_loop()

        try:
            # For single user message, we can use generate_content directly
            if (
                len(conversation_messages) == 1
                and conversation_messages[0].role == "user"
            ):
                msg = conversation_messages[0]

                # Convert content to Google format
                converted_content = self._convert_content_to_google_format(msg.content)

                # Run synchronous operation in thread pool
                response = await loop.run_in_executor(
                    None,
                    lambda: self.client.models.generate_content(
                        model=api_model, contents=converted_content, config=config
                    ),
                )

                response_text = response.text

            else:
                # For multi-turn conversations, construct proper history
                # Split conversation into history and current message
                if conversation_messages:
                    # Build history from all messages except the last user message
                    current_message = None
                    history_messages = []

                    # Find the last user message
                    for i in reversed(range(len(conversation_messages))):
                        if conversation_messages[i].role == "user":
                            current_message = conversation_messages[i]
                            history_messages = conversation_messages[:i]
                            break

                    if not current_message:
                        # No user message found, treat the last message as the query
                        current_message = conversation_messages[-1]
                        history_messages = conversation_messages[:-1]

                    # Convert history to google-genai format
                    for msg in history_messages:
                        if msg.role == "user":
                            converted_content = self._convert_content_to_google_format(
                                msg.content
                            )
                            if isinstance(converted_content, str):
                                parts = [types.Part(text=converted_content)]
                            else:
                                parts = converted_content
                            history.append(types.Content(role="user", parts=parts))
                        elif msg.role == "assistant":
                            history.append(
                                types.Content(
                                    role="model", parts=[types.Part(text=msg.content)]
                                )
                            )

                    # Create chat with history and send the current message
                    def _run_chat():
                        chat = self.client.chats.create(
                            model=api_model, config=config, history=history
                        )
                        converted_content = self._convert_content_to_google_format(
                            current_message.content
                        )
                        return chat.send_message(converted_content)

                    # Run the chat in thread pool
                    response = await loop.run_in_executor(None, _run_chat)
                    response_text = response.text
                else:
                    # No messages? This shouldn't happen but handle gracefully
                    raise ValueError("No messages provided for chat")
        except Exception as e:
            error_msg = str(e)
            # Handle rate limiting with exponential backoff
            if "rate limit" in error_msg.lower() or "quota" in error_msg.lower():
                # Wait a bit before re-raising to allow for retry at higher level
                await asyncio.sleep(1)
                raise ValueError(
                    f"Google Gemini API rate limit exceeded: {error_msg}"
                ) from e
            elif "api key" in error_msg.lower():
                raise ValueError(
                    f"Google API authentication failed: {error_msg}"
                ) from e
            else:
                # Re-raise SDK exceptions with our standard format
                raise Exception(f"Google Gemini API error: {error_msg}") from e

        # Parse for function calls (basic handling since Gemini doesn't have native function calling yet)
        tool_calls = None
        if tools and response_text and "```json" in response_text:
            # Try to extract function call from JSON code blocks
            try:
                # Find JSON blocks
                start_idx = response_text.find("```json")
                if start_idx != -1:
                    json_text = response_text[start_idx + 7 :]
                    end_idx = json_text.find("```")
                    if end_idx != -1:
                        json_text = json_text[:end_idx].strip()
                        tool_data = json.loads(json_text)

                        # Basic structure expected: {"name": "...", "arguments": {...}}
                        if isinstance(tool_data, dict) and "name" in tool_data:
                            tool_calls = [
                                {
                                    "id": f"call_{hash(json_text) & 0xffffffff:x}",  # Generate a deterministic ID
                                    "type": "function",
                                    "function": {
                                        "name": tool_data["name"],
                                        "arguments": json.dumps(
                                            tool_data.get("arguments", {})
                                        ),
                                    },
                                }
                            ]
            except (json.JSONDecodeError, KeyError):
                # If extraction fails, just return the text response
                pass

        # Simple usage tracking (google-genai doesn't provide detailed token counts)
        usage = {
            "prompt_tokens": self.get_token_count(
                "\n".join([str(m.content) for m in messages])
            ),
            "completion_tokens": self.get_token_count(response_text or ""),
            "total_tokens": 0,  # Will be calculated below
        }
        usage["total_tokens"] = usage["prompt_tokens"] + usage["completion_tokens"]

        # Prepare the response
        llm_response = LLMResponse(
            content=response_text or "",
            model=model,  # Return the original model name from database
            usage=usage,
            finish_reason="stop",  # google-genai doesn't provide this
        )

        # Add tool calls if present
        if tool_calls:
            llm_response.tool_calls = tool_calls

        return llm_response

    async def discover_models(self) -> List[ModelInfo]:
        """
        Discover available models from Google Gemini API.

        Returns:
            List of discovered models with capabilities
        """
        try:
            # Use the client's list_models method
            models_response = self.client.models.list()
            discovered = []

            for model in models_response:
                # Filter for chat/generative models only
                if self._is_generative_model(model.name):
                    # Extract model name (remove 'models/' prefix if present)
                    model_name = model.name.replace("models/", "")

                    model_info = ModelInfo(
                        provider="google",
                        model_name=model_name,
                        display_name=self._get_display_name(model_name),
                        description=f"Google {model_name} model",
                        source="api",
                        raw_data={"api_response": model.__dict__},
                    )

                    # Add known capabilities for recognized models
                    capabilities = await self.get_model_capabilities(model_name)
                    if capabilities:
                        model_info.max_context = capabilities.get("max_context")
                        model_info.max_output_tokens = capabilities.get(
                            "max_output_tokens"
                        )
                        model_info.supports_vision = capabilities.get(
                            "supports_vision", False
                        )
                        model_info.supports_function_calling = capabilities.get(
                            "supports_function_calling", False
                        )
                        model_info.supports_json_mode = capabilities.get(
                            "supports_json_mode", False
                        )
                        model_info.supports_parallel_tool_calls = capabilities.get(
                            "supports_parallel_tool_calls", False
                        )
                        model_info.tool_call_format = capabilities.get(
                            "tool_call_format"
                        )

                    discovered.append(model_info)

            return discovered

        except Exception as e:
            # Fallback to static model list if API fails
            import logging

            logging.warning(
                f"Google model discovery failed: {str(e)}, falling back to static list"
            )
            return await super().discover_models()

    async def get_model_capabilities(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        Get capabilities for a specific Google model.

        Args:
            model_name: Name of the model

        Returns:
            Dictionary with model capabilities
        """
        # Known capabilities for Google models as of 2025
        capabilities_map = {
            # Gemini 2.5 models
            "gemini-2.5-pro": {
                "max_context": 2097152,  # 2M tokens
                "max_output_tokens": 8192,
                "supports_vision": True,
                "supports_function_calling": True,
                "supports_json_mode": True,
                "supports_parallel_tool_calls": False,
                "tool_call_format": "google",
            },
            # Gemini 2.0 models
            "gemini-2.0-flash": {
                "max_context": 1048576,  # 1M tokens
                "max_output_tokens": 8192,
                "supports_vision": True,
                "supports_function_calling": True,
                "supports_json_mode": True,
                "supports_parallel_tool_calls": False,
                "tool_call_format": "google",
            },
            "gemini-2.0-flash-lite": {
                "max_context": 1048576,  # 1M tokens
                "max_output_tokens": 8192,
                "supports_vision": True,
                "supports_function_calling": True,
                "supports_json_mode": True,
                "supports_parallel_tool_calls": False,
                "tool_call_format": "google",
            },
            "gemini-2.0-pro": {
                "max_context": 2097152,  # 2M tokens
                "max_output_tokens": 8192,
                "supports_vision": True,
                "supports_function_calling": True,
                "supports_json_mode": True,
                "supports_parallel_tool_calls": False,
                "tool_call_format": "google",
            },
            # Gemini 1.5 models
            "gemini-1.5-pro": {
                "max_context": 2097152,  # 2M tokens
                "max_output_tokens": 8192,
                "supports_vision": True,
                "supports_function_calling": True,
                "supports_json_mode": True,
                "supports_parallel_tool_calls": False,
                "tool_call_format": "google",
            },
            "gemini-1.5-flash": {
                "max_context": 1048576,  # 1M tokens
                "max_output_tokens": 8192,
                "supports_vision": True,
                "supports_function_calling": True,
                "supports_json_mode": True,
                "supports_parallel_tool_calls": False,
                "tool_call_format": "google",
            },
            # Legacy models
            "gemini-pro": {
                "max_context": 32768,
                "max_output_tokens": 2048,
                "supports_vision": False,
                "supports_function_calling": True,
                "supports_json_mode": True,
                "supports_parallel_tool_calls": False,
                "tool_call_format": "google",
            },
            "gemini-pro-vision": {
                "max_context": 16384,
                "max_output_tokens": 2048,
                "supports_vision": True,
                "supports_function_calling": False,
                "supports_json_mode": False,
                "supports_parallel_tool_calls": False,
                "tool_call_format": None,
            },
        }

        return capabilities_map.get(model_name)

    def _is_generative_model(self, model_name: str) -> bool:
        """Check if a model is a generative/chat model."""
        # Filter for Gemini models and exclude specialized models
        model_lower = model_name.lower()

        # Include Gemini models
        if "gemini" in model_lower:
            # Exclude embedding models or other specialized models
            exclude_patterns = ["embedding", "aqa", "text-bison"]
            for pattern in exclude_patterns:
                if pattern in model_lower:
                    return False
            return True

        return False

    def _get_display_name(self, model_id: str) -> str:
        """Get a friendly display name for a model."""
        display_names = {
            # Gemini 2.5 models
            "gemini-2.5-pro": "Gemini 2.5 Pro",
            # Gemini 2.0 models
            "gemini-2.0-flash": "Gemini 2.0 Flash",
            "gemini-2.0-flash-lite": "Gemini 2.0 Flash Lite",
            "gemini-2.0-pro": "Gemini 2.0 Pro",
            # Gemini 1.5 models
            "gemini-1.5-pro": "Gemini 1.5 Pro",
            "gemini-1.5-flash": "Gemini 1.5 Flash",
            # Legacy models
            "gemini-pro": "Gemini Pro",
            "gemini-pro-vision": "Gemini Pro Vision",
        }

        return display_names.get(model_id, model_id.replace("-", " ").title())
