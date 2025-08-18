#!/usr/bin/env python3
"""
Command Line Interface for the Limerick Generator

Usage examples:
    limerick cats
    limerick "quantum physics" --model gpt-4
    limerick dating --filth-level 2
    limerick programming --json
    limerick programming -j -m gpt-5
"""

import argparse
import sys
from src.limerick_generator import generate_limerick, SUPPORTED_MODELS


def main():
    """Main CLI entry point for the limerick generator."""
    parser = argparse.ArgumentParser(
        description="Generate limericks about any topic using OpenAI's API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  limerick cats
  limerick "quantum physics" --model gpt-4
  limerick dating --filth-level 2
  limerick programming --json
  limerick programming -j -m gpt-5

Filth levels:
  0: Family friendly (default)
  1: Risque with innuendo
  2: Dirty and sexually charged
  3: Filthy and offensive

Output formats:
  Default: Just the limerick text
  --json/-j: Full OpenAI response as JSON
  --yaml/-y: Full OpenAI response as YAML
        """,
    )

    parser.add_argument("topic", nargs="*", help="The topic or theme for the limerick")

    parser.add_argument(
        "--model",
        "-m",
        choices=SUPPORTED_MODELS,
        default="gpt-3.5-turbo",
        help="OpenAI model to use (default: gpt-3.5-turbo)",
    )

    parser.add_argument(
        "--filth-level",
        "-f",
        type=int,
        choices=[0, 1, 2, 3],
        default=0,
        help="Content filth level 0-3 (default: 0 - family friendly)",
    )

    # Output format flags - mutually exclusive
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument(
        "--json", "-j", action="store_true", help="Output full OpenAI response as JSON"
    )
    output_group.add_argument(
        "--yaml", "-y", action="store_true", help="Output full OpenAI response as YAML"
    )

    parser.add_argument(
        "--api-key",
        help="OpenAI API key (overrides OPENAI_API_KEY environment variable)",
    )

    args = parser.parse_args()

    # Join topic words into a single string
    topic = " ".join(args.topic) if args.topic else ""
    
    if not topic:
        print("Error: Topic is required", file=sys.stderr)
        sys.exit(1)

    # Determine output format based on flags
    if args.json:
        output_format = "json"
    elif args.yaml:
        output_format = "yaml"
    else:
        output_format = "text"

    try:
        # Generate the limerick
        result = generate_limerick(
            topic=topic,
            api_key=args.api_key,
            model=args.model,
            filth_level=args.filth_level,
            output=output_format,
        )

        print(result)

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error generating limerick: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

