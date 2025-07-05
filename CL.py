import gradio as gr

def Calculator(number1, number2, operation):
    if operation == "Addition":
        return number1 + number2
    elif operation == "Subtraction":
        return number1 - number2
    elif operation == "Multiplication":
        return number1 * number2
    elif operation == "Division":
        return number1 / number2
    elif operation == "Exponentiation":
        return number1 ** number2
    elif operation == "Percentage":
        return (number1 / number2) * 100
    else:
        return "Invalid operation"

interface = gr.Interface(
    fn=Calculator,
    inputs=[
        gr.Number(label="Enter 1st Number"),
        gr.Number(label="Enter 2nd Number"),
        gr.Dropdown(choices=["Addition", "Subtraction", "Multiplication", "Division", "Exponentiation", "Percentage"], label="Operations")
    ],
    outputs=gr.Number(label="Result")
)

interface.launch()