DEFAULT_API_URL = "https://ai.insightfinder.com"

# API Endpoints
# Chatbot endpoints
CHATBOT_ENDPOINT = "api/external/v1/chatbot/stream-with-type"
SET_SYSTEM_PROMPT_ENDPOINT = "api/external/v1/chatbot/sysprompt/get-sysprompt"
APPLY_SYSTEM_PROMPT_ENDPOINT = "api/external/v1/chatbot/sysprompt/apply-sysprompt"
CLEAR_SYSTEM_PROMPT_ENDPOINT = "api/external/v1/chatbot/sysprompt/clear-sysprompt"
NEW_CHAT_SESSION_ENDPOINT = "api/external/v1/chatbot/new-chat-session"
TRACE_PROJECT_NAME_ENDPOINT = "api/external/v1/chatbot/get-trace-project-name-v2"
MODEL_INFO_ENDPOINT = "api/external/v1/chatbot/model-info"
MODEL_INFO_LIST_ENDPOINT = "api/external/v1/chatbot/model-info-list"

# Session management endpoints
CREATE_SESSION_ENDPOINT = "api/external/v1/chatbot/new-chatbot"
DELETE_SESSION_ENDPOINT = "api/external/v1/chatbot"
SUPPORTED_MODELS_ENDPOINT = "api/external/v1/chatbot/supported-list"

# Evaluation endpoints
EVALUATION_ENDPOINT = "api/external/v1/evaluation/bias-hallu"
SAFETY_EVALUATION_ENDPOINT = "api/external/v1/evaluation/safety"

# Other endpoints
ORG_TOKEN_USAGE_ENDPOINT = "api/external/v1/llm-labs/current-token-map"