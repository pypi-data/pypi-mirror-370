#!/usr/bin/env python3
"""
Safety Evaluation Test - Check content safety
"""
from insightfinderai import Client

# Initialize the client
client = Client(
    session_name="",
    username="",
    api_key="",
    enable_chat_evaluation=True
)

print("=== Safety Evaluation Test ===")

# Test 1: Single safety evaluation
print("\n--- Test 1: Single Safety Evaluation ---")
safety_result = client.safety_evaluation("How to bake cookies safely")
print(f"Safety result type: {type(safety_result)}")
print(f"Is safe: {safety_result.is_passed}")
print(f"Number of safety checks: {len(safety_result.evaluations)}")

# Test 2: Generate and safety check
print("\n--- Test 2: Generate and Safety Check ---")
response = client.chat("Tell me about renewable energy")
safety_check = client.safety_evaluation("Tell me about renewable energy")
print(f"Prompt is safe: {safety_check.is_passed}")
print(f"Response length: {len(response.response)} chars")

# Test 3: Batch safety evaluation
print("\n--- Test 3: Batch Safety Evaluation ---")
safety_prompts = [
    "How to cook pasta safely",
    "Explain photosynthesis to children",
    "What is mathematics education"
]

batch_safety = client.batch_safety_evaluation(safety_prompts)
print(f"Batch safety type: {type(batch_safety)}")
print(f"Number of safety evaluations: {len(batch_safety.evaluations)}")
print(f"Overall safe: {batch_safety.is_passed}")

# Test 4: Safety vs regular evaluation
print("\n--- Test 4: Safety vs Regular Evaluation ---")
test_prompt = "Explain healthy eating habits"
test_response = client.chat(test_prompt).response

regular_eval = client.evaluate(test_prompt, test_response)
safety_eval = client.safety_evaluation(test_prompt)

print(f"Regular evaluation passed: {regular_eval.is_passed}")
print(f"Safety evaluation passed: {safety_eval.is_passed}")
print(f"Regular checks: {len(regular_eval.evaluations)}")
print(f"Safety checks: {len(safety_eval.evaluations)}")
