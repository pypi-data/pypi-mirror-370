#!/usr/bin/env python3
"""
Simple Chat Test - Basic chat functionality
"""
from insightfinderai import Client

# Initialize the client
client = Client(
    session_name="",
    username="",
    api_key="",
    enable_chat_evaluation=True
)

print("=== Simple Chat Test ===")

# Test 1: Basic chat
print("\n--- Test 1: Basic Chat ---")
response = client.chat("What is the capital of France?")
print(response)

# Test 2: Chat with streaming
print("\n--- Test 2: Chat with Streaming ---")
response = client.chat("Tell me about artificial intelligence", stream=True)
print(response)

# Test 3: Check response properties
print("\n--- Test 3: Response Properties ---")
response = client.chat("Explain machine learning briefly")
print(f"Response type: {type(response)}")
print(f"Has .response: {hasattr(response, 'response')}")
print(f"Has .is_passed: {hasattr(response, 'is_passed')}")
print(f"Is passed: {response.is_passed}")
print(f"Response length: {len(response.response)} characters")
