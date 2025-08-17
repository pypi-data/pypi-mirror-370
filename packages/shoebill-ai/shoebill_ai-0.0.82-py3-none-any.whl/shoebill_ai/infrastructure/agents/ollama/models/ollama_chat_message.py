from typing import Dict, Union, Any, List, Optional


class OllamaChatMessage:
    def __init__(self, role: str, content: Union[str, Dict[str, Any]], images: Optional[List[str]] = None):
        """
        Initialize a new OllamaChatMessage.

        Args:
            role: The role of the message sender (e.g., "user", "assistant", "system").
            content: The content of the message. Can be a string for text-only messages
                    or a dictionary for structured content (e.g., for vision models).
            images: Optional list of image paths or base64-encoded images.
        """
        self.role = role
        self.content = content
        self.images = images

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the message to a dictionary representation.

        Returns:
            Dict[str, Any]: A dictionary with role, content, and optional images keys.
        """
        result = {
            "role": self.role,
            "content": self.content
        }

        if self.images:
            result["images"] = self.images

        return result
