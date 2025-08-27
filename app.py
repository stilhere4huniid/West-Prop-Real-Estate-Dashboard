import gradio as gr
import subprocess
import os
from pathlib import Path

def run_streamlit():
    # Set the working directory to the current file's directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Run Streamlit in the background
    process = subprocess.Popen([
        "streamlit", 
        "run", 
        "real_estate_dashboard.py",
        "--server.port=7860",
        "--server.headless=true",
        "--server.enableCORS=false"
    ])
    
    # Return a message and the public URL (this will be shown in the Gradio interface)
    return "WestProp Real Estate Dashboard is loading... Please wait a moment and then check the output below for the public URL."

# Create a simple Gradio interface
iface = gr.Interface(
    fn=run_streamlit,
    inputs=None,
    outputs="text",
    title="WestProp Real Estate Dashboard",
    description=(
        "Click the button below to launch the WestProp Real Estate Dashboard. "
        "This may take a moment to load."
    )
)

# Add some styling to make it look better
iface.css = """
    .gradio-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
    }
    h1 {
        color: #1e3a8a;
    }
    .output-text {
        padding: 20px;
        background: #f0f9ff;
        border-radius: 5px;
        margin-top: 20px;
    }
"""

if __name__ == "__main__":
    iface.launch(share=True, server_port=7860, server_name="0.0.0.0")
