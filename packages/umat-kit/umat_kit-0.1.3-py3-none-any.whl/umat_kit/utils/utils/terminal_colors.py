"""
Advanced Terminal Color Management with Rich Styling
Provides comprehensive color and styling utilities for terminal output
"""

import sys
from typing import Optional, Dict, Any, Union
from enum import Enum
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.syntax import Syntax
from rich.json import JSON
from rich.tree import Tree
from colorama import init, Fore, Back, Style

# Initialize colorama for Windows compatibility
init(autoreset=True)

class ColorScheme(Enum):
    """Predefined color schemes for different contexts"""
    SUCCESS = "green"
    ERROR = "red"
    WARNING = "yellow"
    INFO = "blue"
    DEBUG = "magenta"
    HIGHLIGHT = "cyan"
    MUTED = "dim white"

class TerminalColors:
    """Advanced terminal color management using colorama"""

    # Foreground colors
    BLACK = Fore.BLACK
    RED = Fore.RED
    GREEN = Fore.GREEN
    YELLOW = Fore.YELLOW
    BLUE = Fore.BLUE
    MAGENTA = Fore.MAGENTA
    CYAN = Fore.CYAN
    WHITE = Fore.WHITE

    # Background colors
    BG_BLACK = Back.BLACK
    BG_RED = Back.RED
    BG_GREEN = Back.GREEN
    BG_YELLOW = Back.YELLOW
    BG_BLUE = Back.BLUE
    BG_MAGENTA = Back.MAGENTA
    BG_CYAN = Back.CYAN
    BG_WHITE = Back.WHITE

    # Styles
    BRIGHT = Style.BRIGHT
    DIM = Style.DIM
    NORMAL = Style.NORMAL
    RESET = Style.RESET_ALL

    @classmethod
    def colorize(cls, text: str, color: str, bg_color: Optional[str] = None, style: Optional[str] = None) -> str:
        """Apply color and style to text"""
        result = ""

        # Apply foreground color
        if hasattr(cls, color.upper()):
            result += getattr(cls, color.upper())

        # Apply background color
        if bg_color and hasattr(cls, f"BG_{bg_color.upper()}"):
            result += getattr(cls, f"BG_{bg_color.upper()}")

        # Apply style
        if style and hasattr(cls, style.upper()):
            result += getattr(cls, style.upper())

        result += text + cls.RESET
        return result

    @classmethod
    def success(cls, text: str) -> str:
        """Format text as success message"""
        return cls.colorize(text, "GREEN", style="BRIGHT")

    @classmethod
    def error(cls, text: str) -> str:
        """Format text as error message"""
        return cls.colorize(text, "RED", style="BRIGHT")

    @classmethod
    def warning(cls, text: str) -> str:
        """Format text as warning message"""
        return cls.colorize(text, "YELLOW", style="BRIGHT")

    @classmethod
    def info(cls, text: str) -> str:
        """Format text as info message"""
        return cls.colorize(text, "BLUE", style="BRIGHT")

    @classmethod
    def debug(cls, text: str) -> str:
        """Format text as debug message"""
        return cls.colorize(text, "MAGENTA", style="DIM")

    @classmethod
    def highlight(cls, text: str) -> str:
        """Format text as highlighted"""
        return cls.colorize(text, "CYAN", style="BRIGHT")

class ColoredOutput:
    """Advanced output management with Rich library integration"""

    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.colors = TerminalColors()

    def print_header(self, title: str, subtitle: Optional[str] = None) -> None:
        """Print a styled header"""
        if subtitle:
            header_text = f"[bold blue]{title}[/bold blue]\n[dim]{subtitle}[/dim]"
        else:
            header_text = f"[bold blue]{title}[/bold blue]"

        panel = Panel(
            header_text,
            border_style="blue",
            padding=(1, 2)
        )
        self.console.print(panel)

    def print_success(self, message: str, details: Optional[str] = None) -> None:
        """Print success message with optional details"""
        text = Text()
        text.append("✅ ", style="green")
        text.append(message, style="bold green")

        if details:
            text.append(f"\n   {details}", style="dim green")

        self.console.print(text)

    def print_error(self, message: str, details: Optional[str] = None) -> None:
        """Print error message with optional details"""
        text = Text()
        text.append("❌ ", style="red")
        text.append(message, style="bold red")

        if details:
            text.append(f"\n   {details}", style="dim red")

        self.console.print(text)

    def print_warning(self, message: str, details: Optional[str] = None) -> None:
        """Print warning message with optional details"""
        text = Text()
        text.append("⚠️  ", style="yellow")
        text.append(message, style="bold yellow")

        if details:
            text.append(f"\n   {details}", style="dim yellow")

        self.console.print(text)

    def print_info(self, message: str, details: Optional[str] = None) -> None:
        """Print info message with optional details"""
        text = Text()
        text.append("ℹ️  ", style="blue")
        text.append(message, style="bold blue")

        if details:
            text.append(f"\n   {details}", style="dim blue")

        self.console.print(text)

    def print_json(self, data: Union[Dict, list], title: Optional[str] = None) -> None:
        """Print JSON data with syntax highlighting"""
        if title:
            self.console.print(f"\n[bold cyan]{title}[/bold cyan]")

        json_obj = JSON.from_data(data)
        self.console.print(json_obj)

    def print_table(self, data: list, headers: list, title: Optional[str] = None) -> None:
        """Print data in a formatted table"""
        table = Table(title=title, show_header=True, header_style="bold magenta")

        # Add columns
        for header in headers:
            table.add_column(header, style="cyan")

        # Add rows
        for row in data:
            table.add_row(*[str(cell) for cell in row])

        self.console.print(table)

    def print_tree(self, data: Dict[str, Any], title: str = "Data Structure") -> None:
        """Print hierarchical data as a tree"""
        tree = Tree(f"[bold blue]{title}[/bold blue]")

        def add_to_tree(node, data_dict):
            for key, value in data_dict.items():
                if isinstance(value, dict):
                    branch = node.add(f"[yellow]{key}[/yellow]")
                    add_to_tree(branch, value)
                elif isinstance(value, list):
                    branch = node.add(f"[yellow]{key}[/yellow] [dim](list)[/dim]")
                    for i, item in enumerate(value):
                        if isinstance(item, dict):
                            item_branch = branch.add(f"[cyan]Item {i}[/cyan]")
                            add_to_tree(item_branch, item)
                        else:
                            branch.add(f"[green]{item}[/green]")
                else:
                    node.add(f"[yellow]{key}[/yellow]: [green]{value}[/green]")

        add_to_tree(tree, data)
        self.console.print(tree)

    def print_code(self, code: str, language: str = "python", title: Optional[str] = None) -> None:
        """Print code with syntax highlighting"""
        if title:
            self.console.print(f"\n[bold cyan]{title}[/bold cyan]")

        syntax = Syntax(code, language, theme="monokai", line_numbers=True)
        self.console.print(syntax)

    def create_progress_bar(self, description: str = "Processing...") -> Progress:
        """Create a progress bar for long-running operations"""
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=self.console
        )

    def print_separator(self, char: str = "─", length: int = 80, color: str = "dim white") -> None:
        """Print a separator line"""
        separator = Text(char * length, style=color)
        self.console.print(separator)

    def print_status_badge(self, status: str, message: str) -> None:
        """Print a status badge with message"""
        status_colors = {
            "PASS": "green",
            "FAIL": "red",
            "SKIP": "yellow",
            "INFO": "blue",
            "WARN": "yellow"
        }

        color = status_colors.get(status.upper(), "white")
        badge = f"[{color} on white] {status.upper()} [/{color} on white]"

        self.console.print(f"{badge} {message}")

# Global instances for easy access
terminal_colors = TerminalColors()
colored_output = ColoredOutput()