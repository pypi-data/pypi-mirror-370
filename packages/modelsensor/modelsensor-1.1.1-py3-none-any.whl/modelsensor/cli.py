"""
Command Line Interface for ModelSensor
"""

import argparse
import sys
from .core import ModelSensor
from .formatters import JSONFormatter, MarkdownFormatter


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="ModelSensor - Let LLM sense the world",
        prog="modelsensor"
    )
    
    parser.add_argument(
        "-f", "--format",
        choices=["json", "markdown", "md", "summary"],
        default="json",
        help="Output format (default: json)"
    )
    
    parser.add_argument(
        "-l", "--location",
        action="store_true",
        help="Include location information (requires internet)"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output file path (default: stdout)"
    )
    
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="JSON indentation level (default: 2)"
    )
    
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Compact JSON output (no indentation)"
    )
    
    parser.add_argument(
        "-v", "--version",
        action="version",
        version="ModelSensor 1.1.1"
    )
    
    args = parser.parse_args()
    
    try:
        # Create sensor instance and collect data
        sensor = ModelSensor()
        data = sensor.collect_all_data(include_location=args.location)
        
        # Format output
        if args.format == "json":
            if args.compact:
                output = JSONFormatter.format_compact(data)
            else:
                output = JSONFormatter.format(data, indent=args.indent)
        elif args.format in ["markdown", "md"]:
            output = MarkdownFormatter.format(data)
        elif args.format == "summary":
            output = MarkdownFormatter.format_summary(data)
        else:
            output = JSONFormatter.format(data, indent=args.indent)
        
        # Write output
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"Output written to {args.output}")
        else:
            print(output)
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main() 