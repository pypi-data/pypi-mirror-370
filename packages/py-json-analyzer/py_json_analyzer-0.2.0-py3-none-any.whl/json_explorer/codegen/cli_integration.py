"""
CLI integration for code generation functionality.

Provides command-line interface for the codegen module.
"""

import argparse
import sys
import json
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich import box

from . import (
    generate_from_analysis,
    list_supported_languages,
    get_generator,
    get_language_info,
    list_all_language_info,
    GeneratorConfig,
    load_config,
    GeneratorError,
)
from json_explorer.analyzer import analyze_json
from json_explorer.utils import load_json


class CLIError(Exception):
    """Exception raised for CLI-related errors."""

    pass


# Initialize rich console
console = Console()


def add_codegen_args(parser: argparse.ArgumentParser):
    """Add code generation arguments to existing CLI parser."""

    # Create codegen subparser group
    codegen_group = parser.add_argument_group("code generation")

    codegen_group.add_argument(
        "--generate",
        "-g",
        metavar="LANGUAGE",
        help="Generate code in specified language (use --list-languages to see options)",
    )

    codegen_group.add_argument(
        "--output",
        "-o",
        metavar="FILE",
        help="Output file for generated code (default: stdout)",
    )

    codegen_group.add_argument(
        "--config", metavar="FILE", help="JSON configuration file for code generation"
    )

    codegen_group.add_argument(
        "--package-name",
        metavar="NAME",
        help="Package/namespace name for generated code",
    )

    codegen_group.add_argument(
        "--root-name",
        metavar="NAME",
        default="Root",
        help="Name for the root data structure (default: Root)",
    )

    codegen_group.add_argument(
        "--list-languages",
        action="store_true",
        help="List supported target languages and exit",
    )

    codegen_group.add_argument(
        "--language-info",
        metavar="LANGUAGE",
        help="Show detailed information about a specific language",
    )

    # Common generation options
    common_group = parser.add_argument_group("common generation options")
    common_group.add_argument(
        "--no-comments",
        action="store_true",
        help="Don't generate comments in output code",
    )

    common_group.add_argument(
        "--struct-case",
        choices=["pascal", "camel", "snake"],
        help="Case style for struct/class names",
    )

    common_group.add_argument(
        "--field-case",
        choices=["pascal", "camel", "snake"],
        help="Case style for field names",
    )

    common_group.add_argument(
        "--verbose", action="store_true", help="Show generation result metadata"
    )

    # Go-specific options
    go_group = parser.add_argument_group("Go-specific options")
    go_group.add_argument(
        "--no-pointers",
        action="store_true",
        help="Don't use pointers for optional fields in Go",
    )

    go_group.add_argument(
        "--no-json-tags",
        action="store_true",
        help="Don't generate JSON struct tags in Go",
    )

    go_group.add_argument(
        "--no-omitempty",
        action="store_true",
        help="Don't add omitempty to JSON tags in Go",
    )

    go_group.add_argument(
        "--json-tag-case",
        choices=["original", "snake", "camel"],
        help="Case style for JSON tag names in Go",
    )


def handle_codegen_command(args: argparse.Namespace, json_data=None) -> int:
    """
    Handle code generation command from CLI arguments.

    Args:
        args: Parsed command line arguments
        json_data: Optional pre-loaded JSON data

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        # Handle informational commands first
        if hasattr(args, "list_languages") and args.list_languages:
            return _list_languages()

        if hasattr(args, "language_info") and args.language_info:
            return _show_language_info(args.language_info)

        # Check if generation was requested
        if not hasattr(args, "generate") or not args.generate:
            return 0  # No generation requested

        # Validate language
        language = args.generate.lower()
        if not _validate_language(language):
            return 1

        # Get input data if not provided
        if json_data is None:
            json_data = _get_input_data(args)
            if json_data is None:
                return 1

        # Build configuration
        config = _build_config(args, language)

        # Generate code
        return _generate_and_output(json_data, language, config, args)

    except CLIError as e:
        console.print(f"[red]❌ Error:[/red] {e}")
        return 1
    except Exception as e:
        console.print(f"[red]❌ Unexpected error:[/red] {e}")
        return 1


def _list_languages() -> int:
    """List supported languages with details."""
    try:
        language_info = list_all_language_info()

        if not language_info:
            console.print("[yellow]⚠️ No code generators available[/yellow]")
            return 0

        # Create a rich table
        table = Table(
            title="📋 Supported Languages", box=box.ROUNDED, title_style="bold cyan"
        )

        table.add_column("Language", style="bold green", no_wrap=True)
        table.add_column("Extension", style="cyan")
        table.add_column("Generator Class", style="dim")
        table.add_column("Aliases", style="gold1 ")

        for lang_name, info in sorted(language_info.items()):
            aliases = (
                ", ".join(info["aliases"]) if info["aliases"] else "[dim]none[/dim]"
            )

            table.add_row(
                f"🔧 {lang_name}", info["file_extension"], info["class"], aliases
            )

        console.print()
        console.print(table)
        console.print()

        # Add usage hint
        console.print(
            Panel(
                "[bold]Usage:[/bold] json_explorer [dim]input.json[/dim] --generate [cyan]LANGUAGE[/cyan]\n"
                "[bold]Info:[/bold] json_explorer --language-info [cyan]LANGUAGE[/cyan]",
                title="💡 Quick Start",
                border_style="blue",
            )
        )

        return 0

    except Exception as e:
        console.print(f"[red]❌ Error listing languages:[/red] {e}")
        return 1


def _show_language_info(language: str) -> int:
    """Show detailed information about a specific language."""
    try:
        if not _validate_language(language, silent=True):
            console.print(f"[red]❌ Language '{language}' is not supported[/red]")
            console.print("[dim]Use --list-languages to see available options[/dim]")
            return 1

        info = get_language_info(language)

        # Create main info panel
        info_text = f"""[bold]Language:[/bold] {info['name']}
[bold]File Extension:[/bold] {info['file_extension']}
[bold]Generator Class:[/bold] {info['class']}
[bold]Module:[/bold] {info['module']}"""

        if info["aliases"]:
            info_text += f"\n[bold]Aliases:[/bold] {', '.join(info['aliases'])}"

        console.print()
        console.print(
            Panel(
                info_text,
                title=f"🔧 {info['name'].title()} Generator",
                border_style="green",
            )
        )

        # Try to get configuration details
        try:
            generator = get_generator(language)

            # Create configuration table
            config_table = Table(
                title="⚙️ Default Configuration",
                box=box.SIMPLE,
                show_header=True,
                header_style="bold cyan",
            )

            config_table.add_column("Setting", style="bold")
            config_table.add_column("Value", style="green")

            config_table.add_row("Package Name", str(generator.config.package_name))
            config_table.add_row("Indent Size", str(generator.config.indent_size))
            config_table.add_row(
                "Generate JSON Tags", str(generator.config.generate_json_tags)
            )
            config_table.add_row("Add Comments", str(generator.config.add_comments))
            config_table.add_row(
                "JSON Tag Omitempty", str(generator.config.json_tag_omitempty)
            )

            console.print()
            console.print(config_table)

        except Exception:
            console.print(
                "\n[yellow]⚠️  Could not retrieve configuration details[/yellow]"
            )

        # Add examples panel
        examples_text = f"""Generate basic structure:
[cyan]json_explorer data.json --generate {language}[/cyan]

Generate to file:
[cyan]json_explorer data.json --generate {language} --output output{info['file_extension']}[/cyan]

Custom package name:
[cyan]json_explorer data.json --generate {language} --package-name mypackage[/cyan]"""

        console.print()
        console.print(
            Panel(examples_text, title="💡 Usage Examples", border_style="blue")
        )

        return 0

    except Exception as e:
        console.print(f"[red]❌ Error getting language info:[/red] {e}")
        return 1


def _validate_language(language: str, silent: bool = False) -> bool:
    """Validate that a language is supported."""
    try:
        supported = list_supported_languages()
        if language.lower() not in [lang.lower() for lang in supported]:
            if not silent:
                console.print(f"[red]❌ Unsupported language '{language}'[/red]")
                console.print(f"[dim]Supported languages: {', '.join(supported)}[/dim]")
            return False
        return True
    except Exception:
        if not silent:
            console.print("[red]❌ Failed to validate language[/red]")
        return False


def _get_input_data(args: argparse.Namespace):
    """Get JSON input data from various sources."""
    try:
        if hasattr(args, "file") and args.file:
            return load_json(args.file)[1]
        elif hasattr(args, "url") and args.url:
            return load_json(args.url)[1]
        else:
            # Try to read from stdin
            return json.load(sys.stdin)
    except json.JSONDecodeError as e:
        console.print(f"[red]❌ Invalid JSON input:[/red] {e}")
        return None
    except Exception as e:
        console.print(f"[red]❌ Failed to load input:[/red] {e}")
        return None


def _build_config(args: argparse.Namespace, language: str) -> GeneratorConfig:
    """Build configuration from CLI arguments."""
    config_dict = {}

    # Load from config file if provided
    if hasattr(args, "config") and args.config:
        try:
            config_dict = _load_config_file(args.config)
        except Exception as e:
            raise CLIError(f"Configuration error: {e}")

    # Override with CLI arguments
    if hasattr(args, "package_name") and args.package_name:
        config_dict["package_name"] = args.package_name

    if hasattr(args, "no_comments") and args.no_comments:
        config_dict["add_comments"] = False

    if hasattr(args, "struct_case") and args.struct_case:
        config_dict["struct_case"] = args.struct_case

    if hasattr(args, "field_case") and args.field_case:
        config_dict["field_case"] = args.field_case

    # Language-specific options
    if language.lower() == "go":
        if hasattr(args, "no_pointers") and args.no_pointers:
            config_dict["use_pointers_for_optional"] = False

        if hasattr(args, "no_json_tags") and args.no_json_tags:
            config_dict["generate_json_tags"] = False

        if hasattr(args, "no_omitempty") and args.no_omitempty:
            config_dict["json_tag_omitempty"] = False

        if hasattr(args, "json_tag_case") and args.json_tag_case:
            config_dict["json_tag_case"] = args.json_tag_case

    return load_config(custom_config=config_dict)


def _load_config_file(config_path: str) -> dict:
    """Load configuration from JSON file."""
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        if not isinstance(config, dict):
            raise CLIError(f"Configuration file must contain a JSON object")

        return config
    except json.JSONDecodeError as e:
        raise CLIError(f"Invalid JSON in configuration file: {e}")
    except IOError as e:
        raise CLIError(f"Failed to read configuration file: {e}")


def _generate_and_output(
    json_data, language: str, config: GeneratorConfig, args: argparse.Namespace
) -> int:
    """Generate code and handle output with rich formatting."""
    try:

        analysis = analyze_json(json_data)

        root_name = getattr(args, "root_name", "Root")
        result = generate_from_analysis(analysis, language, config, root_name)

        if not result.success:
            console.print(
                f"[red]❌ Code generation failed:[/red] {result.error_message}"
            )
            if hasattr(result, "exception") and result.exception:
                console.print(f"[dim]Details: {result.exception}[/dim]")
            return 1

        # Output code
        output_file = getattr(args, "output", None)
        if output_file:
            try:
                output_path = Path(output_file)
                output_path.write_text(result.code, encoding="utf-8")
                console.print(
                    f"[green]✓[/green] Generated {language} code saved to [cyan]{output_path}[/cyan]"
                )
            except IOError as e:
                console.print(f"[red]❌ Failed to write to {output_path}:[/red] {e}")
                return 1
        else:
            # Display to stdout with rich formatting
            _display_generated_code(result.code, language)

        # Show warnings if any
        if result.warnings:
            console.print("\n[yellow]⚠️ Warnings:[/yellow]")
            for warning in result.warnings:
                console.print(f"  [yellow]•[/yellow] {warning}")

        # Show metadata if verbose
        if hasattr(args, "verbose") and args.verbose and result.metadata:
            _display_metadata(result.metadata)

        return 0

    except GeneratorError as e:
        console.print(f"[red]❌[/red] {e}")
        return 1
    except Exception as e:
        console.print(f"[red]❌ Unexpected failure:[/red] {e}")
        return 1


def _display_generated_code(code: str, language: str):
    """Display generated code with syntax highlighting."""

    console.print(f"\n[green]📄 Generated {language.title()} Code\n[/green]")

    try:
        # Map language names for syntax highlighting
        syntax_lang = language.lower()
        if syntax_lang == "golang":
            syntax_lang = "go"

        syntax = Syntax(code, syntax_lang, theme="monokai", padding=1)
        console.print(syntax)
    except Exception:
        # Fallback to plain text if syntax highlighting fails
        console.print(code)


def _display_metadata(metadata: dict):
    """Display generation metadata in a formatted table."""
    metadata_table = Table(
        title="📊 Generation Metadata",
        box=box.SIMPLE,
        show_header=True,
        header_style="bold cyan",
    )

    metadata_table.add_column("Property", style="bold")
    metadata_table.add_column("Value", style="green")

    for key, value in metadata.items():
        display_key = key.replace("_", " ").title()
        metadata_table.add_row(display_key, str(value))

    console.print()
    console.print(metadata_table)


# Utility functions for testing and development
def validate_cli_config(args: argparse.Namespace) -> bool:
    """
    Validate CLI configuration for development/testing.

    Args:
        args: Parsed CLI arguments

    Returns:
        True if configuration is valid
    """
    try:
        if hasattr(args, "generate") and args.generate:
            # Check language support
            if not _validate_language(args.generate, silent=True):
                return False

            # Try to build config
            config = _build_config(args, args.generate)

            # Try to create generator
            generator = get_generator(args.generate, config)

            return True
    except Exception:
        return False

    return True
