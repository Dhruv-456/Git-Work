import gradio as gr
from PIL import Image
def resize_image(image, width, height):
    resized_image = image.resize((width, height))
    return resized_image
interface = gr.Interface(fn = resize_image, inputs = [gr.Image(type = "pil", label = "Upload Image"), gr.Number(minimum = 100, maximum = 512, label = "width"), gr.Number(minimum = 100, maximum = 512, label = "height")], outputs = gr.Image(label ="Resized Image"))
interface.launch()