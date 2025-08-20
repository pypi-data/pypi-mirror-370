#!/usr/bin/env python3
"""
Chat History Test - Conversation memory functionality
"""
from insightfinderai import Client

# Initialize the client
client = Client(
    session_name="",
    username="",
    api_key="",
    enable_chat_evaluation=True
)
print("=== Chat History Test ===")

# Test 1: Clear history and start fresh
print("\n--- Test 1: Clear History ---")
client.clear_chat_history()
history = client.retrieve_chat_history()
print(f"History after clear: {len(history)} messages")

# Test 2: Build conversation with history
print("\n--- Test 2: Build Conversation ---")
response1 = client.chat("Hi, my name is Alice and I'm a data scientist", chat_history=True)
print(f"First message: {response1.response[:80]}...")

response2 = client.chat("What's my name and profession?", chat_history=True)
print(f"Second message: {response2.response[:80]}...")

# Test 3: Check conversation history
print("\n--- Test 3: Check History ---")
history = client.retrieve_chat_history()
print(f"Total messages: {len(history)}")
for i, msg in enumerate(history):
    print(f"  {i+1}. [{msg['role'].upper()}] {msg['content'][:50]}...")

# Test 4: Manual history management
print("\n--- Test 4: Manual History ---")
client.add_to_conversation("user", "This is a manual message")
history = client.retrieve_chat_history()
print(f"After manual add: {len(history)} messages")
