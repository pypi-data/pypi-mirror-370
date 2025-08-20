"""
BatchComparisonResult model for comparing two sessions with the same prompts.
"""
import json
import os
from datetime import datetime
from typing import List, Optional, Union, Dict, Any
from .batch_chat_result import BatchChatResult


class BatchComparisonResult:
    """Represents comparison results between two sessions with the same prompts."""
    
    def __init__(self, model1_result: BatchChatResult, model2_result: BatchChatResult, 
                 session1_name: str, session2_name: str, prompts: List[str]):
        self.session1 = model1_result
        self.session2 = model2_result
        self.session1_name = session1_name
        self.session2_name = session2_name
        self.prompts = prompts
        self.comparison_summary = self._generate_comparison_summary()
    
    def _generate_comparison_summary(self) -> Dict[str, Any]:
        """Generate comparison summary between the two models."""
        total_prompts = len(self.prompts)
        
        # Session 1 stats
        session1_passed = self.session1.evaluation_summary['passed_evaluations']
        session1_failed = self.session1.evaluation_summary['failed_evaluations']
        
        # Session 2 stats  
        session2_passed = self.session2.evaluation_summary['passed_evaluations']
        session2_failed = self.session2.evaluation_summary['failed_evaluations']
        
        # Determine better performing model
        better_model = None
        if session1_passed > session2_passed:
            better_model = self.session1_name
        elif session2_passed > session1_passed:
            better_model = self.session2_name
        elif session1_passed == session2_passed:
            better_model = "tie"
        
        return {
            'total_prompts': total_prompts,
            'model1_name': self.session1_name,
            'model1_passed': session1_passed,
            'model1_failed': session1_failed,
            'model2_name': self.session2_name,
            'model2_passed': session2_passed,
            'model2_failed': session2_failed,
            'better_performing_model': better_model,
            'performance_difference': abs(session1_passed - session2_passed)
        }

    def save(self, filename: Optional[str] = None) -> str:
        """Save the batch comparison result to a JSON file.
        
        Args:
            filename: Optional filename. If not provided, auto-generates one.
                     Can be just a name like "comparison" or include .json extension.
        
        Returns:
            The full path of the saved file.
        """
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"batch_comparison_result_{timestamp}.json"
        elif not filename.endswith('.json'):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{filename}_{timestamp}.json"
        
        # Prepare the data to save
        def serialize_batch_result(batch_result: BatchChatResult) -> Dict[str, Any]:
            """Convert BatchChatResult to dictionary."""
            responses_data = []
            
            # Get common model info from first response (assuming all use same model)
            first_response = batch_result.response[0] if batch_result.response else None
            
            for resp in batch_result.response:
                response_data = {
                    "prompt": resp.prompt,
                    "response": resp.response,
                    "evaluations": resp.evaluations,
                    "metadata": {
                        "trace_id": resp.trace_id,
                        "is_passed": resp.is_passed
                    }
                }
                    
                responses_data.append(response_data)
            
            return {
                "model": first_response.model if first_response else None,
                "model_version": first_response.model_version if first_response else None,
                "project_name": first_response.project_name if first_response else None,
                "session_name": first_response.session_name if first_response else None,
                # "summary": batch_result.summary,
                "evaluation_summary": batch_result.evaluation_summary,
                "is_passed": batch_result.is_passed,
                "responses": responses_data
            }
        
        data = {
            "type": "batch_comparison_result",
            "timestamp": datetime.now().isoformat(),
            "comparison_summary": self.comparison_summary,
            "prompts": self.prompts,
            "session1_name": self.session1_name,
            "session2_name": self.session2_name,
            "session1": serialize_batch_result(self.session1),
            "session2": serialize_batch_result(self.session2)
        }
        
        # Save to file
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return os.path.abspath(filename)
    
    def print(self) -> str:
        """Print and return comparison results."""
        result = self.__str__()
        print(result)
        return result
    
    def __str__(self):
        """Format comparison results for side-by-side display."""
        if not self.session1.response or not self.session2.response:
            return "[Batch Comparison Results]\nNo responses available for comparison."
        
        # Header with model information
        session1_info = self.session1.response[0] if self.session1.response else None
        session2_info = self.session2.response[0] if self.session2.response else None
        
        result = "=" * 120 + "\n"
        result += "BATCH COMPARISON RESULTS\n"
        result += "=" * 120 + "\n\n"
        
        # Model information side by side
        result += f"{'SESSION 1: ' + self.session1_name:<60}{'SESSION 2: ' + self.session2_name:<60}\n"
        session1_name = (session1_info.model or 'Unknown') if session1_info else 'Unknown'
        session2_name = (session2_info.model or 'Unknown') if session2_info else 'Unknown'
        session1_version = (session1_info.model_version or 'Unknown') if session1_info else 'Unknown'
        session2_version = (session2_info.model_version or 'Unknown') if session2_info else 'Unknown'
        result += f"{'Model: ' + session1_name:<60}{'Model: ' + session2_name:<60}\n"
        result += f"{'Version: ' + session1_version:<60}{'Version: ' + session2_version:<60}\n"
        result += "-" * 120 + "\n\n"
        
        # Side-by-side prompts and responses
        for i, prompt in enumerate(self.prompts):
            if i < len(self.session1.response) and i < len(self.session2.response):
                response1 = self.session1.response[i]
                response2 = self.session2.response[i]
                
                result += f"PROMPT {i+1}: {prompt}\n"
                result += "=" * 120 + "\n"
                
                # Responses side by side
                result += f"{'RESPONSE (' + session1_name + ')':<60}{'RESPONSE (' + session2_name + ')':<60}\n"
                result += "-" * 120 + "\n"
                
                # Split responses into lines for side-by-side display
                lines1 = self._wrap_text(response1.response, 58)
                lines2 = self._wrap_text(response2.response, 58)
                max_lines = max(len(lines1), len(lines2))
                
                for j in range(max_lines):
                    line1 = lines1[j] if j < len(lines1) else ""
                    line2 = lines2[j] if j < len(lines2) else ""
                    result += f"{line1:<60}{line2:<60}\n"
                
                result += "\n"
                
                # Evaluation results side by side
                result += f"{'EVALUATIONS (' + session1_name + ')':<60}{'EVALUATIONS (' + session2_name + ')':<60}\n"
                result += "-" * 120 + "\n"
                
                eval1_text = self._get_evaluation_text(response1)
                eval2_text = self._get_evaluation_text(response2)
                
                # Split evaluation text by existing line breaks first, then wrap if needed
                eval1_lines = []
                for line in eval1_text.split('\n'):
                    if len(line) <= 58:
                        eval1_lines.append(line)
                    else:
                        # Only wrap lines that are too long
                        wrapped_lines = self._wrap_text(line, 58)
                        eval1_lines.extend(wrapped_lines)
                
                eval2_lines = []
                for line in eval2_text.split('\n'):
                    if len(line) <= 58:
                        eval2_lines.append(line)
                    else:
                        # Only wrap lines that are too long
                        wrapped_lines = self._wrap_text(line, 58)
                        eval2_lines.extend(wrapped_lines)
                
                max_eval_lines = max(len(eval1_lines), len(eval2_lines))
                
                for j in range(max_eval_lines):
                    line1 = eval1_lines[j] if j < len(eval1_lines) else ""
                    line2 = eval2_lines[j] if j < len(eval2_lines) else ""
                    result += f"{line1:<60}{line2:<60}\n"
                
                result += "\n" + "=" * 120 + "\n\n"
        
        # Evaluation summary
        result += "EVALUATION SUMMARY\n"
        result += "=" * 120 + "\n"
        
        # Get evaluation summaries from both models
        session1_eval_summary = self.session1.evaluation_summary
        session2_eval_summary = self.session2.evaluation_summary
        
        # Headers side by side
        result += f"{session1_name + ':':<60}{session2_name + ':':<60}\n"
        result += f"{'-' * 60:<60}{'-' * 60:<60}\n"
        
        # Total Prompts
        result += f"{'Total Prompts: ' + str(session1_eval_summary['total_prompts']):<60}{'Total Prompts: ' + str(session2_eval_summary['total_prompts']):<60}\n"
        
        # Passed Evaluations
        result += f"{'Passed Evaluations: ' + str(session1_eval_summary['passed_evaluations']):<60}{'Passed Evaluations: ' + str(session2_eval_summary['passed_evaluations']):<60}\n"
        
        # Failed Evaluations
        result += f"{'Failed Evaluations: ' + str(session1_eval_summary['failed_evaluations']):<60}{'Failed Evaluations: ' + str(session2_eval_summary['failed_evaluations']):<60}\n"
        
        # Top Failed Evaluation
        if session1_eval_summary['top_failed_evaluation']:
            if isinstance(session1_eval_summary['top_failed_evaluation'], list):
                top_failed1 = ', '.join(session1_eval_summary['top_failed_evaluation'])
            else:
                top_failed1 = session1_eval_summary['top_failed_evaluation']
            # Wrap long evaluation names
            top_failed1_wrapped = self._wrap_text(f"Top Failed Evaluation: {top_failed1}", 58)
        else:
            top_failed1_wrapped = ["Top Failed Evaluation: -"]
        
        if session2_eval_summary['top_failed_evaluation']:
            if isinstance(session2_eval_summary['top_failed_evaluation'], list):
                top_failed2 = ', '.join(session2_eval_summary['top_failed_evaluation'])
            else:
                top_failed2 = session2_eval_summary['top_failed_evaluation']
            # Wrap long evaluation names
            top_failed2_wrapped = self._wrap_text(f"Top Failed Evaluation: {top_failed2}", 58)
        else:
            top_failed2_wrapped = ["Top Failed Evaluation: -"]
        
        # Display wrapped top failed evaluations
        max_failed_lines = max(len(top_failed1_wrapped), len(top_failed2_wrapped))
        for i in range(max_failed_lines):
            line1 = top_failed1_wrapped[i] if i < len(top_failed1_wrapped) else ""
            line2 = top_failed2_wrapped[i] if i < len(top_failed2_wrapped) else ""
            result += f"{line1:<60}{line2:<60}\n"
        result += "=" * 120 + "\n"
        
        return result
    
    def _wrap_text(self, text: str, width: int) -> List[str]:
        """Wrap text to specified width."""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line + " " + word) <= width:
                if current_line:
                    current_line += " " + word
                else:
                    current_line = word
            else:
                if current_line:
                    lines.append(current_line)
                    current_line = word
                else:
                    # Word is too long, break it
                    lines.append(word[:width])
                    current_line = word[width:]
        
        if current_line:
            lines.append(current_line)
            
        return lines
    
    def _get_evaluation_text(self, chat_response) -> str:
        """Get evaluation text for a chat response."""
        if chat_response.evaluations and chat_response._evaluation_result:
            eval_content = chat_response._evaluation_result.format_for_chat()
            # Remove the "Evaluations:" header
            eval_lines = eval_content.split('\n')
            if eval_lines[0].strip() == "Evaluations:":
                eval_lines = eval_lines[2:]  # Skip "Evaluations:" and separator line
            return '\n'.join(eval_lines)
        elif chat_response.evaluations:
            # If we have evaluations but no _evaluation_result, format them manually
            if not chat_response.evaluations:
                return "PASSED"
            
            eval_text = ""
            for i, eval_item in enumerate(chat_response.evaluations, 1):
                eval_type = eval_item.get('evaluationType', 'Unknown')
                score = eval_item.get('score', 'N/A')
                explanation = eval_item.get('explanation', 'No explanation')
                
                eval_text += f"{i}. Type        : {eval_type}\n"
                eval_text += f"   Score       : {score}\n"
                eval_text += f"   Explanation : {explanation}\n"
                if i < len(chat_response.evaluations):
                    eval_text += "\n"
            
            return eval_text
        elif chat_response.enable_evaluations:
            return "PASSED"
        else:
            return "No evaluations"
