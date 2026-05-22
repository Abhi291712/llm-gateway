"""
config.py

config.py - Central project configuration and environment setup.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
OPENAI_API_KEY    = os.environ.get("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
GROQ_API_KEY      = os.environ.get("GROQ_API_KEY")
GEMINI_API_KEY    = os.environ.get("GEMINI_API_KEY")

# Model Registry
MODELS = {
    "openai":    "gpt-4o-mini",
    "groq":      "groq/llama-3.3-70b-versatile",
    "anthropic": "anthropic/claude-3-5-sonnet-20240620",
    "gemini":    "gemini/gemini-1.5-flash",
}

# Routing Map — task type to model chain
ROUTING = {
    "code":    ["gpt-4o", "gpt-4o-mini", "groq/llama-3.3-70b-versatile"],
    "summary": ["gpt-4o-mini", "groq/llama-3.3-70b-versatile"],
    "general": ["groq/llama-3.3-70b-versatile", "gpt-4o-mini"],
}

# Cache Config
CACHE_TYPE         = "local"
SEMANTIC_THRESHOLD = 0.95
REDIS_URL          = os.environ.get("REDIS_URL", "redis://localhost:6379")

# Observability
LANGFUSE_PUBLIC_KEY = os.environ.get("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY = os.environ.get("LANGFUSE_SECRET_KEY")
LANGFUSE_HOST       = os.environ.get("LANGFUSE_HOST", "https://cloud.langfuse.com")