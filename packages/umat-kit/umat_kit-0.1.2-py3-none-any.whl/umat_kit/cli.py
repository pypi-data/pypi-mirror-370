from __future__ import annotations

import sys
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table

from .student_portal import main as student_portal_main

console = Console()

def show_main_menu():
    """Show the main application menu"""
    banner = Panel.fit(
        """
╔══════════════════════════════════════════════════════════════╗
║                     UMAT KIT TERMINAL                        ║
║                 Student Portal & Utilities                   ║
╚══════════════════════════════════════════════════════════════╝
        """.strip(),
        title="🎓 UMAT Kit",
        border_style="cyan",
    )
    console.print(banner)

    console.print("\n[bold cyan]Welcome to UMAT Kit![/bold cyan]")
    console.print("Choose an option to get started:\n")

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Option", style="bold cyan", width=8)
    table.add_column("Description", style="white")

    table.add_row("1", "🎓 Student Portal (Login Required)")
    table.add_row("2", "🔧 Developer Tools")
    table.add_row("0", "🚪 Exit")

    console.print(table)

def developer_tools():
    """Show developer tools menu"""
    console.print("\n[bold yellow]🔧 Developer Tools[/bold yellow]")
    console.print("[dim]These tools are for development and testing purposes[/dim]\n")

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Option", style="bold yellow", width=8)
    table.add_column("Description", style="white")

    table.add_row("1", "🧪 API Testing Mode")
    table.add_row("2", "📊 Quick Profile Test")
    table.add_row("0", "🔙 Back to Main Menu")

    console.print(table)

    choice = Prompt.ask("\n[bold yellow]Select developer option[/bold yellow]", default="0")

    if choice == "1":
        legacy_interactive_terminal()
    elif choice == "2":
        username = Prompt.ask("Enter username (student number)")
        password = Prompt.ask("Enter password", password=True)
        quick_test_flow(username, password)
    elif choice == "0":
        return
    else:
        console.print("[red]❌ Invalid option[/red]")

def quick_test_flow(username: str, password: str) -> None:
    """Quick test flow for developers"""
    from . import APIManager

    mgr = APIManager()
    if not mgr.authenticate(username, password):
        console.print("[red]Authentication failed[/]")
        console.print("[yellow]💡 If you're seeing server errors (502/503), the UMAT portal may be temporarily down.[/]")
        console.print("[yellow]   Please try again in a few minutes.[/]")
        return
    mgr.get_complete_user_profile(validate_data=True)
    mgr.logout()

def legacy_interactive_terminal() -> None:
    """Legacy API testing terminal (for developers)"""
    from . import APIManager

    banner = Panel.fit(
        """
╔══════════════════════════════════════════════════════════════╗
║                     UMAT KIT TERMINAL                        ║
║                 API Testing & Development                    ║
╚══════════════════════════════════════════════════════════════╝
        """.strip(),
        title="🧪 Developer Mode",
        border_style="yellow",
    )
    console.print(banner)

    # Credentials: always prompt (do not use .env)
    username = Prompt.ask("Enter username (student number)")
    password = Prompt.ask("Enter password", password=True)

    mgr = APIManager()
    if not mgr.authenticate(username, password):
        console.print("[red]Authentication failed[/]")
        console.print("[yellow]💡 If you're seeing server errors (502/503), the UMAT portal may be temporarily down.[/]")
        console.print("[yellow]   Please try again in a few minutes.[/]")
        return

    while True:
        _header("Main Menu")
        table = Table(show_header=False)
        table.add_column("k")
        table.add_column("Action")
        table.add_row("1", "Authentication flow test")
        table.add_row("2", "User info endpoints test")
        table.add_row("3", "Get complete user profile")
        table.add_row("4", "Session information")
        table.add_row("5", "API statistics")
        table.add_row("6", "Performance tests")
        table.add_row("7", "Export test results")
        table.add_row("8", "Run custom test (framework)")
        table.add_row("s", "Scripts hub (password gen, refs validator, etc.)")
        table.add_row("q", "Quit")
        console.print(table)

        choice = Prompt.ask("Select option", default="3").strip().lower()
        if choice == "q":
            break
        try:
            if choice == "1":
                mgr.login_api.test_authentication_flow(username, password)
            elif choice == "2":
                mgr.userinfo_api.test_user_info_endpoints()
            elif choice == "3":
                mgr.get_complete_user_profile(validate_data=True)
            elif choice == "4":
                mgr.print_session_status()
            elif choice == "5":
                mgr.print_api_statistics()
            elif choice == "6":
                # quick perf loop
                for _ in range(3):
                    mgr.userinfo_api.get_student_portal_info(use_cache=False)
            elif choice == "7":
                # no-op placeholder: export already supported in old main
                console.print("[yellow]Export hook — integrate with results store as needed[/]")
            elif choice == "8":
                console.print("[yellow]Custom tests entry — extend as needed[/]")
            elif choice == "s":
                scripts_hub()
            else:
                console.print("[yellow]Unknown option[/]")
        except KeyboardInterrupt:
            console.print("[yellow]\nCancelled[/]")
        except Exception as e:
            console.print(f"[red]❌ An error occurred: {str(e)}[/]")
            console.print("[yellow]💡 Please try again or contact support if the issue persists[/]")
        _pause()

    mgr.logout()


def scripts_hub() -> None:
    from .scripts import (
        password_generator as pwdgen,
        validate_refs as vrefs,
        umat_reference_generator as refgen,
        umat_reference_analyzer as refana,
        userinfo as userinfo_script,
        login as login_script,
        test_runner as runner,
    )

    while True:
        _header("Scripts Hub")
        table = Table(show_header=False)
        table.add_column("k")
        table.add_column("Script")
        table.add_row("1", "Password Generator (Rich)")
        table.add_row("2", "Validate Refs (Rich + requests)")
        table.add_row("3", "UMAT Reference Generator")
        table.add_row("4", "UMAT Reference Analyzer")
        table.add_row("5", "Login Tester")
        table.add_row("6", "UserInfo Tester")
        table.add_row("7", "Test Runner Demo")
        table.add_row("b", "Back")
        console.print(table)

        choice = Prompt.ask("Select script", default="b").strip().lower()
        if choice == "b":
            return
        try:
            if choice == "1":
                pwdgen.main()
            elif choice == "2":
                vrefs.main()
            elif choice == "3":
                refgen.main()
            elif choice == "4":
                refana.analyze_reference_numbers()
            elif choice == "5":
                login_script.main()
            elif choice == "6":
                userinfo_script.main()
            elif choice == "7":
                runner.main()
            else:
                console.print("[yellow]Unknown option[/]")
        except SystemExit:
            # Some scripts may sys.exit; swallow for hub UX
            pass
        except Exception as e:
            console.print(f"[red]Script error:[/] {e}")
        _pause()


def main(argv: Optional[list[str]] = None) -> int:
    """Main CLI entry point"""
    argv = argv or sys.argv[1:]

    if not argv:
        # Default: show main menu
        main_menu()
        return 0

    # Handle commands
    cmd = argv[0]
    if cmd in {"interactive", "ui", "portal"}:
        # Student portal
        student_portal_main()
        return 0
    elif cmd == "dev":
        # Developer tools
        developer_tools()
        return 0
    elif cmd == "quick" and len(argv) >= 3:
        # Quick test (for developers)
        quick_test_flow(argv[1], argv[2])
        return 0
    elif cmd == "legacy":
        # Legacy testing mode
        legacy_interactive_terminal()
        return 0

    console.print("[yellow]Usage:[/]")
    console.print("  umat-kli                    - Main menu")
    console.print("  umat-kli portal             - Student portal")
    console.print("  umat-kli dev                - Developer tools")
    console.print("  umat-kli quick <user> <pass> - Quick test")
    console.print("  umat-kli legacy             - Legacy testing mode")
    return 2

def main_menu():
    """Main application menu"""
    while True:
        show_main_menu()

        try:
            choice = Prompt.ask("\n[bold cyan]Select an option[/bold cyan]", default="0")

            if choice == "0":
                console.print("\n[green]👋 Thank you for using UMAT Kit![/green]")
                break
            elif choice == "1":
                student_portal_main()
            elif choice == "2":
                developer_tools()
            else:
                console.print("[red]❌ Invalid option. Please try again.[/red]")

        except KeyboardInterrupt:
            console.print("\n[yellow]👋 Goodbye![/yellow]")
            break
        except Exception as e:
            console.print(f"[red]❌ An error occurred: {str(e)}[/red]")

def _header(title: str, subtitle: Optional[str] = None) -> None:
    """Display section header"""
    console.rule(f"[bold cyan]{title}[/bold cyan]")
    if subtitle:
        console.print(f"[dim]{subtitle}[/dim]")

def _pause() -> None:
    """Pause for user input"""
    try:
        Prompt.ask("Press Enter to continue", default="")
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    raise SystemExit(main())