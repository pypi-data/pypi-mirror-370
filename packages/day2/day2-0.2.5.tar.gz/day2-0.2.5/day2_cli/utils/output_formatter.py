"""Output formatters for the MontyCloud DAY2 CLI."""

import json
from typing import Any, Dict, List, Optional, Union

from rich.console import Console
from rich.table import Table

from day2.client.config import Config

console = Console()


def get_output_format(format_override: Optional[str] = None) -> str:
    """Get the output format to use.

    Args:
        format_override: Format to use, overriding config if provided

    Returns:
        Output format to use (table or json)
    """
    if format_override:
        return format_override.lower()

    # Load from config
    config = Config.from_file()
    return config.output_format.lower()


def format_list_output(
    items: List[Dict[str, Any]],
    title: str,
    columns: Dict[str, str],
    format_override: Optional[str] = None,
) -> None:
    """Format and output a list of items.

    Args:
        items: List of items to output
        title: Title for the output
        columns: Dictionary mapping column keys to display names
        format_override: Format to use, overriding config if provided
    """
    output_format = get_output_format(format_override)

    if output_format == "json":
        # Output as JSON
        console.print(json.dumps(items, indent=2, default=str))
    else:
        # Output as table
        table = Table(title=title)

        # Define column styles
        styles = ["cyan", "green", "blue", "magenta", "yellow"]

        # Add columns with styles
        for i, (_, column_name) in enumerate(columns.items()):
            style = styles[i % len(styles)]
            table.add_column(column_name, style=style)

        # Add rows
        for item in items:
            row = []
            for column_key in columns.keys():
                value = item.get(column_key, "")
                row.append(str(value) if value is not None else "N/A")
            table.add_row(*row)

        console.print(table)


def format_item_output(
    item: Dict[str, Any],
    title: str,
    format_override: Optional[str] = None,
) -> None:
    """Format and output a single item.

    Args:
        item: Item to output
        title: Title for the output
        format_override: Format to use, overriding config if provided
    """
    output_format = get_output_format(format_override)

    if output_format == "json":
        # Output as JSON
        console.print(json.dumps(item, indent=2, default=str))
    else:
        # Output as table
        table = Table(title=title)
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")

        for key, value in item.items():
            if isinstance(value, (dict, list)):
                # Convert complex values to JSON string
                value = json.dumps(value, default=str)
            elif value is None:
                value = "N/A"
            else:
                value = str(value)

            table.add_row(key, value)

        console.print(table)


def format_simple_output(
    message: str,
    data: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None,
    format_override: Optional[str] = None,
) -> None:
    """Format and output a simple message, optionally with data.

    Args:
        message: Message to output
        data: Optional data to include in JSON output
        format_override: Format to use, overriding config if provided
    """
    output_format = get_output_format(format_override)

    if output_format == "json":
        # Output as JSON
        if data:
            result = {"message": message, "data": data}
            console.print(json.dumps(result, indent=2, default=str))
        else:
            console.print(json.dumps({"message": message}, indent=2))
    else:
        # Output as text
        console.print(message)
