#!/usr/bin/env python3
"""
Session Override Test - Using different sessions
"""
from insightfinderai import Client

# Initialize the client with default session
client = Client(
    session_name="",
    username="",
    api_key="",
    enable_chat_evaluation=True
)

print("=== Session Override Test ===")

# Test 1: Default session
print("\n--- Test 1: Default Session ---")
response1 = client.chat("Hello, I'm Alice")
print(f"Default session response: {response1.response[:50]}...")

# Test 2: Override session for chat
print("\n--- Test 2: Override Session ---")
response2 = client.chat("Hello, I'm Bob", session_name="custom-session")
print(f"Custom session response: {response2.response[:50]}...")

# Test 3: Override session for evaluation
print("\n--- Test 3: Session Override for Evaluation ---")
eval_result = client.evaluate(
    prompt="What is AI?",
    response="AI is artificial intelligence",
    session_name="eval-session"
)
print(f"Evaluation with session override: {eval_result.is_passed}")

# Test 4: Override session for batch operations
print("\n--- Test 4: Batch with Session Override ---")
batch_result = client.batch_chat(
    ["What is Python?", "What is Java?"],
    session_name="batch-session"
)
print(f"Batch with session override: {len(batch_result.response)} responses")

# Test 5: Safety evaluation with session override
print("\n--- Test 5: Safety with Session Override ---")
safety_result = client.safety_evaluation(
    "Tell me about cooking",
    session_name="safety-session"
)
print(f"Safety with session override: {safety_result.is_passed}")

# Test 6: Multiple sessions
print("\n--- Test 6: Multiple Sessions ---")
sessions = ["session-1", "session-2", "session-3"]

for i, session in enumerate(sessions):
    response = client.chat(f"Hello from session {i+1}", session_name=session)
    print(f"Session {session}: {response.response[:40]}...")

print(f"\nTested {len(sessions)} different sessions successfully")
