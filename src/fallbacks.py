"""
fallbacks.py - Automatic fallback handling across LLM providers.
"""

from litellm import completion
from src.config import MODELS


def call_with_fallback(prompt: str, primary: str = "openai") -> str:
    """
    Try primary model first.
    If it fails, fall back to the next available model.
    """
    fallback_chain = [m for k, m in MODELS.items() if k != primary]
    primary_model  = MODELS.get(primary, MODELS["openai"])

    response = completion(
        model=primary_model,
        fallbacks=fallback_chain,
        messages=[{"role": "user", "content": prompt}]
    )

    print(f"Responded by: {response.model}")
    return response.choices[0].message.content


if __name__ == "__main__":
    result = call_with_fallback(
        prompt="Explain RAG in one sentence",
        primary="openai"
    )
    print(result)