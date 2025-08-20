"""
ChatResponse model for the InsightFinder AI SDK.
"""
from typing import List, Optional, Union, Dict, Any
from .evaluation_result import EvaluationResult


class ChatResponse:
    """Represents a chat response with formatted display and object access."""
    
    def __init__(self, response: str, prompt: Optional[Union[str, List[Dict[str, str]]]] = None, evaluations: Optional[List[dict]] = None, trace_id: Optional[str] = None, model: Optional[str] = None, model_version: Optional[str] = None, raw_chunks: Optional[List] = None, enable_evaluations: bool = False, project_name: Optional[str] = None, session_name: Optional[str] = None, prompt_token: Optional[int] = None, response_token: Optional[int] = None):
        self.response = response
        self.prompt = prompt
        # Convert prompt to string for evaluation result if it's a list
        prompt_str = self._format_prompt_for_display() if isinstance(prompt, list) else prompt
        
        # Store evaluations both as EvaluationResult object and as direct list
        self._evaluation_result = EvaluationResult({'evaluations': evaluations or []}, trace_id, prompt_str, response, model, model_version) if evaluations else None
        self.evaluations = evaluations or []  # Direct access to evaluations list
        
        self.enable_evaluations = enable_evaluations
        self.trace_id = trace_id
        self.model = model
        self.model_version = model_version
        self.project_name = project_name
        self.session_name = session_name
        self.raw_chunks = raw_chunks or []
        self.is_passed = self._evaluation_result is None or self._evaluation_result.is_passed
        self.prompt_token = prompt_token or 0
        self.response_token = response_token or 0
        # system_prompt_applied will be set dynamically only for set_system_prompt responses

    def _format_prompt_for_display(self) -> str:
        """Format conversation history for display."""
        if not isinstance(self.prompt, list):
            return str(self.prompt) if self.prompt else ""
        
        formatted = []
        for msg in self.prompt:
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            formatted.append(f"[{role.upper()}] {content}")
        return "\n".join(formatted)
    
    def print(self) -> str:
        """Print and return chat response for clean, user-friendly display."""
        result = self.__str__()
        print(result)
        return result
    
    def __str__(self):
        """Format chat response for clean, user-friendly display."""
        result = "[Chat Response]\n"
        if self.model is not None and self.model_version is not None:
            result += f"Model         : {self.model or 'Unknown'}\n"
            result += f"Model Version : {self.model_version or 'Unknown'}\n"
        
        # Show system prompt applied status if this is a system prompt response
        system_prompt_applied = getattr(self, 'system_prompt_applied', None)
        if system_prompt_applied is not None:
            result += f"System Prompt Applied: {'Yes' if system_prompt_applied else 'No'}\n"
        
        result += "\n"
        
        if self.prompt:
            result += "Prompt:\n"
            if isinstance(self.prompt, list):
                # Format conversation history nicely
                for i, msg in enumerate(self.prompt):
                    role = msg.get('role', 'unknown').upper()
                    content = msg.get('content', '')
                    result += f">> [{role}] {content}\n"
            else:
                result += f">> {self.prompt}\n"
            result += "\n"
        
        result += "Response:\n"
        result += f">> {self._clean_response_content(self.response)}\n"
        
        # Show evaluations if they exist and enable_evaluations was enabled
        if self.evaluations and self._evaluation_result:
            result += "\n" + self._evaluation_result.format_for_chat()
        elif self.enable_evaluations:
            # Show PASSED when evaluations are enabled but no evaluations were returned
            result += "\n\nEvaluations:\n"
            result += "-" * 40 + "\n"
            result += "PASSED"
        
        return result
    
    def _clean_response_content(self, content: str) -> str:
        """
        Clean response content to handle encoding issues and malformed characters.
        This is only used for display purposes in __str__ method.
        
        Args:
            content (str): Raw content from the API response
            
        Returns:
            str: Cleaned content safe for terminal display
        """
        if not content:
            return content
        
        try:
            # Fix common encoding issues
            cleaned = content
            
            # Replace common malformed characters caused by encoding issues
            replacements = {
                'â': '"',  # Fix malformed quotes
                'â': '"',  # Fix malformed quotes  
                'â': "'",  # Fix malformed apostrophes
                'â': '-',  # Fix malformed dashes
                'â': '-',  # Fix malformed dashes
                'â¦': '...',  # Fix malformed ellipsis
                'â¢': '•',  # Fix malformed bullets
                'âº': '→',  # Fix malformed arrows
                'â¹': '←',  # Fix malformed arrows
                'Â': '',   # Remove unnecessary characters
                'Ã': '',   # Remove unnecessary characters
            }
            
            for bad_char, good_char in replacements.items():
                cleaned = cleaned.replace(bad_char, good_char)
            
            # Remove control characters that might cause terminal issues
            import string
            printable_chars = set(string.printable)
            # Allow common unicode characters but filter out control chars
            cleaned = ''.join(
                char for char in cleaned 
                if char in printable_chars or (ord(char) > 127 and char.isprintable())
            )
            
            # Ensure proper encoding - handle any remaining encoding issues
            cleaned = cleaned.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')
            
            return cleaned
            
        except Exception as e:
            # If cleaning fails, return a safe fallback
            try:
                # Fallback: just ensure it's safe ASCII and remove problematic chars
                safe_content = ''.join(char for char in content if ord(char) < 128 and char.isprintable())
                return safe_content if safe_content else "[Content encoding error]"
            except:
                return "[Content encoding error]"
