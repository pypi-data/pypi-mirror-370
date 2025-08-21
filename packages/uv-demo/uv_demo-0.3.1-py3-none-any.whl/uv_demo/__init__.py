"""The uv-demo package."""

from importlib.metadata import version

from .greetings import LIB_NAME, say_goodbye, say_hello

__version__ = version(LIB_NAME)

__all__ = [
    "__version__",
    "LIB_NAME",
    "say_hello",
    "say_goodbye",
]
