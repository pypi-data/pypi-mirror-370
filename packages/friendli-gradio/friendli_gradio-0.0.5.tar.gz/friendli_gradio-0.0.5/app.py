import gradio as gr
import friendli_gradio

gr.load(
    name='Qwen/Qwen3-235B-A22B-Instruct-2507',
    src=friendli_gradio.registry
).launch(share=False)
