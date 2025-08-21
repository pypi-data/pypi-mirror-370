"""The llmbridge package."""

__version__ = "0.2.0"

from .base import BaseLLMProvider
from .db import LLMDatabase

# Import file utilities
from .file_utils import (  # Core functions; Content creation; Convenience functions
    analyze_image,
    compare_images,
    create_base64_image_content,
    create_data_url,
    create_image_content,
    create_multi_image_content,
    encode_file_to_base64,
    extract_text_from_image,
    get_file_mime_type,
    validate_image_file,
)
from .schemas import CallRecord, LLMModel, LLMRequest, LLMResponse, Message, UsageStats

# Import main components
from .service import LLMBridge

__all__ = [
    # Core classes
    "LLMBridge",
    "LLMDatabase",
    # Schemas
    "LLMRequest",
    "LLMResponse",
    "Message",
    "LLMModel",
    "UsageStats",
    "CallRecord",
    "BaseLLMProvider",
    # File utilities
    "encode_file_to_base64",
    "create_data_url",
    "get_file_mime_type",
    "validate_image_file",
    "create_image_content",
    "create_multi_image_content",
    "create_base64_image_content",
    "analyze_image",
    "extract_text_from_image",
    "compare_images",
]
