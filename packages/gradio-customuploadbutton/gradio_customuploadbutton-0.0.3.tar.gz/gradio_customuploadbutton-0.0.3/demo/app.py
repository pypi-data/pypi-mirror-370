
import gradio as gr
from gradio_customuploadbutton import CustomUploadButton


example = CustomUploadButton().example_value()

with gr.Blocks() as demo:
    with gr.Row():
        CustomUploadButton(label="Blank"),  # blank component
        CustomUploadButton(value=example, label="Populated"),  # populated component


if __name__ == "__main__":
    demo.launch()
