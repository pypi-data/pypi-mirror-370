#!/usr/bin/env python3
"""
Context Management Test - Context window and usage
"""
from insightfinderai import Client

# Initialize the client
client = Client(
    session_name="",
    username="",
    api_key="",
    enable_chat_evaluation=True
)

print("=== Context Management Test ===")

# Test 1: Initial context info
print("\n--- Test 1: Initial Context Info ---")
client.clear_chat_history()
context_info = client.get_context_info()
print(f"Message count: {context_info['message_count']}")
print(f"Context size: {context_info['context_size_chars']} characters")
print(f"Usage percentage: {context_info['usage_percentage']}%")
print(f"Near limit: {context_info['near_limit']}")

# Test 2: Build conversation and monitor context
print("\n--- Test 2: Build Conversation ---")
for i in range(5):
    message = f"Tell me about topic {i+1} in detail"
    response = client.chat(message, chat_history=True)
    context = client.get_context_info()
    print(f"Message {i+1}: {context['context_size_chars']} chars, {context['usage_percentage']}%")

# Test 3: Check context after conversation
print("\n--- Test 3: Final Context State ---")
final_context = client.get_context_info()
print(f"Final message count: {final_context['message_count']}")
print(f"Final context size: {final_context['context_size_chars']} characters")
print(f"Final usage: {final_context['usage_percentage']}%")
print(f"Near limit: {final_context['near_limit']}")
print(f"Max context size: {final_context['max_context_size']} characters")

# Test 4: Context with longer messages
print("\n--- Test 4: Long Message Context ---")
long_message = "Explain artificial intelligence in great detail. " * 10
response = client.chat(long_message, chat_history=True)
long_context = client.get_context_info()
print(f"After long message: {long_context['context_size_chars']} chars")
print(f"Usage after long message: {long_context['usage_percentage']}%")

# Test 5: Clear and verify
print("\n--- Test 5: Clear Context ---")
client.clear_chat_history()
cleared_context = client.get_context_info()
print(f"After clear: {cleared_context['message_count']} messages")
print(f"After clear: {cleared_context['context_size_chars']} chars")
print(f"After clear: {cleared_context['usage_percentage']}%")

print("Context management test completed!")
