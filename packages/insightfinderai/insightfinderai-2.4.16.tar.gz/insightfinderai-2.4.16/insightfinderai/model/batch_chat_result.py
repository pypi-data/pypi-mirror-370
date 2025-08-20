"""
BatchChatResult model for the InsightFinder AI SDK.
"""
import json
import os
from datetime import datetime
from typing import List, Optional, Union, Dict, Any
from .chat_response import ChatResponse


class BatchChatResult:
    """Represents batch chat results with object access."""
    
    def __init__(self, chat_responses: List[ChatResponse], enable_evaluation: bool = True):
        self.response = chat_responses
        self.evaluations = [resp.evaluations for resp in chat_responses if resp.evaluations]
        self.history = []  # Batch chat typically doesn't maintain conversation history
        # self.summary = self._generate_summary()
        self.evaluation_summary = self._generate_evaluation_summary()
        self.is_passed = all(resp.is_passed for resp in chat_responses)
        self.enable_evaluation = enable_evaluation
    
    # def _generate_summary(self) -> Dict[str, Any]:
    #     """Generate summary statistics for batch chat."""
    #     total_chats = len(self.response)
    #     successful_chats = sum(1 for resp in self.response if resp.response)
        
    #     return {
    #         'total_chats': total_chats,
    #         'successful_chats': successful_chats,
    #         'failed_chats': total_chats - successful_chats
    #     }
    
    def _generate_evaluation_summary(self) -> Dict[str, Any]:
        """Generate evaluation summary with same structure as EvaluationResult."""
        total_prompts = len(self.response)
        passed_evaluations = sum(1 for resp in self.response if resp.is_passed)
        failed_evaluations = total_prompts - passed_evaluations
        
        # Count evaluation types across all responses to find top failed evaluation
        eval_type_counts = {}
        for response in self.response:
            if response.evaluations:  # response.evaluations is now a list
                for eval_item in response.evaluations:
                    eval_type = eval_item.get('evaluationType', 'Unknown')
                    eval_type_counts[eval_type] = eval_type_counts.get(eval_type, 0) + 1
        
        # Find top failed evaluation type(s)
        top_failed_evaluation = None
        if eval_type_counts:
            max_count = max(eval_type_counts.values())
            top_failed_types = [eval_type for eval_type, count in eval_type_counts.items() if count == max_count]
            top_failed_evaluation = top_failed_types if len(top_failed_types) > 1 else top_failed_types[0]
        
        return {
            'total_prompts': total_prompts,
            'passed_evaluations': passed_evaluations,
            'failed_evaluations': failed_evaluations,
            'top_failed_evaluation': top_failed_evaluation
        }

    def save(self, filename: Optional[str] = None) -> str:
        """Save the batch chat result to a JSON file.
        
        Args:
            filename: Optional filename. If not provided, auto-generates one.
                     Can be just a name like "batch_chat" or include .json extension.
        
        Returns:
            The full path of the saved file.
        """
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"batch_chat_result_{timestamp}.json"
        elif not filename.endswith('.json'):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{filename}_{timestamp}.json"
        
        # Prepare the data to save - convert ChatResponse objects to dictionaries
        responses_data = []
        
        # Get common model info from first response (assuming all use same model)
        first_response = self.response[0] if self.response else None
        
        for resp in self.response:
            response_data = {
                "prompt": resp.prompt,
                "response": resp.response,
                "evaluations": resp.evaluations,
                "metadata": {
                    "trace_id": resp.trace_id,
                    "is_passed": resp.is_passed
                }
            }
            
            # Only include history if it's not empty
            if resp.history:
                response_data["history"] = resp.history
                
            responses_data.append(response_data)
        
        data = {
            "type": "batch_chat_result",
            "timestamp": datetime.now().isoformat(),
            "model": first_response.model if first_response else None,
            "model_version": first_response.model_version if first_response else None,
            "project_name": first_response.project_name if first_response else None,
            "session_name": first_response.session_name if first_response else None,
            # "summary": self.summary,  # Commented out - not needed
            "evaluation_summary": self.evaluation_summary,
            "is_passed": self.is_passed,
            "responses": responses_data
        }
        
        # Save to file
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return os.path.abspath(filename)

    @property
    def prompt(self) -> List[Union[str, List[Dict[str, str]]]]:
        """Get all prompts from the batch chat."""
        return [resp.prompt for resp in self.response if resp.prompt]
    
    def print(self) -> str:
        """Print and return batch chat results."""
        result = self.__str__()
        print(result)
        return result
    
    def __str__(self):
        """Format batch chat results for display."""
        if not self.response:
            return "[Batch Chat Results]\nNo responses available."
        
        # Get model info from first response (assuming all use same model)
        first_response = self.response[0]
        result = f"Model         : {first_response.model or 'Unknown'}\n"
        result += f"Model Version : {first_response.model_version or 'Unknown'}\n\n"
        
        # Display each prompt and response
        for i, chat_response in enumerate(self.response, 1):
            result += f"--- Prompt {i} ---\n"
            result += "Prompt:\n"
            
            # Handle prompt display
            if isinstance(chat_response.prompt, list):
                for msg in chat_response.prompt:
                    role = msg.get('role', 'unknown').upper()
                    content = msg.get('content', '')
                    result += f">> [{role}] {content}\n"
            else:
                result += f">> {chat_response.prompt}\n"
            
            result += "\nResponse:\n"
            result += f">> {chat_response.response}\n\n"

        if self.enable_evaluation:
            # Display evaluations section
            result += "Evaluations:\n"
            result += "-" * 56 + "\n"

            for i, chat_response in enumerate(self.response, 1):
                # Get prompt text for evaluation header
                if isinstance(chat_response.prompt, list):
                    # Extract last user message for header
                    prompt_text = "Conversation"
                    for msg in reversed(chat_response.prompt):
                        if msg.get('role') == 'user':
                            prompt_text = msg.get('content', 'Conversation')[:50]
                            if len(msg.get('content', '')) > 50:
                                prompt_text += "..."
                            break
                else:
                    prompt_text = str(chat_response.prompt)[:50]
                    if len(str(chat_response.prompt)) > 50:
                        prompt_text += "..."

                result += f"-- Evaluations for Prompt {i}: {prompt_text} --\n"

                # Display evaluations for this prompt
                if chat_response.evaluations and chat_response._evaluation_result:
                    eval_content = chat_response._evaluation_result.format_for_chat()
                    # Remove the "Evaluations:" header since we have our own
                    eval_lines = eval_content.split('\n')
                    if eval_lines[0].strip() == "Evaluations:":
                        eval_lines = eval_lines[2:]  # Skip "Evaluations:" and separator line
                    result += '\n'.join(eval_lines) + "\n\n"
                elif chat_response.enable_evaluations:
                    result += "PASSED\n\n"
                else:
                    result += "No evaluations\n\n"

            # Add evaluation summary
            eval_summary = self.evaluation_summary
            result += "Evaluation Summary\n"
            result += "-" * 66 + "\n"
            result += f"Total prompts: {eval_summary['total_prompts']}\n"
            result += f"Passed evaluations: {eval_summary['passed_evaluations']}\n"
            result += f"Failed evaluations: {eval_summary['failed_evaluations']}\n"

            # Always show Top Failed Evaluation line
            if eval_summary['top_failed_evaluation']:
                if isinstance(eval_summary['top_failed_evaluation'], list):
                    top_failed = ', '.join(eval_summary['top_failed_evaluation'])
                else:
                    top_failed = eval_summary['top_failed_evaluation']
                result += f"Top Failed Evaluation: {top_failed}\n"
            else:
                result += f"Top Failed Evaluation: -\n"
        
        return result
