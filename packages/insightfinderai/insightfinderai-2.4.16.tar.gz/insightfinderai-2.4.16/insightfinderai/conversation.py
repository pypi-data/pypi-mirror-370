"""
Conversation history management for the InsightFinder AI SDK.
"""
import json
from typing import List, Dict

class ConversationHistory:
    """Manages conversation history for chat sessions."""
    
    def __init__(self):
        self.messages: List[Dict[str, str]] = []
    
    def add_message(self, role: str, content: str):
        """Add a message to the conversation history."""
        self.messages.append({"role": role, "content": content})
    
    def add_user_message(self, content: str):
        """Add a user message to the conversation."""
        self.add_message("user", content)
    
    def add_assistant_message(self, content: str):
        """Add an assistant message to the conversation."""
        self.add_message("assistant", content)
    
    def get_messages(self) -> List[Dict[str, str]]:
        """Get all messages in the conversation."""
        return self.messages.copy()
    
    def clear(self):
        """Clear the conversation history."""
        self.messages.clear()
    
    def to_string(self) -> str:
        """Convert conversation history to the string format expected by the API."""
        if not self.messages:
            return ""
        
        # Convert to JSON string format
        return ', '.join([json.dumps(msg, separators=(',', ':')) for msg in self.messages])
