import friendli_gradio

app = friendli_gradio.registry(
    name='Qwen/Qwen3-235B-A22B-Instruct-2507',
    # base_url='http://localhost:8000/v1'
)
app.launch()
