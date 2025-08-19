from abc import ABC, abstractmethod

_default_backend = None
backend_registry = {}


def register_backend(name: str):
    """
    Decorator for registering a class as a backend with a name.

    Args:
        name: The name to register the backend under. This name can be used as input
              to `inference.get_backend`.
    """

    def wrapper(cls):
        backend_registry[name] = cls
        return cls

    return wrapper


class InferenceBackend(ABC):
    """Abstract class encapsulating a backend for obtaining LLM responses."""

    def call(self, prompt: str, model: str | None) -> str:
        """
        Prompt an LLM for a response.

        Args:
            prompt: The prompt to pass to the LLM.
            model: The ID of the model from which to obtain the response.
        Returns:
            The LLM's response.
        """
        model = model or self.default_model
        return self._generate_completion(prompt, model)

    @abstractmethod
    def _generate_completion(self, prompt: str, model: str) -> str:
        """
        Backend-specific logic for obtaining a response from a model.

        Args:
            prompt: The prompt to pass to the LLM
            model: The ID of the model from which to obtain the response.
        Returns:
            The LLM's response.
        """
        pass


@register_backend("openai")
class OpenAIBackend(InferenceBackend):
    """Inference backend for the OpenAI API."""

    def __init__(self):
        try:
            from openai import OpenAI

            self.client = OpenAI()
        except ImportError:
            raise ImportError(
                "Using `OpenAIBackend` requires that the `openai` library is installed."
                "To install it, run the following command: `pip install openai`"
            )
        self.default_model = "gpt-4o"

    def _generate_completion(self, prompt: str, model: str) -> str:
        completion = self.client.responses.create(model=model, input=prompt)
        return completion.output_text


def get_backend(name: str) -> InferenceBackend:
    """
    Get an inference backend from a registered name.

    Available backends by name:
    - **"openai"**: `OpenAIBackend`

    Args:
        name: The name of the backend to retrieve.
    Returns:
        The backend corresponding to the given name.
    """
    backend_cls = backend_registry.get(name)
    if backend_cls is None:
        available_backends = ",".join(f"'{name}'" for name in backend_registry.keys())
        raise ValueError(
            f"No available inference backend '{name}'."
            f"Available backends: {available_backends}'"
        )
    return backend_cls()


def set_default_backend(backend: str | InferenceBackend) -> None:
    """
    Sets the default backend to be used for inference.

    Args:
        backend: The inference backend to be set as the default.
    """
    global _default_backend
    if isinstance(backend, str):
        _default_backend = get_backend(backend)
    else:
        _default_backend = backend


def get_default_backend() -> InferenceBackend:
    """
    Gets the default backend used for inference.

    Returns:
        An instance of the default backend class.
    """
    global _default_backend
    if _default_backend is None:
        _default_backend = OpenAIBackend()
    return _default_backend
