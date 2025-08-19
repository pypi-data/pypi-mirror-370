"""CLI interface for ATC - Anthropic Tokens Counter"""

import argparse
import sys
from typing import Optional

from . import __version__
from .config import get_default_model, set_default_model
from .models import list_models, is_valid_model, get_full_model_name, get_short_name
from .token_counter import TokenCounter, get_content

def cmd_models(args):
    """Handle models subcommand"""
    if hasattr(args, 'models_command') and args.models_command == 'set-default':
        model = args.model
        if not is_valid_model(model):
            print(f"Error: Invalid model '{model}'", file=sys.stderr)
            return 1
        
        full_model = set_default_model(model)
        print(f"default model is now {full_model}")
        return 0
    
    default_model = get_default_model()
    default_full = get_full_model_name(default_model)
    
    models = list_models(verbose=args.verbose)
    
    for model in sorted(models):
        if args.verbose:
            is_default = model == default_full
            suffix = " (default)" if is_default else ""
            print(f"- {model}{suffix}")
        else:
            is_default = model == default_model
            suffix = " (default)" if is_default else ""
            print(f"- {model}{suffix}")
    
    return 0

def cmd_count(args):
    """Handle token counting (default command)"""
    try:
        content = get_content(args.file_path)
        if not content:
            print("Error: No content provided", file=sys.stderr)
            return 1
        
        model = args.model if args.model else get_default_model()
        if not is_valid_model(model):
            print(f"Error: Invalid model '{model}'", file=sys.stderr)
            return 1
        
        counter = TokenCounter()
        token_count = counter.count_tokens(content, model)
        print(token_count)
        return 0
        
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


def main():
    """Main entry point"""
    # Handle the special case where first argument is 'models'
    if len(sys.argv) > 1 and sys.argv[1] == 'models':
        parser = create_models_parser()
        # Remove 'models' from args before parsing
        args = parser.parse_args(sys.argv[2:])
        return cmd_models(args)
    else:
        # Default token counting behavior
        parser = create_count_parser()
        args = parser.parse_args()
        return cmd_count(args)

def create_models_parser():
    """Create parser for models subcommand"""
    parser = argparse.ArgumentParser(
        prog='atc models',
        description='Manage models for ATC',
    )
    parser.add_argument('-v', '--verbose', action='store_true', 
                       help='Show full model names')
    
    subparsers = parser.add_subparsers(dest='models_command', required=False)
    set_default_parser = subparsers.add_parser('set-default', help='Set default model')
    set_default_parser.add_argument('model', help='Model to set as default')
    
    return parser

def create_count_parser():
    """Create parser for token counting (default behavior)"""
    parser = argparse.ArgumentParser(
        prog='atc',
        description='ATC - Anthropic Tokens Counter',
    )
    parser.add_argument('--version', action='version', version=f'atc {__version__}')
    parser.add_argument('-m', '--model', help='Model to use for token counting')
    parser.add_argument('file_path', nargs='?', 
                       help='Path to file (if not provided, reads from stdin)')
    
    return parser

if __name__ == '__main__':
    sys.exit(main())