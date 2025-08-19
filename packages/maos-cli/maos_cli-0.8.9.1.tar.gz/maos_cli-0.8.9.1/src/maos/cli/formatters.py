"""
MAOS CLI Output Formatters

Formatting utilities for consistent CLI output across different
formats including tables, JSON, YAML, and custom rich formatting.
"""

import json
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

import yaml
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree
from rich.json import JSON
from rich.syntax import Syntax
from rich.text import Text
from rich.columns import Columns
from rich import box

console = Console()


class OutputFormatter(ABC):
    """Abstract base class for output formatters."""
    
    @abstractmethod
    def format_dict(self, data: Dict[str, Any], title: Optional[str] = None) -> Any:
        """Format a dictionary for display."""
        pass
    
    @abstractmethod
    def format_list(self, data: List[Dict[str, Any]], title: Optional[str] = None) -> Any:
        """Format a list of dictionaries for display."""
        pass
    
    @staticmethod
    def create(format_type: str) -> "OutputFormatter":
        """Factory method to create formatter instances."""
        formatters = {
            "table": TableFormatter,
            "json": JSONFormatter,
            "yaml": YAMLFormatter,
            "tree": TreeFormatter,
            "compact": CompactFormatter
        }
        
        formatter_class = formatters.get(format_type.lower(), TableFormatter)
        return formatter_class()


class TableFormatter(OutputFormatter):
    """Rich table formatter for structured data display."""
    
    def format_dict(self, data: Dict[str, Any], title: Optional[str] = None) -> Panel:
        """Format dictionary as a two-column table."""
        table = self._create_dict_table(data)
        
        if title:
            return Panel(table, title=title, border_style="blue")
        return table
    
    def format_list(self, data: List[Dict[str, Any]], title: Optional[str] = None) -> Union[Panel, Table]:
        """Format list of dictionaries as a multi-column table."""
        if not data:
            empty_panel = Panel("[dim]No data available[/dim]", title=title or "Empty", border_style="dim")
            return empty_panel
        
        table = self._create_table(data, title)
        
        if title:
            return Panel(table, title=title, border_style="blue")
        return table
    
    def _create_dict_table(self, data: Dict[str, Any]) -> Table:
        """Create a table from a dictionary."""
        table = Table(show_header=True, header_style="bold blue", box=box.ROUNDED)
        table.add_column("Property", style="cyan", width=25)
        table.add_column("Value", style="green")
        
        for key, value in data.items():
            formatted_key = key.replace('_', ' ').title()
            formatted_value = self._format_value(value)
            table.add_row(formatted_key, formatted_value)
        
        return table
    
    def _create_table(self, data: List[Dict[str, Any]], title: Optional[str] = None) -> Table:
        """Create a table from a list of dictionaries."""
        if not data:
            return Table(title=title or "Empty")
        
        # Determine columns from first item
        columns = list(data[0].keys())
        
        table = Table(show_header=True, header_style="bold blue", box=box.ROUNDED)
        
        # Add columns with appropriate styling
        for col in columns:
            formatted_col = col.replace('_', ' ').title()
            style = self._get_column_style(col)
            table.add_column(formatted_col, style=style)
        
        # Add rows
        for row in data:
            formatted_row = [self._format_value(row.get(col, "")) for col in columns]
            table.add_row(*formatted_row)
        
        return table
    
    def _format_value(self, value: Any) -> str:
        """Format a value for table display."""
        if value is None:
            return "[dim]None[/dim]"
        elif isinstance(value, bool):
            return "[green]True[/green]" if value else "[red]False[/red]"
        elif isinstance(value, (list, set)):
            if len(value) == 0:
                return "[dim]Empty[/dim]"
            elif len(value) <= 3:
                return ", ".join(str(v) for v in value)
            else:
                return f"{', '.join(str(v) for v in list(value)[:3])}..."
        elif isinstance(value, dict):
            if len(value) == 0:
                return "[dim]Empty[/dim]"
            return f"{len(value)} items"
        elif isinstance(value, datetime):
            return value.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(value, str) and len(value) > 50:
            return value[:47] + "..."
        else:
            return str(value)
    
    def _get_column_style(self, column_name: str) -> str:
        """Get appropriate style for column based on name."""
        if "id" in column_name.lower():
            return "cyan"
        elif "status" in column_name.lower():
            return "yellow"
        elif "name" in column_name.lower() or "type" in column_name.lower():
            return "green"
        elif "time" in column_name.lower() or "date" in column_name.lower():
            return "blue"
        elif "error" in column_name.lower():
            return "red"
        else:
            return "white"


class JSONFormatter(OutputFormatter):
    """JSON formatter with syntax highlighting."""
    
    def format_dict(self, data: Dict[str, Any], title: Optional[str] = None) -> Union[Panel, JSON]:
        """Format dictionary as JSON."""
        json_str = json.dumps(data, indent=2, default=self._json_serializer)
        json_display = JSON(json_str)
        
        if title:
            return Panel(json_display, title=title, border_style="green")
        return json_display
    
    def format_list(self, data: List[Dict[str, Any]], title: Optional[str] = None) -> Union[Panel, JSON]:
        """Format list as JSON."""
        json_str = json.dumps(data, indent=2, default=self._json_serializer)
        json_display = JSON(json_str)
        
        if title:
            return Panel(json_display, title=title, border_style="green")
        return json_display
    
    def _json_serializer(self, obj: Any) -> Any:
        """Custom JSON serializer for complex objects."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, set):
            return list(obj)
        else:
            return str(obj)


class YAMLFormatter(OutputFormatter):
    """YAML formatter with syntax highlighting."""
    
    def format_dict(self, data: Dict[str, Any], title: Optional[str] = None) -> Union[Panel, Syntax]:
        """Format dictionary as YAML."""
        yaml_str = yaml.dump(data, default_flow_style=False, indent=2)
        yaml_display = Syntax(yaml_str, "yaml", theme="monokai", line_numbers=True)
        
        if title:
            return Panel(yaml_display, title=title, border_style="magenta")
        return yaml_display
    
    def format_list(self, data: List[Dict[str, Any]], title: Optional[str] = None) -> Union[Panel, Syntax]:
        """Format list as YAML."""
        yaml_str = yaml.dump(data, default_flow_style=False, indent=2)
        yaml_display = Syntax(yaml_str, "yaml", theme="monokai", line_numbers=True)
        
        if title:
            return Panel(yaml_display, title=title, border_style="magenta")
        return yaml_display


class TreeFormatter(OutputFormatter):
    """Tree formatter for hierarchical data display."""
    
    def format_dict(self, data: Dict[str, Any], title: Optional[str] = None) -> Union[Panel, Tree]:
        """Format dictionary as a tree structure."""
        tree = Tree(title or "Data")
        self._add_dict_to_tree(tree, data)
        
        if title and title != "Data":
            return Panel(tree, title=title, border_style="cyan")
        return tree
    
    def format_list(self, data: List[Dict[str, Any]], title: Optional[str] = None) -> Union[Panel, Tree]:
        """Format list as a tree structure."""
        tree = Tree(title or "Data")
        
        for i, item in enumerate(data):
            if isinstance(item, dict):
                item_node = tree.add(f"Item {i + 1}")
                self._add_dict_to_tree(item_node, item)
            else:
                tree.add(str(item))
        
        if title and title != "Data":
            return Panel(tree, title=title, border_style="cyan")
        return tree
    
    def _add_dict_to_tree(self, parent_node: Tree, data: Dict[str, Any]):
        """Recursively add dictionary items to tree."""
        for key, value in data.items():
            if isinstance(value, dict):
                child_node = parent_node.add(f"[bold blue]{key}[/bold blue]")
                self._add_dict_to_tree(child_node, value)
            elif isinstance(value, list):
                child_node = parent_node.add(f"[bold blue]{key}[/bold blue] ({len(value)} items)")
                for i, item in enumerate(value[:10]):  # Limit to first 10 items
                    if isinstance(item, dict):
                        item_node = child_node.add(f"Item {i + 1}")
                        self._add_dict_to_tree(item_node, item)
                    else:
                        child_node.add(str(item))
                if len(value) > 10:
                    child_node.add(f"[dim]...and {len(value) - 10} more items[/dim]")
            else:
                formatted_value = self._format_tree_value(value)
                parent_node.add(f"[blue]{key}[/blue]: {formatted_value}")
    
    def _format_tree_value(self, value: Any) -> str:
        """Format value for tree display."""
        if value is None:
            return "[dim]None[/dim]"
        elif isinstance(value, bool):
            return "[green]True[/green]" if value else "[red]False[/red]"
        elif isinstance(value, str) and len(value) > 50:
            return f"[yellow]{value[:47]}...[/yellow]"
        elif isinstance(value, datetime):
            return f"[cyan]{value.strftime('%Y-%m-%d %H:%M:%S')}[/cyan]"
        else:
            return f"[white]{value}[/white]"


class CompactFormatter(OutputFormatter):
    """Compact formatter for minimal display."""
    
    def format_dict(self, data: Dict[str, Any], title: Optional[str] = None) -> Union[Panel, Text]:
        """Format dictionary in compact form."""
        lines = []
        for key, value in data.items():
            formatted_value = self._compact_value(value)
            lines.append(f"[cyan]{key}[/cyan]: {formatted_value}")
        
        content = Text("\n".join(lines))
        
        if title:
            return Panel(content, title=title, border_style="dim")
        return content
    
    def format_list(self, data: List[Dict[str, Any]], title: Optional[str] = None) -> Union[Panel, Columns]:
        """Format list in compact columns."""
        if not data:
            empty_text = Text("No data available", style="dim")
            return Panel(empty_text, title=title or "Empty", border_style="dim")
        
        panels = []
        for i, item in enumerate(data[:20]):  # Limit to 20 items
            if isinstance(item, dict):
                lines = []
                for key, value in list(item.items())[:5]:  # Show first 5 fields
                    formatted_value = self._compact_value(value)
                    lines.append(f"[dim]{key}:[/dim] {formatted_value}")
                
                if len(item) > 5:
                    lines.append(f"[dim]...and {len(item) - 5} more[/dim]")
                
                content = Text("\n".join(lines))
                panels.append(Panel(content, title=f"#{i+1}", border_style="dim", width=30))
        
        if len(data) > 20:
            more_panel = Panel(
                f"[dim]...and {len(data) - 20} more items[/dim]",
                title="More",
                border_style="dim",
                width=30
            )
            panels.append(more_panel)
        
        columns = Columns(panels, equal=False, expand=True)
        
        if title:
            return Panel(columns, title=title, border_style="dim")
        return columns
    
    def _compact_value(self, value: Any) -> str:
        """Format value in compact form."""
        if value is None:
            return "[dim]None[/dim]"
        elif isinstance(value, bool):
            return "[green]✓[/green]" if value else "[red]✗[/red]"
        elif isinstance(value, (list, set)):
            return f"[yellow]{len(value)} items[/yellow]"
        elif isinstance(value, dict):
            return f"[yellow]{len(value)} fields[/yellow]"
        elif isinstance(value, str) and len(value) > 30:
            return f"[white]{value[:27]}...[/white]"
        elif isinstance(value, datetime):
            return f"[blue]{value.strftime('%m/%d %H:%M')}[/blue]"
        else:
            return f"[white]{value}[/white]"


# Utility functions for custom formatting

def format_duration(seconds: float) -> str:
    """Format duration in human-readable format."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        return f"{seconds/60:.1f}m"
    elif seconds < 86400:
        return f"{seconds/3600:.1f}h"
    else:
        return f"{seconds/86400:.1f}d"


def format_size(bytes_value: int) -> str:
    """Format byte size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f}{unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f}PB"


def format_percentage(value: float, total: float) -> str:
    """Format percentage with color coding."""
    if total == 0:
        return "[dim]N/A[/dim]"
    
    percentage = (value / total) * 100
    
    if percentage >= 90:
        return f"[red]{percentage:.1f}%[/red]"
    elif percentage >= 70:
        return f"[yellow]{percentage:.1f}%[/yellow]"
    else:
        return f"[green]{percentage:.1f}%[/green]"


def format_status(status: str) -> str:
    """Format status with appropriate color."""
    status_colors = {
        'running': 'green',
        'completed': 'blue',
        'failed': 'red',
        'cancelled': 'yellow',
        'pending': 'dim',
        'error': 'red',
        'healthy': 'green',
        'unhealthy': 'red',
        'available': 'green',
        'busy': 'yellow',
        'idle': 'dim'
    }
    
    color = status_colors.get(status.lower(), 'white')
    return f"[{color}]{status}[/{color}]"


def create_progress_bar(current: int, total: int, width: int = 20) -> str:
    """Create a simple progress bar."""
    if total == 0:
        return "[dim]N/A[/dim]"
    
    percentage = current / total
    filled = int(width * percentage)
    bar = "█" * filled + "░" * (width - filled)
    
    if percentage >= 1.0:
        return f"[green]{bar}[/green] 100%"
    elif percentage >= 0.7:
        return f"[yellow]{bar}[/yellow] {percentage*100:.1f}%"
    else:
        return f"[blue]{bar}[/blue] {percentage*100:.1f}%"


def format_timestamp(timestamp: datetime, relative: bool = True) -> str:
    """Format timestamp with optional relative time."""
    absolute = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    
    if not relative:
        return f"[blue]{absolute}[/blue]"
    
    now = datetime.utcnow()
    diff = now - timestamp
    
    if diff.total_seconds() < 60:
        return f"[green]Just now[/green] ({absolute})"
    elif diff.total_seconds() < 3600:
        minutes = int(diff.total_seconds() / 60)
        return f"[yellow]{minutes}m ago[/yellow] ({absolute})"
    elif diff.total_seconds() < 86400:
        hours = int(diff.total_seconds() / 3600)
        return f"[blue]{hours}h ago[/blue] ({absolute})"
    else:
        days = int(diff.total_seconds() / 86400)
        return f"[dim]{days}d ago[/dim] ({absolute})"


def create_summary_panel(data: Dict[str, Any], title: str = "Summary") -> Panel:
    """Create a summary panel with key metrics."""
    summary_text = []
    
    for key, value in data.items():
        formatted_key = key.replace('_', ' ').title()
        
        if isinstance(value, (int, float)):
            if key.endswith('_count') or key.startswith('total_'):
                summary_text.append(f"[cyan]{formatted_key}:[/cyan] [bold white]{value:,}[/bold white]")
            else:
                summary_text.append(f"[cyan]{formatted_key}:[/cyan] [white]{value}[/white]")
        elif isinstance(value, str):
            summary_text.append(f"[cyan]{formatted_key}:[/cyan] [green]{value}[/green]")
        else:
            summary_text.append(f"[cyan]{formatted_key}:[/cyan] [white]{value}[/white]")
    
    content = Text("\n".join(summary_text))
    return Panel(content, title=title, border_style="blue", padding=(1, 2))