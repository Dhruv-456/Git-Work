import gradio as gr
def square_number(number):
    return number**2
interface = gr.Interface(fn = square_number, inputs = gr.Slider(minimum = 0, maximum = 100, label = "Select a number"), outputs = gr.Number(label = "Result"))
interface.launch()