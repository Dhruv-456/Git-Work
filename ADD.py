import gradio as gr
def add_number(a, b):
    return a + b
interface = gr.Interface(add_number, inputs = [gr.Text(label = "first Number"), gr.Number(label = "second Number")], outputs = gr.Number(label = "Sum"))
interface.launch()