"""
Helpers for defining dynamic UIs for Lumera agents.
"""

import functools
import json
import os
import sys
from typing import Callable, List

_UI_INPUTS_ATTRIBUTE = "_lumera_ui_inputs"


# ruff's ANN* rules require explicit annotations for public callables.  The
# signature below purposefully uses ``Any`` for parameters that accept a wide
# range of values (e.g. *default*, **kwargs).  Consumers of the SDK can supply
# JSON-serialisable values and the decorator forwards them verbatim to the
# backend.


def input(
    name: str,
    type: type,
    label: str = "",
    default: object | None = None,
    description: str = "",
    widget: str = "",
    options: List[object] | None = None,
    **kwargs: object,
) -> Callable[[Callable[..., object]], Callable[..., object]]:
    """
    Decorator to define a UI input for the main agent function.

    Args:
        name: The variable name passed to the function (e.g., "user_name").
        type: The Python data type (str, int, float, bool).
        label: The user-friendly text for the UI (e.g., "Your Name").
        default: A default value for the input field.
        description: Help text displayed below the input.
        widget: A hint for the frontend for special rendering (e.g., "textarea", "slider").
        options: A list of choices for dropdowns or radio buttons.
        **kwargs: For future extensions like 'min', 'max', 'step' for sliders.
    """

    def decorator(func: Callable[..., object]) -> Callable[..., object]:
        if not hasattr(func, _UI_INPUTS_ATTRIBUTE):
            setattr(func, _UI_INPUTS_ATTRIBUTE, [])

        # Map Python types to simple string identifiers for JSON
        type_str_map = {
            str: "string",
            int: "integer",
            float: "float",
            bool: "boolean",
        }
        type_name = type_str_map.get(type, str(type))

        # Prepend to handle decorators stacked top-down as they are evaluated bottom-up
        getattr(func, _UI_INPUTS_ATTRIBUTE).insert(
            0,
            {
                "name": name,
                "type": type_name,
                "label": label or name.replace("_", " ").title(),
                "default": default,
                "description": description,
                "widget": widget,
                "options": options,
                **kwargs,
            },
        )

        @functools.wraps(func)
        def wrapper(*args: object, **kwargs: object) -> object:
            # The wrapper itself doesn't need to do anything special at runtime
            return func(*args, **kwargs)

        return wrapper

    return decorator


def _print_inputs_schema_as_json(module_name: str, function_name: str = "main") -> None:
    """
    Introspection utility to find a function in a module, extract the
    UI schema defined by @input decorators, and print it as a JSON string.

    This function is intended to be called by the Lumera backend, not by users.
    """
    try:
        # Dynamically import the specified module
        __import__(module_name)
        module = sys.modules[module_name]
        func = getattr(module, function_name)

        if hasattr(func, _UI_INPUTS_ATTRIBUTE):
            schema = getattr(func, _UI_INPUTS_ATTRIBUTE)
            print(json.dumps(schema))
        else:
            # No decorators found, print an empty list
            print(json.dumps([]))

    except (ImportError, AttributeError):
        # If module/function doesn't exist, it's not an error, just no UI.
        print(json.dumps([]))
    except Exception as e:
        # For other errors, log to stderr for backend debugging and print empty.
        print(f"Error during UI schema introspection: {e}", file=sys.stderr)
        print(json.dumps([]))


# This block allows the backend to run this file as a script for introspection
if __name__ == "__main__" and len(sys.argv) > 2 and sys.argv[1] == "--introspect":
    # The backend will call: python3 -m lumera.ui --introspect <path_to_agent_file>
    # We need to add the module's directory to the path to enable the import.
    agent_file_path = sys.argv[2]
    module_dir = os.path.dirname(agent_file_path)
    module_name = os.path.basename(agent_file_path).replace('.py', '')

    # Add agent's directory to path to allow it to be imported
    sys.path.insert(0, module_dir)

    _print_inputs_schema_as_json(module_name)
