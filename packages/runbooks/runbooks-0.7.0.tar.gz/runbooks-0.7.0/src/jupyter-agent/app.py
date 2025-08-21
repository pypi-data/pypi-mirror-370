"""
app.py

Main entry point for the Jupyter Agent. This file sets up the Gradio user interface,
handles session-specific sandbox initialization, file management, and orchestrates
the interactive notebook generation and code execution.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Tuple

import gradio as gr
from e2b_code_interpreter import Sandbox
from gradio.utils import get_space
from huggingface_hub import InferenceClient
from transformers import AutoTokenizer

## Import helper functions from utils with type hints
from utils import (
    create_base_notebook,
    run_interactive_notebook,
    update_notebook_display,
)

from runbooks.utils.logger import configure_logger

## ✅ Configure Logger
logger = configure_logger(__name__)

## Load environment variables if not running in a Hugging Face Space
if not get_space():
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except (ImportError, ModuleNotFoundError):
        logger.warning("python-dotenv not installed; proceeding without .env support.")
        pass

## Global configurations
## For sandbox execution and Hugging Face API authentication
E2B_API_KEY = os.environ["E2B_API_KEY"]
HF_TOKEN = os.environ["HF_TOKEN"]
## Set a limit on the number of new tokens generated per request.
DEFAULT_MAX_TOKENS = 512
## A dictionary used to keep track of separate execution environments (sandboxes) for each session.
SANDBOXES = {}
## For storing temporary files (e.g., generated notebooks)
TMP_DIR = "./tmp/"
## Ensure the temporary directory exists
if not os.path.exists(TMP_DIR):
    os.makedirs(TMP_DIR)

## Initialize a base notebook on startup
notebook_data = create_base_notebook([])[0]
with open(TMP_DIR + "jupyter-agent.ipynb", "w", encoding="utf-8") as f:
    json.dump(notebook_data, f, indent=2)

## Read default system prompt
try:
    with open("ds-system-prompt.txt", "r", encoding="utf-8") as f:
        DEFAULT_SYSTEM_PROMPT: str = f.read()
except FileNotFoundError:
    logger.error("ds-system-prompt.txt not found. Please ensure it is available.")
    DEFAULT_SYSTEM_PROMPT = ""


## --- Main Execution Function ---
def execute_jupyter_agent(
    system_prompt: str,
    user_input: str,
    max_new_tokens: int,
    model: str,
    files: List[str],
    message_history: List[Dict[str, Any]],
    request: gr.Request,
) -> Tuple[str, List[Dict[str, Any]], str]:
    """
    Core callback function that orchestrates the interactive notebook generation.

    :param system_prompt: The system prompt template.
    :param user_input: User's input command.
    :param max_new_tokens: Maximum number of tokens to generate.
    :param model: Identifier for the language model.
    :param files: List of file paths uploaded by the user.
    :param message_history: History of conversation messages.
    :param request: Gradio request object with session details.
    :return: A tuple containing the updated notebook HTML, updated message history,
             and the path to the generated notebook file.
    """
    ## Retrieve or create a sandbox instance for the given session.
    if request.session_hash not in SANDBOXES:
        ## Create a new Sandbox with the E2B API key and stored
        SANDBOXES[request.session_hash] = Sandbox(api_key=E2B_API_KEY)
    sbx = SANDBOXES[request.session_hash]

    ## Create session-specific directory for saving notebook
    save_dir = os.path.join(TMP_DIR, request.session_hash)
    os.makedirs(save_dir, exist_ok=True)
    save_dir = os.path.join(save_dir, "jupyter-agent.ipynb")

    ## Initializes an inference client for text generation using the provided Hugging Face token.
    client = InferenceClient(api_key=HF_TOKEN)

    ## Loads the tokenizer corresponding to the chosen model.
    tokenizer = AutoTokenizer.from_pretrained(model)
    # model = "meta-llama/Llama-3.1-8B-Instruct"

    ## Process uploaded files
    filenames = []
    if files is not None:
        for filepath in files:
            filpath = Path(filepath)
            with open(filepath, "rb") as file:
                print(f"uploading {filepath}...")
                ## Write the file into the sandbox’s file system (allowing the agent to access it during execution).
                sbx.files.write(filpath.name, file)
                filenames.append(filpath.name)

    ## Initialize message_history if it doesn't exist
    if len(message_history) == 0:
        message_history.append(
            {
                "role": "system",
                "content": system_prompt.format("- " + "\n- ".join(filenames)),
            }
        )
    message_history.append({"role": "user", "content": user_input})

    ## Outputs the current conversation history for debugging purposes.
    logger.debug(f"Message history: {message_history}")

    ## Generate notebook updates by streaming responses
    for notebook_html, notebook_data, messages in run_interactive_notebook(
        client, model, tokenizer, message_history, sbx, max_new_tokens=max_new_tokens
    ):
        message_history = messages

        ## Yield intermediate UI updates with a fixed download path (initial version)
        yield notebook_html, message_history, TMP_DIR + "jupyter-agent.ipynb"

    ## Save the final notebook JSON data to a specified path.
    with open(save_dir, "w", encoding="utf-8") as f:
        json.dump(notebook_data, f, indent=2)
    yield notebook_html, message_history, save_dir
    logger.info(f"Notebook saved to {save_dir}")


def clear(msg_state):
    msg_state = []
    return update_notebook_display(create_base_notebook([])[0]), msg_state


## Gradio components fill the full height of the viewport, allow scrolling, and have appropriate padding
custom_css = """
#component-0 {
    height: 100vh;
    overflow-y: auto;
    padding: 20px;
}

.gradio-container {
    height: 100vh !important;
}

.contain {
    height: 100vh !important;
}
"""
## TODO
# footer {
#         visibility: hidden;
# }


## Build and return the Gradio Blocks interface for the Jupyter Agent.
# with gr.Blocks(css=custom_css) as poc:
with gr.Blocks() as poc:
    msg_state = gr.State(value=[])

    html_output = gr.HTML(value=update_notebook_display(create_base_notebook([])[0]))

    user_input = gr.Textbox(
        value="Solve the Bayes' theorem equation and plot the results.",
        lines=3,
        label="User input",
    )

    with gr.Row():
        generate_btn = gr.Button("▶️ Let's go!")
        clear_btn = gr.Button("🧹 Clear")

    file = gr.File(
        TMP_DIR + "jupyter-agent.ipynb", label="💾 Download Jupyter Notebook"
    )

    with gr.Accordion("Upload files", open=False):
        files = gr.File(label="Upload files to use", file_count="multiple")

    with gr.Accordion("Advanced Settings", open=False):
        system_input = gr.Textbox(
            label="System Prompt",
            value=DEFAULT_SYSTEM_PROMPT,
            elem_classes="input-box",
            lines=8,
        )
        with gr.Row():
            max_tokens = gr.Number(
                label="Max New Tokens",
                value=DEFAULT_MAX_TOKENS,
                minimum=128,
                maximum=2048,
                step=8,
                interactive=True,
            )

            model = gr.Dropdown(
                # value="meta-llama/Llama-3.1-8B-Instruct",
                value="meta-llama/Llama-3.3-70B-Instruct",
                choices=[
                    ## Text only instruct-tuned model in 70B size (text in/text out).
                    "meta-llama/Llama-3.3-70B-Instruct",
                    ## Pretrained and fine-tuned text models with sizes
                    "meta-llama/Llama-3.1-8B-Instruct",
                    ## pretrained and instruction-tuned image reasoning generative models in 11B and 90B sizes (text + images in / text out)
                    "meta-llama/Llama-3.2-3B-Instruct",
                    "meta-llama/Llama-3.2-11B-Vision-Instruct",
                ],
                label="Models",
            )

    generate_btn.click(
        fn=execute_jupyter_agent,
        inputs=[system_input, user_input, max_tokens, model, files, msg_state],
        outputs=[html_output, msg_state, file],
    )

    clear_btn.click(fn=clear, inputs=[msg_state], outputs=[html_output, msg_state])

    poc.load(
        fn=None,
        inputs=None,
        outputs=None,
        js=""" () => {
    if (document.querySelectorAll('.dark').length) {
        document.querySelectorAll('.dark').forEach(el => el.classList.remove('dark'));
    }
}
""",
    )

## Main entry point: launch the Gradio interface.
## Disable server-side rendering (i.e., client-side rendering is used).
poc.launch(ssr_mode=False, pwa=True, share=True)
