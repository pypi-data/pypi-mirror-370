# `friendli-gradio`

<a target="_blank" href="https://colab.research.google.com/github/friendliai/friendli-gradio/blob/main/examples/colab.ipynb">
  <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/>
</a>

is a Python package that makes it very easy for developers to create machine learning apps that are powered by Friendli's API.

# Installation

You can install `friendli-gradio` directly using pip:

```bash
pip install -U friendli-gradio
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
