"""Token counting functionality using Anthropic API"""

import os
import sys
from pathlib import Path
from typing import Optional

import anthropic

from .models import get_full_model_name

class TokenCounter:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize token counter with Anthropic client"""
        api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        self.client = anthropic.Anthropic(api_key=api_key)
    
    def count_tokens(self, content: str, model: str) -> int:
        """Count tokens for given content and model"""
        full_model = get_full_model_name(model)
        
        try:
            response = self.client.messages.count_tokens(
                model=full_model,
                messages=[{
                    "role": "user",
                    "content": [{"type": "text", "text": content}]
                }]
            )
            return response.input_tokens
        except Exception as e:
            raise RuntimeError(f"Failed to count tokens: {e}")

def read_from_stdin() -> str:
    """Read text content from stdin"""
    if sys.stdin.isatty():
        return ""
    return sys.stdin.read().strip()

def read_from_file(file_path: str) -> str:
    """Read text content from file"""
    path = Path(file_path).expanduser().resolve()
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if not path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        raise ValueError(f"File is not valid UTF-8: {file_path}")

def get_content(file_path: Optional[str] = None) -> str:
    """Get content from file or stdin"""
    if file_path:
        return read_from_file(file_path)
    else:
        return read_from_stdin()