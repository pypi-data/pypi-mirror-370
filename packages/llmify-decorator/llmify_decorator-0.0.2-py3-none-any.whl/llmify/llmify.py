from __future__ import annotations

import inspect
from functools import wraps
from llmify.guessing import guess_output
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from llmify.inference import InferenceBackend


def llmify(model: str | None = None, backend: str | InferenceBackend | None = None):
    """
    Decorator that replaces a function's execution with an LLM inference call using
    its source code and arguments.

    Args:
        model: The ID of the LLM model to use. This is passed to the `InferenceBackend`
               instance.
        backend: The inference backend to use. This is either a string containing the
                 name of the inference backend to use (currently only "openai" is
                 supported), or an `InferenceBackend` instance.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            fn_source = inspect.getsource(func)
            return guess_output(fn_source, args, kwargs, model, backend)

        return wrapper

    return decorator
