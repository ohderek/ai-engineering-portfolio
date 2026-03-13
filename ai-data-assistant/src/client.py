"""
Step 1: Working with the Claude API.

Thin wrapper around the Anthropic SDK that centralises model choice,
streaming, and error handling so every feature uses the same setup.
"""

import anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-opus-4-6"


def get_client() -> anthropic.Anthropic:
    return anthropic.Anthropic()


def stream_response(
    messages: list[dict],
    system: str = "",
    max_tokens: int = 2048,
) -> str:
    """Stream a response from Claude and return the full text."""
    client = get_client()

    full_text = ""
    with client.messages.stream(
        model=MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=messages,
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            full_text += text

    print()  # newline after stream ends
    return full_text


def single_response(
    messages: list[dict],
    system: str = "",
    max_tokens: int = 2048,
) -> str:
    """Single (non-streaming) API call — used for structured outputs."""
    client = get_client()

    response = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=messages,
    )

    return next(
        (block.text for block in response.content if block.type == "text"), ""
    )
