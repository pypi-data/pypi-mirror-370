"""Public API for stripgpt.

Provides convenient imports:

	from stripgpt import clean_text, START, END
"""

from .core import clean_text, detect_artifacts, START, END  # noqa: F401

__version__ = "0.2.0"

__all__ = ["clean_text", "detect_artifacts", "START", "END", "__version__"]

