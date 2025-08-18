#!/usr/bin/env python3
"""
Simple shell script template generator.
Creates basic shell scripts with help, arg handling, and empty task functions.
"""

import inspect
import os
from typing import Any, Callable, Dict, Optional


class _Generator:
    """Generates simple shell scripts from Python task functions."""

    def __init__(self, module):
        self.functions: Dict[str, Dict] = {}
        self.default_task: Optional[str] = None
        self.add_functions_from_module(module)

    def add_function(self, name: str, func: Callable, is_default: bool = False):
        """Add a task function to be converted to shell."""
        params = self._get_function_params(func)
        self.functions[name] = {"params": params}

        if is_default:
            self.default_task = name

    def add_functions_from_module(self, module) -> int:
        """Add all task functions from a Python module. Returns count added."""
        count = 0
        default_task = getattr(module, "DEFAULT", None)

        for name in dir(module):
            obj = getattr(module, name)

            # Skip private and non-callable
            if name.startswith("_") or not callable(obj):
                continue

            # Skip imports
            if hasattr(obj, "__module__") and obj.__module__ != module.__name__:
                continue

            is_default = name == default_task
            self.add_function(name, obj, is_default)
            count += 1

        return count

    def generate_script(self) -> str:
        """Generate the complete shell script."""
        parts = [
            self._generate_header(),
            self._generate_utilities(),
            self._generate_task_functions(),
            self._generate_help_function(),
            self._generate_argument_parsing(),
            self._generate_task_execution(),
        ]

        return "\n".join(parts)

    def generate(self, filename: str = "tasks.sh") -> None:
        """Save the generated script to a file and make it executable."""
        script_content = self.generate_script()

        with open(filename, "w") as f:
            f.write(script_content)

        os.chmod(filename, 0o755)

    def _get_function_params(self, func: Callable) -> Dict[str, Any]:
        """Extract function parameters with defaults."""
        sig = inspect.signature(func)
        params = {}

        for param_name, param in sig.parameters.items():
            params[param_name] = {
                "required": param.default == inspect.Parameter.empty,
                "default": param.default if param.default != inspect.Parameter.empty else None,
            }

        return params

    def _generate_header(self) -> str:
        """Generate shell script header."""
        return """#!/bin/bash
set -euo pipefail

# Simple task runner script
# Edit the functions below to add your commands

"""

    def _generate_utilities(self) -> str:
        """Generate utility functions."""
        return """# Utilities
run_cmd() {
    echo "Running: $*"
    "$@"
}

log_info() {
    echo "[INFO] $1"
}

log_error() {
    echo "[ERROR] $1" >&2
}

"""

    def _generate_task_functions(self) -> str:
        """Generate empty task functions."""
        if not self.functions:
            return "# No tasks defined\n\n"

        content = "# Task functions. Fill in functionality from tasks.py here\n"

        for func_name, func_info in self.functions.items():
            params = func_info["params"]

            # Function header
            content += f"\n{func_name}() {{\n"

            # Parameter handling
            for param_name, param_info in params.items():
                var_name = param_name.upper()
                if param_info["required"]:
                    content += f'    [ -z "${{{var_name}:-}}" ] && {{ log_error "Missing required parameter: --{param_name}"; exit 1; }}\n'
                elif param_info["default"] is not None:
                    default_val = param_info["default"]
                    content += f'    {var_name}="${{{var_name}:-{default_val}}}"\n'

            content += f'    log_info "Running task: {func_name}"\n'
            content += "    \n"
            content += f'    log_info "Task {func_name} completed"\n'
            content += "}\n"

        return content

    def _generate_help_function(self) -> str:
        """Generate help function."""
        content = """
show_help() {
    echo "Usage: $0 [task] [options]"
    echo ""
    echo "Tasks:"
"""

        for func_name, func_info in self.functions.items():
            params = func_info["params"]
            param_str = ""

            if params:
                param_parts = []
                for param_name, param_info in params.items():
                    if param_info["required"]:
                        param_parts.append(f"--{param_name} <value>")
                    else:
                        param_parts.append(f"[--{param_name} <value>]")
                param_str = " " + " ".join(param_parts)

            default_marker = " (default)" if func_name == self.default_task else ""
            content += f'    echo "  {func_name}{param_str}{default_marker}"\n'

        content += """    echo ""
    echo "Options:"
    echo "  -h, --help    Show this help"
}

"""
        return content

    def _generate_argument_parsing(self) -> str:
        """Generate argument parsing logic."""
        content = """# Parse arguments
TASK=""
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
"""

        # Add parameter parsing
        all_params = set()
        for func_info in self.functions.values():
            all_params.update(func_info["params"].keys())

        for param_name in sorted(all_params):
            var_name = param_name.upper()
            content += f"""        --{param_name})
            {var_name}="$2"
            shift 2
            ;;
"""

        content += """        -*)
            log_error "Unknown option: $1"
            show_help
            exit 1
            ;;
        *)
            TASK="$1"
            shift
            ;;
    esac
done

"""

        # Default task handling
        if self.default_task:
            content += f"""# Set default task
[ -z "$TASK" ] && TASK="{self.default_task}"

"""
        else:
            content += """# Require task
if [ -z "$TASK" ]; then
    log_error "No task specified"
    show_help
    exit 1
fi

"""

        return content

    def _generate_task_execution(self) -> str:
        """Generate task execution logic."""
        content = """# Run task
case "$TASK" in
"""

        for func_name in self.functions:
            content += f"""    {func_name})
        {func_name}
        ;;
"""

        content += """    *)
        log_error "Unknown task: $TASK"
        show_help
        exit 1
        ;;
esac
"""

        return content
