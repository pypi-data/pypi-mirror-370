## src/runbooks/aws/__init__.py
"""AWS Runbooks Initialization Module."""

import importlib
import os
import sys

from runbooks.utils.logger import configure_logger

logger = configure_logger(__name__)


def discover_scripts():
    """
    Dynamically discovers and lists all AWS scripts in this package.

    Returns:
        dict: A mapping of script names to their main functions.
    """
    scripts = {}
    aws_path = os.path.dirname(__file__)
    for filename in os.listdir(aws_path):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = f"runbooks.aws.{filename[:-3]}"
            try:
                module = importlib.import_module(module_name)
                if hasattr(module, "main"):
                    scripts[filename[:-3]] = module.main
            except Exception as e:
                logger.error(f"Error importing {module_name}: {e}")
    return scripts


def run_script(script_name, *args):
    """
    Executes the given script by name.

    Args:
        script_name (str): The name of the script to execute.
        *args: Additional arguments to pass to the script.
    """
    scripts = discover_scripts()
    if script_name in scripts:
        try:
            scripts[script_name](*args)
        except Exception as e:
            logger.error(f"Error executing script {script_name}: {e}")
    else:
        logger.error(f"Script {script_name} not found.")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.error("Usage: python -m runbooks.aws <script_name> [<args>]")
        sys.exit(1)

    run_script(sys.argv[1], *sys.argv[2:])
