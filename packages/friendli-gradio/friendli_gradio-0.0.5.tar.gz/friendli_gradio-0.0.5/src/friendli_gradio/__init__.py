import gradio as gr
from openai import OpenAI

from friendli_gradio.utils.token_loader import get_friendli_token


def registry(name: str, token: str | None = None, base_url: str | None = None) -> gr.Blocks:
    """
    Create a Gradio ChatInterface for Friendli models.

    Args:
        name: The model name (e.g., "Qwen/Qwen3-235B-A22B-Instruct-2507")
        token: Optional API token. If not provided, uses FRIENDLI_TOKEN environment variable.
        base_url: Optional base URL. If not provided, uses Friendli serverless endpoint.

    Returns:
        A Gradio Blocks app with ChatInterface
    """
    # Use provided token or fallback to environment variable
    api_key = token if token is not None else get_friendli_token()

    if api_key is None:
        raise ValueError(
            "No API key provided. Please set FRIENDLI_TOKEN environment variable or pass token parameter.")

    # Use provided base_url or fallback to Friendli serverless endpoint
    api_base_url = base_url or "https://api.friendli.ai/serverless/v1"

    # Initialize OpenAI client with Friendli API
    client = OpenAI(
        api_key=api_key,
        base_url=api_base_url,
    )

    def stream_response(message, history):
        """Generate streaming response from Friendli model"""
        messages = [
            {"role": "system", "content": "You are a helpful assistant."}]

        # Add conversation history
        for msg in history:
            # Only include role and content fields to ensure Friendli API compatibility
            clean_msg = {
                "role": msg["role"],
                "content": msg["content"]
            }
            messages.append(clean_msg)

        # Add current user message
        messages.append({"role": "user", "content": message})

        # Create streaming completion
        stream = client.chat.completions.create(
            model=name,
            messages=messages,
            stream=True,
        )

        response = ""
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                response += chunk.choices[0].delta.content
                yield response

    # Create and return ChatInterface
    demo = gr.ChatInterface(
        stream_response,
        title=f"Friendli Chat - {name}",
        description=f"Chat with {name} powered by Friendli API",
        type="messages"
    )

    return demo


# Make registry available for direct import
__all__ = ["registry"]
