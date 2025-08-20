#!/usr/bin/env python3
"""
Save and Load Test - Conversation persistence
"""
from insightfinderai import Client
import os

# Initialize the client
client = Client(
    session_name="",
    username="",
    api_key="",
    enable_chat_evaluation=True
)

print("=== Save and Load Test ===")

# Test 1: Create conversation
print("\n--- Test 1: Create Conversation ---")
client.clear_chat_history()
client.chat("Hi, I'm learning about space", chat_history=True)
client.chat("Tell me about Mars", chat_history=True)
client.chat("What about Jupiter?", chat_history=True)

original_history = client.retrieve_chat_history()
print(f"Created conversation with {len(original_history)} messages")

# Test 2: Save with auto filename
print("\n--- Test 2: Save with Auto Filename ---")
auto_filename = client.save_chat_history()
print(f"Saved to: {auto_filename}")
print(f"File exists: {os.path.exists(auto_filename)}")

# Test 3: Save with custom filename
print("\n--- Test 3: Save with Custom Filename ---")
custom_filename = "my_space_conversation.json"
saved_filename = client.save_chat_history(custom_filename)
print(f"Saved to: {saved_filename}")
print(f"Custom file exists: {os.path.exists(custom_filename)}")

# Test 4: Clear and load
print("\n--- Test 4: Clear and Load ---")
client.clear_chat_history()
cleared_history = client.retrieve_chat_history()
print(f"After clear: {len(cleared_history)} messages")

loaded_data = client.load_chat_history(custom_filename)
print(f"Loaded data has {loaded_data['message_count']} messages")

client.set_chat_history(loaded_data)
restored_history = client.retrieve_chat_history()
print(f"After restore: {len(restored_history)} messages")

# Test 5: Test context preservation
print("\n--- Test 5: Context Preservation ---")
context_test = client.chat("What planet did we discuss first?", chat_history=True)
print(f"Context test: {context_test.response[:60]}...")

# Test 6: Cleanup
print("\n--- Test 6: Cleanup ---")
for filename in [auto_filename, custom_filename]:
    if os.path.exists(filename):
        os.remove(filename)
        print(f"Cleaned up: {filename}")

print("Save and load test completed successfully!")
