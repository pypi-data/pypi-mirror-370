"""Models management for ATC"""

MODEL_MAPPINGS = {
    "opus": "claude-3-opus-20240229",
    "opus-3": "claude-3-opus-20240229",
    "sonnet": "claude-3-5-sonnet-20241022",
    "sonnet-3.5": "claude-3-5-sonnet-20241022",
    "haiku": "claude-3-5-haiku-20241022",
    "haiku-3.5": "claude-3-5-haiku-20241022",
}

PRIMARY_MODELS = ["opus", "sonnet", "haiku"]

DEFAULT_MODEL = "opus"

def get_full_model_name(short_name):
    """Convert short model name to full model ID"""
    return MODEL_MAPPINGS.get(short_name.lower(), short_name)

def get_short_name(full_name):
    """Convert full model ID to short name (returns first match)"""
    for short, full in MODEL_MAPPINGS.items():
        if full == full_name:
            return short
    return full_name

def list_models(verbose=False):
    """List available models"""
    if verbose:
        return sorted(list(set(MODEL_MAPPINGS.values())))
    else:
        return PRIMARY_MODELS

def is_valid_model(model_name):
    """Check if model name is valid (short or full)"""
    if model_name in MODEL_MAPPINGS:
        return True
    if model_name in MODEL_MAPPINGS.values():
        return True
    return False