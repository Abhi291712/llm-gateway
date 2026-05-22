"""
basic_completion.py

Problem: Different LLM providers need different SDKs and API integrations.
Solution: LiteLLM gives one unified function - just change the model name.
"""

from litellm import completion
from config import MODELS


def call_llm(prompt: str, provider: str = "openai") -> str:
    """
    One function. Any provider. No SDK switching.
    """
    model = MODELS.get(provider, MODELS["openai"])

    response = completion(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    prompt = "Explain RAG in one sentence"

    for provider in ["openai", "groq"]:
        print(f"\n[{provider.upper()}]")
        result = call_llm(prompt, provider=provider)
        print(result)