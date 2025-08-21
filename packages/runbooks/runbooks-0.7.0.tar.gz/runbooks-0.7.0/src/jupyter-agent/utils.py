"""
utils.py

This module provides helper functions to:
- Generate and update Jupyter Notebook structures.
- Execute code in a sandbox environment.
- Parse and convert execution results to notebook cell outputs.
- Export notebooks to HTML.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

import nbformat
from e2b_code_interpreter import Sandbox
from huggingface_hub import InferenceClient
from nbconvert import HTMLExporter
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook
from traitlets.config import Config
from transformers import AutoTokenizer

## --- Global Configuration and Template Loading ---

## Create a configuration for nbconvert and set up the HTML exporter
config = Config()
html_exporter = HTMLExporter(config=config, template_name="classic")

## Load the Jinja template for the LLaMA model
TEMPLATE_PATH = Path("llama3_template.jinja")
try:
    with TEMPLATE_PATH.open("r", encoding="utf-8") as f:
        llama_template = f.read()
except FileNotFoundError:
    raise FileNotFoundError(f"Template file {TEMPLATE_PATH} not found.")

MAX_TURNS = 4

## --- Code Execution Functions ---


def parse_exec_result_nb(execution: Any) -> List[Dict[str, Any]]:
    """
    Convert an E2B execution object to a list of Jupyter notebook cell outputs format.

    :param execution: Execution object from the sandbox.
    :return: List of output dictionaries.
    """
    outputs: List[Dict[str, Any]] = []

    if execution.logs.stdout:
        outputs.append(
            {
                "output_type": "stream",
                "name": "stdout",
                "text": "".join(execution.logs.stdout),
            }
        )

    if execution.logs.stderr:
        outputs.append(
            {
                "output_type": "stream",
                "name": "stderr",
                "text": "".join(execution.logs.stderr),
            }
        )

    if execution.error:
        outputs.append(
            {
                "output_type": "error",
                "ename": execution.error.name,
                "evalue": execution.error.value,
                "traceback": [line for line in execution.error.traceback.split("\n")],
            }
        )

    for result in execution.results:
        output = {
            "output_type": (
                "execute_result" if result.is_main_result else "display_data"
            ),
            "metadata": {},
            "data": {},
        }

        if result.text:
            output["data"]["text/plain"] = [result.text]  # Array for text/plain
        if result.html:
            output["data"]["text/html"] = result.html
        if result.png:
            output["data"]["image/png"] = result.png
        if result.svg:
            output["data"]["image/svg+xml"] = result.svg
        if result.jpeg:
            output["data"]["image/jpeg"] = result.jpeg
        if result.pdf:
            output["data"]["application/pdf"] = result.pdf
        if result.latex:
            output["data"]["text/latex"] = result.latex
        if result.json:
            output["data"]["application/json"] = result.json
        if result.javascript:
            output["data"]["application/javascript"] = result.javascript

        if result.is_main_result and execution.execution_count is not None:
            output["execution_count"] = execution.execution_count

        if output["data"]:
            outputs.append(output)

    return outputs


## HTML and CSS templates for notebook cells
system_template = """\
<details>
  <summary style="display: flex; align-items: center;">
    <div class="alert alert-block alert-info" style="margin: 0; width: 100%;">
      <b>System: <span class="arrow">▶</span></b>
    </div>
  </summary>
  <div class="alert alert-block alert-info">
    {}
  </div>
</details>

<style>
details > summary .arrow {{
  display: inline-block;
  transition: transform 0.2s;
}}
details[open] > summary .arrow {{
  transform: rotate(90deg);
}}
</style>
"""

user_template = """<div class="alert alert-block alert-success">
<b>User:</b> {}
</div>
"""

header_message = """<p align="center">
  <img src="cloudops-agent.png" alt="Jupyter Agent" />
</p>


<p style="text-align:center;">Let a LLM agent write and execute code inside a notebook!</p>"""

bad_html_bad = """input[type="file"] {
  display: block;
}"""


## --- Notebook Creation and Update Functions ---


def create_base_notebook(messages: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], int]:
    """
    Create the base Jupyter Notebook structure with initial cells.

    :param messages: List of conversation messages.
    :return: A tuple of the notebook data dictionary and the current code cell counter.
    """
    base_notebook = {
        "metadata": {
            "kernel_info": {"name": "python3"},
            "language_info": {
                "name": "python",
                "version": "3.12",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 0,
        "cells": [],
    }
    base_notebook["cells"].append(
        {"cell_type": "markdown", "metadata": {}, "source": header_message}
    )

    if len(messages) == 0:
        base_notebook["cells"].append(
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "source": "",
                "outputs": [],
            }
        )

    code_cell_counter = 0

    for message in messages:
        if message["role"] == "system":
            text = system_template.format(message["content"].replace("\n", "<br>"))
            base_notebook["cells"].append(
                {"cell_type": "markdown", "metadata": {}, "source": text}
            )
        elif message["role"] == "user":
            text = user_template.format(message["content"].replace("\n", "<br>"))
            base_notebook["cells"].append(
                {"cell_type": "markdown", "metadata": {}, "source": text}
            )

        elif message["role"] == "assistant" and "tool_calls" in message:
            base_notebook["cells"].append(
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "source": message["content"],
                    "outputs": [],
                }
            )

        elif message["role"] == "ipython":
            code_cell_counter += 1
            base_notebook["cells"][-1]["outputs"] = message["nbformat"]
            base_notebook["cells"][-1]["execution_count"] = code_cell_counter

        elif message["role"] == "assistant" and "tool_calls" not in message:
            base_notebook["cells"].append(
                {"cell_type": "markdown", "metadata": {}, "source": message["content"]}
            )

        else:
            raise ValueError(message)

    return base_notebook, code_cell_counter


def execute_code(sbx: Sandbox, code: str) -> Tuple[str, Any]:
    """
    Execute the given code in the provided sandbox.

    :param sbx: Sandbox instance to run the code.
    :param code: Code to execute.
    :return: Tuple of aggregated output string and the raw execution object.
    """
    execution = sbx.run_code(code, on_stdout=lambda data: print("stdout:", data))
    output = ""
    if len(execution.logs.stdout) > 0:
        output += "\n".join(execution.logs.stdout)
    if len(execution.logs.stderr) > 0:
        output += "\n".join(execution.logs.stderr)
    if execution.error is not None:
        output += execution.error.traceback
    return output, execution


def parse_exec_result_llm(execution: Any) -> str:
    """
    Parse the execution results and return a single concatenated output string.

    :param execution: Execution object from the sandbox.
    :return: Concatenated string of output messages.
    """
    output = ""
    if len(execution.logs.stdout) > 0:
        output += "\n".join(execution.logs.stdout)
    if len(execution.logs.stderr) > 0:
        output += "\n".join(execution.logs.stderr)
    if execution.error is not None:
        output += execution.error.traceback
    return output


def update_notebook_display(notebook_data):
    notebook = nbformat.from_dict(notebook_data)
    notebook_body, _ = html_exporter.from_notebook_node(notebook)
    notebook_body = notebook_body.replace(bad_html_bad, "")
    return notebook_body


## --- Interactive Notebook Generation ---


def run_interactive_notebook(
    client: InferenceClient,
    model: str,
    tokenizer: Any,
    messages: List[Dict[str, Any]],
    sbx: Sandbox,
    max_new_tokens: int = 512,
) -> Any:
    """
    Generator function that iteratively builds and updates the Jupyter Notebook.

    :param client: Hugging Face InferenceClient for text generation.
    :param model: Model identifier.
    :param tokenizer: Tokenizer corresponding to the model.
    :param messages: List of conversation messages.
    :param sbx: Sandbox instance for executing code.
    :param max_new_tokens: Maximum tokens to generate per turn.
    :yield: Tuple containing updated notebook HTML, notebook data, and messages.
    """
    notebook_data, code_cell_counter = create_base_notebook(messages)
    turns = 0

    # code_cell_counter = 0
    while turns <= MAX_TURNS:
        turns += 1
        input_tokens = tokenizer.apply_chat_template(
            messages,
            chat_template=llama_template,
            builtin_tools=["code_interpreter"],
            add_generation_prompt=True,
        )
        model_input = tokenizer.decode(input_tokens)

        print(f"Model input:\n{model_input}\n{'='*80}")

        response_stream = client.text_generation(
            model=model,
            prompt=model_input,
            details=True,
            stream=True,
            do_sample=True,
            repetition_penalty=1.1,
            temperature=0.8,
            max_new_tokens=max_new_tokens,
        )

        assistant_response = ""
        tokens = []

        code_cell = False
        for i, chunk in enumerate(response_stream):
            if not chunk.token.special:
                content = chunk.token.text
            else:
                content = ""
            tokens.append(chunk.token.text)
            assistant_response += content

            if len(tokens) == 1:
                create_cell = True
                code_cell = "<|python_tag|>" in tokens[0]
                if code_cell:
                    code_cell_counter += 1
            else:
                create_cell = False

            ## Update notebook cells in real-time
            if create_cell:
                if "<|python_tag|>" in tokens[0]:
                    notebook_data["cells"].append(
                        {
                            "cell_type": "code",
                            "execution_count": None,
                            "metadata": {},
                            "source": assistant_response,
                            "outputs": [],
                        }
                    )
                else:
                    notebook_data["cells"].append(
                        {
                            "cell_type": "markdown",
                            "metadata": {},
                            "source": assistant_response,
                        }
                    )
            else:
                notebook_data["cells"][-1]["source"] = assistant_response
            if i % 16 == 0:
                yield update_notebook_display(notebook_data), notebook_data, messages
        yield update_notebook_display(notebook_data), notebook_data, messages

        ## If a code cell was generated, execute the code
        if code_cell:
            notebook_data["cells"][-1]["execution_count"] = code_cell_counter

            exec_result, execution = execute_code(sbx, assistant_response)
            messages.append(
                {
                    "role": "assistant",
                    "content": assistant_response,
                    "tool_calls": [
                        {
                            "type": "function",
                            "function": {
                                "name": "code_interpreter",
                                "arguments": {"code": assistant_response},
                            },
                        }
                    ],
                }
            )
            messages.append(
                {
                    "role": "ipython",
                    "content": parse_exec_result_llm(execution),
                    "nbformat": parse_exec_result_nb(execution),
                }
            )

            ## Update the last code cell with execution results
            notebook_data["cells"][-1]["outputs"] = parse_exec_result_nb(execution)
            update_notebook_display(notebook_data)
        else:
            messages.append({"role": "assistant", "content": assistant_response})
            if tokens[-1] == "<|eot_id|>":
                break

    yield update_notebook_display(notebook_data), notebook_data, messages
