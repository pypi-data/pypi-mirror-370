#!/usr/bin/env python3
"""
Evaluation Test - Response evaluation functionality
"""
from insightfinderai import Client

# Initialize the client
client = Client(
    session_name="",
    username="",
    api_key="",
    enable_chat_evaluation=True
)

print("=== Evaluation Test ===")

# Test 1: Single evaluation
print("\n--- Test 1: Single Evaluation ---")
eval_result = client.evaluate(
    prompt="What is the capital of France?",
    response="The capital of France is Paris"
)
print(eval_result)

# Test 2: Check evaluation properties
print("\n--- Test 2: Evaluation Properties ---")
print(f"Evaluation type: {type(eval_result)}")
print(f"Is passed: {eval_result.is_passed}")
print(f"Number of evaluations: {len(eval_result.evaluations)}")
print(f"Summary: {eval_result.summary}")

# Test 3: Generate and evaluate
print("\n--- Test 3: Generate and Evaluate ---")
chat_response = client.chat("Explain quantum computing")
eval_result = client.evaluate("Explain quantum computing", chat_response.response)
print(f"Generated response evaluated: {eval_result.is_passed}")
print(f"Response length: {len(chat_response.response)} chars")
print(f"Evaluation details: {len(eval_result.evaluations)} checks")
