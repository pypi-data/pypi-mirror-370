"""
InsightFinder AI SDK

A user-friendly Python SDK for the InsightFinder AI platform.
Designed for easy use with beautiful, formatted outputs.
"""

from .client import Client
from .model import ChatResponse, EvaluationResult, BatchEvaluationResult, BatchChatResult

__version__ = "2.4.16"
__all__ = ["Client", "ChatResponse", "EvaluationResult", "BatchEvaluationResult", "BatchChatResult"]