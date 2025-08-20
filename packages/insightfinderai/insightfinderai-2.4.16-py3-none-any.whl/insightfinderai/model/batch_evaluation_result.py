"""
BatchEvaluationResult model for the InsightFinder AI SDK.
"""
import json
import os
from datetime import datetime
from typing import List, Optional, Union, Dict, Any
from .evaluation_result import EvaluationResult

class BatchEvaluationResult:
    """Represents batch evaluation results with summary statistics and object access."""
    
    def __init__(self, evaluation_results: List[EvaluationResult]):
        self.evaluations = evaluation_results
        self.response = evaluation_results  # Alias for consistency
        self.summary = self._generate_summary()
        self.is_passed = all(eval_result.is_passed for eval_result in self.evaluations)
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate summary statistics for batch evaluations."""
        if not self.evaluations:
            return {
                'total_prompts': 0,
                'passed_evaluations': 0,
                'failed_evaluations': 0,
                'top_failed_evaluation': None
            }
        
        total_prompts = len(self.evaluations)
        passed_evaluations = 0
        failed_evaluations = 0
        
        # Count evaluation types across all failed prompts
        eval_type_counts = {}
        
        for eval_result in self.evaluations:
            if not eval_result.evaluations:
                # Empty evaluations = PASS
                passed_evaluations += 1
            else:
                # Has evaluations = FAIL (regardless of scores)
                failed_evaluations += 1
                
                # Count evaluation types for this failed prompt
                for eval_item in eval_result.evaluations:
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
        """Save the batch evaluation result to a JSON file.
        
        Args:
            filename: Optional filename. If not provided, auto-generates one.
                     Can be just a name like "evaluations" or include .json extension.
        
        Returns:
            The full path of the saved file.
        """
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"batch_evaluation_result_{timestamp}.json"
        elif not filename.endswith('.json'):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{filename}_{timestamp}.json"
        
        # Prepare the data to save - convert EvaluationResult objects to dictionaries
        evaluations_data = []
        
        # Get common model info from first evaluation (assuming all use same model)
        first_eval = self.evaluations[0] if self.evaluations else None
        
        for eval_result in self.evaluations:
            evaluation_data = {
                "prompt": eval_result.prompt,
                "response": eval_result.response,
                "evaluations": eval_result.evaluations,
                "summary": eval_result.summary,
                "metadata": {
                    "trace_id": eval_result.trace_id,
                    "is_passed": eval_result.is_passed
                }
            }
            evaluations_data.append(evaluation_data)
        
        data = {
            "type": "batch_evaluation_result",
            "timestamp": datetime.now().isoformat(),
            "model": first_eval.model if first_eval else None,
            "model_version": first_eval.model_version if first_eval else None,
            "summary": self.summary,
            "is_passed": self.is_passed,
            "evaluations": evaluations_data
        }
        
        # Save to file
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return os.path.abspath(filename)

    @property
    def prompt(self) -> List[str]:
        """Get all prompts from the batch evaluations."""
        return [eval_result.prompt for eval_result in self.evaluations if eval_result.prompt]
    
    def print(self) -> str:
        """Print and return batch evaluation results."""
        result = self.__str__()
        print(result)
        return result
    
    def __str__(self):
        """Format batch evaluation results for display."""
        if not self.evaluations:
            return "[Batch Evaluation Results]\nNo evaluations available."
        
        result = ""
        
        # Display each evaluation
        for i, eval_result in enumerate(self.evaluations, 1):
            result += f"--- Evaluation {i} ---\n"
            
            # Display prompt
            if eval_result.prompt:
                result += "Prompt:\n"
                result += f">> {eval_result.prompt}\n\n"
            
            # Display response if available
            if eval_result.response:
                result += "Response:\n"
                result += f">> {eval_result.response}\n\n"
            
            # Display evaluations
            if eval_result.evaluations:
                result += "Evaluations:\n"
                result += "-" * 40 + "\n"
                
                for j, eval_item in enumerate(eval_result.evaluations, 1):
                    eval_type = eval_item.get('evaluationType', 'Unknown')
                    score = eval_item.get('score', 0)
                    explanation = eval_item.get('explanation', 'No explanation provided')
                    
                    result += f"{j}. Type        : {eval_type}\n"
                    result += f"   Score       : {score}\n"
                    result += f"   Explanation : {explanation}\n"
                    if j < len(eval_result.evaluations):
                        result += "\n"
            else:
                result += "Evaluations:\n"
                result += "-" * 40 + "\n"
                result += "PASSED"
            
            result += "\n\n"
        
        # Add evaluation summary
        result += "Evaluation Summary\n"
        result += "-" * 66 + "\n"
        result += f"Total prompts: {self.summary['total_prompts']}\n"
        result += f"Passed evaluations: {self.summary['passed_evaluations']}\n"
        result += f"Failed evaluations: {self.summary['failed_evaluations']}\n"
        
        # Always show Top Failed Evaluation line
        if self.summary['top_failed_evaluation']:
            if isinstance(self.summary['top_failed_evaluation'], list):
                top_failed = ', '.join(self.summary['top_failed_evaluation'])
            else:
                top_failed = self.summary['top_failed_evaluation']
            result += f"Top Failed Evaluation: {top_failed}\n"
        else:
            result += f"Top Failed Evaluation: -\n"
        
        return result