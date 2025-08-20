# InsightFinder AI SDK

A powerful and user-friendly Python SDK for the InsightFinder AI platform. This SDK provides easy-to-use methods for chatting with AI models, evaluating responses, managing sessions, and more.

## 🚀 Quick Start

### Installation

```bash
pip install insightfinderai
```

### Basic Setup

**Choose Your Setup Method:**

**OPTION A: LLM Gateway (Recommended for most users)**
- Use when you need high availability and automatic failover
- Best for production applications requiring high uptime
- Ideal for getting started quickly without session management
- Perfect for prototyping and development
- Key: Do NOT provide session_name to activate gateway

**OPTION B: Specific Session**
- Use when you need direct control over a specific model
- Best for research requiring consistent model behavior
- Ideal for testing specific model capabilities
- Perfect for custom or fine-tuned models
- Key: Provide session_name to bypass gateway

```python
from insightfinderai import Client

# OPTION A: LLM Gateway (Recommended for most users)
# A1: Direct credentials
client = Client(
    username="your_username",
    api_key="your_api_key"
    # No session_name = Uses LLM Gateway
)

# A2: Environment variables (recommended for production)
# Set environment variables to avoid credentials in code:
# export INSIGHTFINDER_USERNAME="your_username"
# export INSIGHTFINDER_API_KEY="your_api_key"
client = Client()  # No session_name = Uses LLM Gateway

# OPTION B: Specific Session (Advanced users)
# B1: Direct credentials
client = Client(
    session_name="my-ai-session",
    username="your_username",
    api_key="your_api_key",
    enable_chat_evaluation=True  # Default: True
)

# B2: Environment variables (recommended for production)
# Set environment variables to avoid credentials in code:
# export INSIGHTFINDER_USERNAME="your_username"
# export INSIGHTFINDER_API_KEY="your_api_key"
client = Client(session_name="my-ai-session")
```

### 🤔 Which Method Should You Use?

| Use Case | Recommended Method | Why? |
|----------|-------------------|------|
| **Getting Started** | Option A (LLM Gateway) | Automatic failover, no setup |
| **Production Apps** | Option A (LLM Gateway) | High availability, cost optimization |
| **Prototyping** | Option A (LLM Gateway) | Quick start, reliable |
| **Model Testing** | Option B (Specific Session) | Control exact model behavior |
| **Research** | Option B (Specific Session) | Consistent model responses |
| **Custom Models** | Option B (Specific Session) | Use your fine-tuned models |

**💡 Pro Tip**: Start with Option A (LLM Gateway). Only use Option B if you need specific model control.

## 📋 Table of Contents

- [LLM Gateway Service](#-llm-gateway-service)
- [Chat Operations](#-chat-operations)
- [Evaluation Features](#-evaluation-features)
- [Session Management](#-session-management)
- [System Prompt Management](#-system-prompt-management)
- [Context Management](#-context-management)
- [Batch Operations](#-batch-operations)
- [Model Information](#-model-information)
- [Usage Statistics](#-usage-statistics)

## 🌐 LLM Gateway Service

The LLM Gateway service provides automatic failover capabilities when you **don't specify a `session_name`**. This service allows you to configure multiple models with automatic fallback behavior.

### 🔑 How to Activate LLM Gateway

**Simple rule: Don't provide `session_name` when creating your client**

```python
# ✅ Uses LLM Gateway (recommended)
client = Client(
    username="your_username",
    api_key="your_api_key"
    # No session_name parameter = Gateway mode
)

# ❌ Does NOT use LLM Gateway
client = Client(
    session_name="my-session",  # This bypasses the gateway
    username="your_username",
    api_key="your_api_key"
)
```

### How It Works

When you create a client without a `session_name`, the system uses the LLM Gateway which includes:

- **Primary LLM**: Your main model that handles all requests initially
- **First Backup LLM**: Automatically used if the primary model fails
- **Second Backup LLM**: Used as the final fallback if both primary and first backup fail

```python
# Using LLM Gateway with automatic fallback
client = Client(
    username="your_username",
    api_key="your_api_key"
)

# All chat operations will use the gateway with automatic fallback
response = client.chat("Hello world")
# If primary model fails → tries first backup
# If first backup fails → tries second backup
```

### Benefits

- **High Availability**: Automatic failover ensures your application keeps working
- **No Code Changes**: Fallback is transparent to your application
- **Centralized Configuration**: Manage model preferences in one place
- **Cost Optimization**: Use cheaper backup models when primary is unavailable
- **Zero Setup**: No need to create or manage sessions

## 💬 Chat Operations

### Basic Chat

```python
# Simple chat (uses LLM Gateway if no session_name provided during client creation)
response = client.chat("What is artificial intelligence?")
print(response)

# Chat with streaming (shows response as it's generated)
response = client.chat("Tell me a story", stream=True)

# Chat without history (independent messages)
response = client.chat("What's 2+2?", chat_history=False)
```

### Chat with Different Sessions

```python
# Use a specific session for this chat (bypasses LLM Gateway)
response = client.chat("Hello", session_name="custom-session")
```

## 🎯 Evaluation Features

### Single Evaluation

```python
# Evaluate a prompt-response pair
result = client.evaluate(
    prompt="What's 2+2?",
    response="The answer is 4"
)
print(result)
```

### Safety Evaluation

```python
# Check if a prompt is safe
result = client.safety_evaluation("What is your credit card number?")
print(result)  # Shows PII/PHI detection results
```

### Batch Evaluation

```python
# Evaluate multiple prompt-response pairs
pairs = [
    ("What's 2+2?", "4"),
    ("Capital of France?", "Paris"),
    ("Tell me a joke", "Why did the chicken cross the road?")
]
results = client.batch_evaluate(pairs)
for result in results:
    print(result)
```

### Batch Safety Evaluation

```python
# Check safety of multiple prompts
prompts = ["Hello", "What's your SSN?", "Tell me about AI"]
results = client.batch_safety_evaluation(prompts)
for result in results:
    print(result)
```

## 🎛️ Session Management

### List Sessions

```python
# Get all your sessions
sessions = client.list_sessions()
for session in sessions.sessions:
    print(f"Name: {session.name}")
    print(f"Model: {session.model_type}/{session.model_version}")
    print(f"Tokens: {session.token_usage.input_tokens}/{session.token_usage.output_tokens}")
```

### Create New Session

```python
# Create a new session with a specific model
success = client.create_session(
    model_name="my-gpt-session",
    model_type="OpenAI",
    model_version="gpt-4o",
    description="My GPT-4 session"
)
if success:
    print("Session created successfully")
```

### Delete Session

```python
# Delete a session
success = client.delete_session("my-old-session")
if success:
    print("Session deleted successfully")
```

### List Supported Models

```python
# See all available models
models = client.list_supported_models()
for model in models:
    print(model)  # Format: "ModelType/ModelVersion"
```

## 🔧 System Prompt Management

### Set System Prompt

```python
# Set a system prompt with evaluation
response = client.set_system_prompt(
    "You are a helpful assistant that always responds in JSON format"
)
print(response)

# Check if it was applied
if hasattr(response, 'system_prompt_applied') and response.system_prompt_applied:
    print("System prompt applied successfully")
```

### Apply System Prompt (Force)

```python
# Apply system prompt without evaluation
success = client.apply_system_prompt(
    "You are a helpful assistant that responds briefly"
)
if success:
    print("System prompt applied")
```

### Clear System Prompt

```python
# Remove the system prompt
success = client.clear_system_prompt()
if success:
    print("System prompt cleared")
```

## 🧹 Context Management

### Clear Context

```python
# Clear conversation history
success = client.clear_context()
if success:
    print("Context cleared - fresh start!")
```

## 📦 Batch Operations

### Batch Chat

```python
# Process multiple prompts in parallel
prompts = ["Hello!", "What's the weather?", "Tell me a joke"]
responses = client.batch_chat(prompts, max_workers=3)

# Access individual responses
for i, response in enumerate(responses.results):
    print(f"Prompt {i+1}: {response.response}")

# Get summary statistics
print(f"Success rate: {responses.success_rate}")
print(f"Average response time: {responses.average_response_time}")
```

### Model Comparison

```python
# Compare two models on the same prompts
prompts = [
    "What is artificial intelligence?",
    "Explain machine learning",
    "Tell me a joke"
]

comparison = client.compare_models(
    session1_name="gpt-4-session",
    session2_name="claude-session",
    prompts=prompts
)

# Print side-by-side comparison
comparison.print()

# Check which performed better
if comparison.comparison_summary['better_performing_model'] != 'tie':
    print(f"Better model: {comparison.comparison_summary['better_performing_model']}")
```

## 📊 Model Information

### Token Usage for Session

```python
# Get token usage for a specific session
usage = client.token_usage("my-session")
print(f"Input tokens: {usage.input_tokens}")
print(f"Output tokens: {usage.output_tokens}")
```

### Organization Usage Statistics

```python
# Get organization-wide usage stats
stats = client.usage_stats()
print(f"Total input tokens: {stats.total_input_tokens}")
print(f"Total output tokens: {stats.total_output_tokens}")
print(f"Token limit: {stats.total_token_limit}")
```

## 🔄 Cache Management

### Clear Caches

```python
# Clear project name cache
client.clear_project_name_cache()

# Clear model info cache
client.clear_model_info_cache()

# View cached data
project_names = client.get_cached_project_names()
model_info = client.get_cached_model_info()
```

## 🎨 Working with Response Objects

### ChatResponse Object

```python
response = client.chat("Hello world")

# Access properties
print(f"Response: {response.response}")
print(f"Prompt: {response.prompt}")
print(f"Model: {response.model}")
print(f"Model Version: {response.model_version}")
print(f"Trace ID: {response.trace_id}")
print(f"Session: {response.session_name}")
print(f"Tokens: {response.prompt_token}/{response.response_token}")

# Check if evaluations are available
if response.evaluations:
    print("Evaluation results available")

# Pretty print (formatted output)
response.print()
```

### EvaluationResult Object

```python
result = client.evaluate("Test prompt", "Test response")

# Access evaluation data
print(f"Trace ID: {result.trace_id}")
print(f"Prompt: {result.prompt}")
print(f"Response: {result.response}")
print(f"Model: {result.model}/{result.model_version}")

# Pretty print evaluation results
result.print()
```

## ⚙️ Advanced Configuration

### LLM Gateway vs Session-Based Usage

**The key difference is whether you provide `session_name` or not:**

```python
# 🌐 OPTION A: LLM Gateway (High Availability Mode)
# ✅ Automatic failover between Primary → Backup1 → Backup2
# ✅ 99.9% uptime
# ✅ Cost optimization
# ✅ Zero session management
client = Client(
    username="your_username",
    api_key="your_api_key"
    # KEY: No session_name = Gateway mode
)

# 🎯 OPTION B: Direct Session (Specific Model Mode)  
# ✅ Direct control over exact model
# ✅ Consistent model behavior
# ❌ No automatic failover
# ❌ Manual session management required
client = Client(
    session_name="my-gpt-session",  # KEY: session_name = Direct mode
    username="your_username", 
    api_key="your_api_key"
)
```

**Decision Guide:**
- **Need reliability?** → Use Option A (no session_name)
- **Need specific model?** → Use Option B (with session_name)
- **Just getting started?** → Use Option A (no session_name)
- **Building production app?** → Use Option A (no session_name)
- **Doing model research?** → Use Option B (with session_name)

### Custom API URL

```python
# Use a custom API endpoint
client = Client(
    session_name="my-session",
    url="https://custom-api.example.com",
    username="user",
    api_key="key"
)
```

### Disable Evaluations

```python
# Create client without evaluations
client = Client(
    session_name="my-session",
    enable_chat_evaluation=False
)

# Or disable for specific chat
response = client.chat("Hello", enable_evaluation=False)
```

### Custom Session Names in Operations

```python
# Most operations support custom session names
client.chat("Hello", session_name="session-1")
client.evaluate("Test", "Response", session_name="session-2")
client.set_system_prompt("System prompt", session_name="session-3")
client.clear_context(session_name="session-4")
```

## 🚨 Error Handling

```python
try:
    response = client.chat("Hello")
    print(response)
except ValueError as e:
    print(f"API Error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## 🔑 Environment Variables

Set these environment variables to avoid passing credentials in code:

```bash
export INSIGHTFINDER_USERNAME="your_username"
export INSIGHTFINDER_API_KEY="your_api_key"
```

## 📝 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions, please contact: support@insightfinder.com

## 🔄 Version

Current version: 2.4.9

---

**Happy AI chatting! 🤖✨**