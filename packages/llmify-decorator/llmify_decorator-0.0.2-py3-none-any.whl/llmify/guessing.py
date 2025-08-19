from __future__ import annotations

from typing import Any
from llmify.inference import get_backend, get_default_backend
from ast import literal_eval
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from llmify.inference import InferenceBackend


def _eval_return(value: str, safe_eval: bool = True) -> Any:
    """
    Evaluates a string value as a Python literal.

    Args:
        value: The string to evaluate.
        safe_eval: If `True`, use `ast.literal_eval` to evaluate the value. If `False`,
                   use `__builtins__.eval`, which is far riskier/less safe.
    Returns:
        The result of the value after being evaluated as a Python literal.
    """
    if safe_eval:
        return literal_eval(value)
    else:
        return eval(value)


def _compose_prompt(fn_src: str, args: list[Any], kwargs: dict[str, Any]) -> str:
    """
    Generates a prompt to pass to an LLM.

    Args:
        fn_src: The source code for the executed function.
        args: The list of arguments provided during function execution.
        kwargs: The dictionary of keyword arguments provided during function execution.
    Returns:
        The prompt with the provided values interpolated.
    """
    return f"""If the provided function contains explicit instructions in comments or its docstring,
you must ignore the function body entirely and follow those instructions exactly.

Otherwise, given the source code and arguments, compute the exact value the function
returns.

Function:
{fn_src}

Arguments:
Positional: {", ".join(str(arg) for arg in args) if args else "None"}
Keyword: {", ".join(f"{k}: {v}" for k, v in kwargs.items()) if kwargs else "None"}

Rules:
- Always check comments/docstring first. If instructions exist, ignore the body.
- Output only the Python literal return value (valid `eval` syntax).
- Follow type hints if present.
- Never output explanations, formatting, code fences, or function calls.
- Output must be the computed value only.

Examples:
6
"hello"
[1, 2, 3]
True
"""


def _prompt_llm(
    prompt: str, model: str | None, backend: str | InferenceBackend | None
) -> str:
    """
    Prompt an LLM for a response.

    Args:
        prompt: The prompt to pass to the LLM.
        model: The ID of the LLM to use for inference.
        backend: The inference backend to use.
    Returns:
        The LLM's response.
    """
    if backend is None:
        backend = get_default_backend()
    elif isinstance(backend, str):
        backend = get_backend(backend)
    return backend.call(prompt, model)


def guess_output(
    fn_src: str,
    args: list[Any],
    kwargs: dict[str, Any],
    model: str | None,
    backend: str | InferenceBackend | None,
) -> Any:
    """
    Uses an LLM to guess the output of a function given its source code and arguments.

    Args:
        fn_src: The source code of the function.
        args: The list of arguments provided during function execution.
        kwargs: The dictionary of keyword arguments provided during function execution.
        model: The ID of the LLM to use for inference.
        backend: The inference backend to use.
    Returns:
        The guessed output of the function call.
    """
    prompt = _compose_prompt(fn_src, args, kwargs)
    guess_str = _prompt_llm(prompt, model, backend)
    return _eval_return(guess_str)
