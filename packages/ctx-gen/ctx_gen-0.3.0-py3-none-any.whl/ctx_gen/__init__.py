"""ctx-gen: An context generator that converts project structure and file contents into LLM-friendly formats."""

__version__ = "0.3.0"
__author__ = "foxmcp"
__email__ = "ctx-gen@foxmcp.com"

from .cli import (
    ContextGenerator,
    Config,
    FileInfo,
    ScanResult,
    BinaryFileDetector,
    TokenizerModel,
    OutputFormat,
)

__all__ = [
    "ContextGenerator",
    "Config",
    "FileInfo",
    "ScanResult",
    "BinaryFileDetector",
    "TokenizerModel",
    "OutputFormat",
]
