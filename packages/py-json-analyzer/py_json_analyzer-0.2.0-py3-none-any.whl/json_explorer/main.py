#!/usr/bin/env python3

"""
main.py

Entry point for the JSON Explorer CLI tool.

Author: MS-32154
email: msttoffg@gmail.com
Version: 0.2.0
License: MIT
Date: 2025-09-01
"""

import argparse
import sys

from .cli import CLIHandler
from .interactive import InteractiveHandler
from .utils import load_json
from .codegen.cli_integration import add_codegen_args, handle_codegen_command
from rich.console import Console


class JSONExplorer:
    """Main JSON Explorer application coordinator."""

    def __init__(self):
        self.data = None
        self.source = None
        self.console = Console()
        self.cli_handler = CLIHandler()
        self.interactive_handler = InteractiveHandler()

    def load_data(self, file_path=None, url=None):
        """Load JSON data from file or URL."""
        try:
            self.source, self.data = load_json(file_path, url)
            return True
        except Exception as e:
            self.console.print(f"❌ [red]Error loading data: {e}[/red]")
            return False

    def run(self, args):
        """Main execution method."""
        # Handle codegen commands
        if self._is_codegen_command(args):
            # Some codegen commands don't need data (like --list-languages)
            if hasattr(args, "list_languages") and args.list_languages:
                return handle_codegen_command(args, None)

            # Load data for generation commands
            if not self.load_data(args.file, args.url):
                return 1

            return handle_codegen_command(args, self.data)

        # For other operations, load data first
        if not self.load_data(args.file, args.url):
            return 1

        self.cli_handler.set_data(self.data, self.source)
        self.interactive_handler.set_data(self.data, self.source)

        if args.interactive or not self._has_cli_actions(args):
            return self.interactive_handler.run()
        else:
            return self.cli_handler.run(args)

    def _is_codegen_command(self, args) -> bool:
        """Check if this is a code generation command."""
        return (
            (hasattr(args, "generate") and args.generate)
            or (hasattr(args, "list_languages") and args.list_languages)
            or (hasattr(args, "language_info") and args.language_info)
        )

    def _has_cli_actions(self, args) -> bool:
        """Check if any CLI-specific actions are requested."""
        return any([args.tree, args.search, args.stats, args.plot])


def create_parser():
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="🔍 JSON Explorer - Analyze, visualize, and explore JSON data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s data.json --interactive
  %(prog)s data.json --tree compact --stats
  %(prog)s data.json --search "name" --search-type key
  %(prog)s data.json --search "isinstance(value, int) and value > 10" --search-type filter
  %(prog)s --url https://api.example.com/data --plot
  
Code Generation:
  %(prog)s data.json --generate go --output user.go --root-name User
  %(prog)s data.json --generate go --package-name models --no-pointers
  %(prog)s data.json --generate go --config my-config.json
  %(prog)s --list-languages
        """,
    )

    # Data source
    parser.add_argument("file", nargs="?", help="Path to JSON file")
    parser.add_argument("--url", type=str, help="URL to fetch JSON from")

    # Interactive mode
    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Run in interactive mode"
    )

    # Tree operations
    parser.add_argument(
        "--tree",
        choices=["compact", "analysis", "raw"],
        help="Display JSON tree structure",
    )

    # Search operations
    search_group = parser.add_argument_group("search options")
    search_group.add_argument(
        "--search", type=str, help="Search query or filter expression"
    )
    search_group.add_argument(
        "--search-type",
        choices=["key", "value", "pair", "filter"],
        default="key",
        help="Type of search to perform",
    )
    search_group.add_argument(
        "--search-value",
        type=str,
        help="Value to search for (used with --search-type pair)",
    )
    search_group.add_argument(
        "--search-mode",
        type=str,
        choices=[
            "exact",
            "contains",
            "regex",
            "startswith",
            "endswith",
            "case_insensitive",
        ],
        default="exact",
        help="Search mode",
    )
    search_group.add_argument(
        "--tree-results",
        action="store_true",
        help="Display search results in tree format",
    )

    # Analysis options
    analysis_group = parser.add_argument_group("analysis options")
    analysis_group.add_argument("--stats", action="store_true", help="Show statistics")
    analysis_group.add_argument(
        "--detailed", action="store_true", help="Show detailed analysis/statistics"
    )

    # Visualization options
    viz_group = parser.add_argument_group("visualization options")
    viz_group.add_argument(
        "--plot", action="store_true", help="Generate visualizations"
    )
    viz_group.add_argument(
        "--plot-format",
        choices=["terminal", "matplotlib", "browser", "all"],
        default="matplotlib",
        help="Visualization format",
    )
    viz_group.add_argument("--save-path", type=str, help="Path to save visualizations")
    viz_group.add_argument(
        "--no-browser",
        action="store_true",
        help="Don't open browser for HTML visualizations",
    )

    # Add codegen arguments
    add_codegen_args(parser)

    return parser


def main():
    """Main entry point for the JSON Explorer."""
    parser = create_parser()
    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        return 1

    # Handle special commands that don't need file/url
    if hasattr(args, "list_languages") and args.list_languages:
        explorer = JSONExplorer()
        return explorer.run(args)

    if hasattr(args, "language_info") and args.language_info:
        explorer = JSONExplorer()
        return explorer.run(args)

    # For codegen, we need either file or url
    if hasattr(args, "generate") and args.generate:
        if not (args.file or args.url):
            print("❌ Error: Code generation requires a file path or --url")
            parser.print_help()
            return 1

    # For other operations, file or url is required
    if (
        not hasattr(args, "generate")
        and not hasattr(args, "list_languages")
        and not hasattr(args, "language_info")
    ):
        if not (args.file or args.url):
            print("❌ Error: You must provide a file path or --url")
            parser.print_help()
            return 1

    explorer = JSONExplorer()
    return explorer.run(args)


if __name__ == "__main__":
    sys.exit(main())
