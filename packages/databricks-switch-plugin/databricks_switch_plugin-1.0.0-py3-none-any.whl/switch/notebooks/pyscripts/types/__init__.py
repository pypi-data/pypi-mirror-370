"""Type definitions for Switch conversion system."""
from .comment_language import CommentLanguage, MessageKey
from .log_level import LogLevel
from .builtin_prompt import BuiltinPrompt, PromptCategory
from .source_format import SourceFormat
from .target_type import TargetType

__all__ = [
    "CommentLanguage",
    "LogLevel",
    "MessageKey",
    "BuiltinPrompt",
    "SourceFormat",
    "TargetType",
    "PromptCategory",
]