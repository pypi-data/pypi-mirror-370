# `friendli-gradio`

is a Python package that makes it very easy for developers to create machine learning apps that are powered by Friendli's serverless API.

# Installation

You can install `friendli-gradio` directly using pip:

```bash
pip install friendli-gradio
```

That's it! 

# Basic Usage

Just like if you were to use the `friendli` API, you should first save your Friendli API key to this environment variable:

```
export FRIENDLI_TOKEN=<your token>
```

Then in a Python file, write:

```python
import gradio as gr
import friendli_gradio

gr.load(
    name='Qwen/Qwen3-235B-A22B-Instruct-2507',
    src=friendli_gradio.registry,
).launch()
```

Run the Python file, and you should see a Gradio ChatInterface connected to the model on Friendli!

## Alternative: Manual Implementation

If you prefer more control, you can also use the traditional approach:

```python
import os
from openai import OpenAI
import gradio as gr

client = OpenAI(
    api_key=os.getenv("FRIENDLI_TOKEN"),
    base_url="https://api.friendli.ai/serverless/v1",
)

def stream_response(message, history):
    messages = [{"role": "system", "content": "You are a helpful assistant."}]
    for user_msg, assistant_msg in history:
        messages.append({"role": "user", "content": user_msg})
        if assistant_msg:
            messages.append({"role": "assistant", "content": assistant_msg})
    messages.append({"role": "user", "content": message})

    stream = client.chat.completions.create(
        model="Qwen/Qwen3-235B-A22B-Instruct-2507",
        messages=messages,
        stream=True,
    )

    response = ""
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            response += chunk.choices[0].delta.content
            yield response

demo = gr.ChatInterface(stream_response)
demo.launch()
```

But with `friendli-gradio`, you can achieve the same result with just 4 lines of code!

![ChatInterface](chatinterface.png)