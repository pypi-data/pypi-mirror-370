#!/usr/bin/env python3
"""
Batch Evaluation Test - Evaluate multiple prompt-response pairs
"""
from insightfinderai import Client

# Initialize the client
client = Client(
    session_name="",
    username="",
    api_key="",
    enable_chat_evaluation=True
)

print("=== Batch Evaluation Test ===")

# Test 1: Prepare evaluation pairs
print("\n--- Test 1: Batch Evaluation ---")
pairs = [
    ("What's 2+2?", "4"),
    ("What's the capital of France?", "Paris"),
    ("What's the capital of Japan?", "Tokyo")
]

batch_eval = client.batch_evaluate(pairs)
print(f"Batch evaluation type: {type(batch_eval)}")
print(f"Number of evaluations: {len(batch_eval.evaluations)}")
print(f"Overall passed: {batch_eval.is_passed}")

# Test 2: Check individual evaluations
print("\n--- Test 2: Individual Results ---")
for i, eval_result in enumerate(batch_eval.evaluations):
    print(f"Evaluation {i+1}: {eval_result.is_passed}")
    print(f"  Prompt: {eval_result.prompt}")
    print(f"  Response: {eval_result.response}")

# Test 3: Generate responses and evaluate
print("\n--- Test 3: Generate and Batch Evaluate ---")
test_prompts = ["Explain AI", "What is Python?"]
responses = []

for prompt in test_prompts:
    response = client.chat(prompt)
    responses.append((prompt, response.response))

generated_batch_eval = client.batch_evaluate(responses)
print(f"Generated batch evaluations: {len(generated_batch_eval.evaluations)}")
print(f"Generated batch passed: {generated_batch_eval.is_passed}")

# Test 4: Summary statistics
print("\n--- Test 4: Summary ---")
summary = batch_eval.summary
print(f"Total prompts: {summary['total_prompts']}")
print(f"Passed evaluations: {summary['passed_evaluations']}")
print(f"Failed evaluations: {summary['failed_evaluations']}")
