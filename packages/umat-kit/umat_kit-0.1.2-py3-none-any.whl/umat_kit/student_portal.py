"""
UMAT Student Portal CLI
Interactive student portal interface
"""

from __future__ import annotations

import sys
from typing import Optional, Dict, Any, List
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.text import Text
from rich.columns import Columns
from rich.align import Align

from . import APIManager
from .admin_config import admin_config
from .utils.utils.terminal_colors import colored_output

console = Console()

class StudentPortal:
    """Interactive Student Portal"""

    def __init__(self):
        self.api_manager: Optional[APIManager] = None
        self.current_user: Optional[str] = None
        self.is_admin: bool = False
        self.user_data: Optional[Dict[str, Any]] = None

    def show_banner(self):
        """Display portal banner"""
        banner = Panel.fit(
            """
╔══════════════════════════════════════════════════════════════╗
║                    UMAT STUDENT PORTAL                       ║
║                  Interactive CLI Interface                   ║
╚══════════════════════════════════════════════════════════════╝
            """.strip(),
            title="🎓 UMAT Portal",
            border_style="cyan",
        )
        console.print(banner)

    def authenticate(self) -> bool:
        """Handle user authentication"""
        console.print("\n[bold cyan]🔐 Student Portal Login[/bold cyan]")

        username = Prompt.ask("Enter your student number")
        password = Prompt.ask("Enter your password", password=True)

        # Initialize API manager
        self.api_manager = APIManager()

        # Attempt authentication
        if self.api_manager.authenticate(username, password):
            self.current_user = username
            self.is_admin = admin_config.is_admin(username, password)

            # Get user data
            self._load_user_data()

            return True
        else:
            return False

    def _load_user_data(self):
        """Load user data from API silently"""
        if self.api_manager:
            try:
                # Load data silently without displaying it
                response = self.api_manager.userinfo_api.get_student_portal_info(
                    use_cache=False,
                    validate_data=False,
                    display_info=False
                )
                if response.is_success and response.data:
                    self.user_data = response.data
            except Exception as e:
                console.print(f"[yellow]⚠️ Could not load user data: {str(e)}[/yellow]")

    def show_dashboard(self):
        """Display main dashboard"""
        if not self.current_user:
            return

        # Enhanced welcome message
        user_name = "Student"
        programme = ""
        level = ""

        if self.user_data:
            user_name = self.user_data.get('fullName', self.current_user)
            programme = self.user_data.get('programme', '')
            level = self.user_data.get('level', '')

        # Create a more detailed welcome message
        welcome_content = f"[bold green]Welcome back, {user_name}![/bold green]\n\n"
        welcome_content += f"🆔 Student Number: [cyan]{self.current_user}[/cyan]\n"

        if programme:
            welcome_content += f"📚 Programme: [blue]{programme}[/blue]\n"
        if level:
            welcome_content += f"📊 Level: [yellow]{level}[/yellow]\n"

        if self.is_admin:
            welcome_content += f"\n[red]🔧 Admin Access Enabled[/red]"

        welcome_panel = Panel(
            welcome_content,
            title="👋 Dashboard",
            title_align="center",
            border_style="green",
            padding=(1, 2)
        )
        console.print(welcome_panel)

        # Main menu
        while True:
            self._show_main_menu()

            try:
                choice = Prompt.ask("\n[bold cyan]Select an option[/bold cyan]", default="0")

                if choice == "0":
                    break
                elif choice == "1":
                    self._show_profile()
                elif choice == "2":
                    self._password_generator()
                elif choice == "3":
                    self._course_registration_menu()
                elif choice == "4":
                    self._academic_results_menu()
                elif choice == "5":
                    self._bills_payment_menu()
                elif choice == "6":
                    self._course_assessment_menu()
                elif choice == "7" and self.is_admin:
                    self._admin_reference_menu()
                elif choice == "8":
                    self._refresh_data()
                elif choice == "9":
                    self._about()
                else:
                    console.print("[red]❌ Invalid option. Please try again.[/red]")

                if choice != "0":
                    self._pause()

            except KeyboardInterrupt:
                console.print("\n[yellow]👋 Goodbye![/yellow]")
                break

    def _show_main_menu(self):
        """Display main menu options"""
        console.print("\n" + "="*60)
        console.print("[bold cyan]📋 MAIN MENU[/bold cyan]")
        console.print("="*60)

        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Option", style="bold cyan")
        table.add_column("Description", style="white")

        table.add_row("1", "👤 View Profile")
        table.add_row("2", "🔐 Generate VLE & Email Credentials")
        table.add_row("3", "📚 Course Registration")
        table.add_row("4", "📊 Check Academic Results")
        table.add_row("5", "💰 Bills and Payment")
        table.add_row("6", "📝 Course Assessment")

        if self.is_admin:
            table.add_row("7", "🔧 Reference Management (Admin)")

        table.add_row("8", "🔄 Refresh Data")
        table.add_row("9", "ℹ️  About")
        table.add_row("0", "🚪 Exit")

        console.print(table)

    def _show_profile(self):
        """Display user profile information with enhanced UI"""
        console.print("\n")
        console.rule("[bold cyan]👤 Student Profile[/bold cyan]", style="cyan")

        if not self.user_data:
            console.print("[yellow]⚠️ No profile data available. Please refresh your data first.[/yellow]")
            return

        # Display profile image if available
        self._display_profile_image()

        # Helper function to format values
        def format_value(value):
            if value is None or value == "" or value == "null":
                return "[dim italic]Not Available[/dim italic]"
            return str(value)

        # Format date of birth
        def format_date(date_str):
            if not date_str or date_str == "null":
                return "[dim italic]Not Available[/dim italic]"
            try:
                from datetime import datetime
                # Parse the date string
                date_obj = datetime.fromisoformat(date_str.replace('T00:00:00', ''))
                return date_obj.strftime("%B %d, %Y")
            except:
                return str(date_str)

        # Create main profile layout using columns
        from rich.columns import Columns

        # Personal Information Section
        personal_table = Table(title="👤 Personal Information",
                             title_style="bold blue",
                             box=None,
                             show_header=False,
                             padding=(0, 1))
        personal_table.add_column("Field", style="bold cyan", width=18)
        personal_table.add_column("Value", style="white", width=35)

        # Add personal information rows (explicit to avoid duplicates)
        personal_table.add_row("📛 Full Name", format_value(self.user_data.get('fullName')))
        personal_table.add_row("🆔 Student Number", format_value(self.user_data.get('studentNumber')))
        personal_table.add_row("📋 Index Number", format_value(self.user_data.get('indexNumber')))
        personal_table.add_row("📞 Phone Number", format_value(self.user_data.get('phoneNumber')))
        personal_table.add_row("📧 Email", format_value(self.user_data.get('email')))
        personal_table.add_row("🎂 Date of Birth", format_date(self.user_data.get('dateOfBirth')))
        personal_table.add_row("🏠 Address", format_value(self.user_data.get('address')))

        # Academic Information Section
        academic_table = Table(title="🎓 Academic Information",
                              title_style="bold green",
                              box=None,
                              show_header=False,
                              padding=(0, 1))
        academic_table.add_column("Field", style="bold cyan", width=18)
        academic_table.add_column("Value", style="white", width=35)

        # Add academic information rows (explicit to avoid duplicates)
        academic_table.add_row("📚 Programme", format_value(self.user_data.get('programme')))
        academic_table.add_row("🏢 Department", format_value(self.user_data.get('department')))
        academic_table.add_row("🏫 Campus", format_value(self.user_data.get('campus')))
        academic_table.add_row("📊 Current Level", format_value(self.user_data.get('level')))
        academic_table.add_row("📅 Year Group", format_value(self.user_data.get('yearGroup')))

        # Display tables side by side
        console.print()
        console.print(Columns([personal_table, academic_table], equal=True, expand=True))

        # Add a nice footer
        console.print()
        footer_panel = Panel(
            f"[dim]Profile last updated: {self._get_current_time()}[/dim]",
            border_style="dim",
            padding=(0, 1)
        )
        console.print(footer_panel)

    def _display_profile_image(self):
        """Display profile image as ASCII art"""
        photo_url = self.user_data.get('photoUrl')
        if not photo_url:
            return

        try:
            import ascii_magic
            console.print("\n[dim]Loading profile image...[/dim]")

            # Generate ASCII art from the profile image URL
            ascii_art_obj = ascii_magic.from_url(photo_url)

            # Display ASCII art directly to terminal (preferred style)
            ascii_art_obj.to_terminal(columns=50, width_ratio=2.0)
            console.print()

        except ImportError:
            console.print("[yellow]⚠️ ASCII image display not available (missing ascii-magic)[/yellow]")
            self._show_placeholder_image()
        except Exception as e:
            console.print(f"[yellow]⚠️ Could not load profile image: {str(e)}[/yellow]")
            self._show_placeholder_image()

    def _show_placeholder_image(self):
        """Show a placeholder when profile image cannot be loaded"""
        placeholder_panel = Panel(
            "[dim]👤\n\nProfile Photo\nNot Available[/dim]",
            title="📸 Profile Photo",
            title_align="center",
            border_style="dim",
            padding=(1, 2),
            width=30
        )
        console.print(Align.center(placeholder_panel))
        console.print()

    def _get_current_time(self):
        """Get current time formatted"""
        from datetime import datetime
        return datetime.now().strftime("%B %d, %Y at %I:%M %p")

    def _password_generator(self):
        """Generate UMAT student credentials (VLE & Email) based on UMAT standard"""
        console.print("\n")
        console.rule("[bold cyan]🔐 UMAT Credential Generator[/bold cyan]", style="cyan")

        if not self.user_data:
            console.print("[yellow]⚠️ No user data available. Please refresh your data first.[/yellow]")
            return

        try:
            from .scripts.gen_vle_logins import VLELoginGenerator
            from .scripts.activate_stu_email import StudentEmailActivator

            # Extract user information
            full_name = self.user_data.get('fullName', '')
            student_number = self.user_data.get('studentNumber', '')
            department = self.user_data.get('department', '')

            if not full_name or not student_number:
                console.print("[red]❌ Missing required user information (name or student number)[/red]")
                return

            # Generate VLE credentials
            vle_generator = VLELoginGenerator()
            vle_credentials = vle_generator.generate_credentials(full_name, student_number, department)
            vle_generator.display_credentials(vle_credentials)

            # Generate email credentials
            email_activator = StudentEmailActivator()
            email_credentials = email_activator.generate_email_credentials(vle_credentials)
            email_activator.display_email_credentials(vle_credentials, email_credentials)

        except Exception as e:
            console.print(f"[red]❌ Error generating credentials: {str(e)}[/red]")

    def _admin_reference_menu(self):
        """Admin reference management menu"""
        if not self.is_admin:
            console.print("[red]❌ Admin access required[/red]")
            return

        console.print("\n[bold red]🔧 REFERENCE MANAGEMENT (ADMIN)[/bold red]")

        admin_table = Table(show_header=False, box=None, padding=(0, 2))
        admin_table.add_column("Option", style="bold red")
        admin_table.add_column("Description", style="white")

        admin_table.add_row("1", "🎯 Generate Reference Number")
        admin_table.add_row("2", "📊 Analyze Reference Numbers")
        admin_table.add_row("3", "✅ Validate Reference Numbers")
        admin_table.add_row("0", "🔙 Back to Main Menu")

        console.print(admin_table)

        choice = Prompt.ask("\n[bold red]Select admin option[/bold red]", default="0")

        try:
            if choice == "1":
                self._reference_generator()
            elif choice == "2":
                self._reference_analyzer()
            elif choice == "3":
                self._reference_validator()
            elif choice == "0":
                return
            else:
                console.print("[red]❌ Invalid option[/red]")
        except Exception as e:
            console.print(f"[red]❌ Error: {str(e)}[/red]")

    def _reference_generator(self):
        """Reference number generator (Admin only)"""
        console.print("\n[bold red]🎯 Reference Number Generator[/bold red]")

        try:
            from .scripts.umat_reference_generator import main as ref_gen_main
            ref_gen_main()
        except ImportError:
            console.print("[red]❌ Reference generator not available[/red]")
        except Exception as e:
            console.print(f"[red]❌ Error: {str(e)}[/red]")

    def _reference_analyzer(self):
        """Reference number analyzer (Admin only)"""
        console.print("\n[bold red]📊 Reference Number Analyzer[/bold red]")

        try:
            from .scripts.umat_reference_analyzer import main as ref_ana_main
            ref_ana_main()
        except ImportError:
            console.print("[red]❌ Reference analyzer not available[/red]")
        except Exception as e:
            console.print(f"[red]❌ Error: {str(e)}[/red]")

    def _reference_validator(self):
        """Reference number validator (Admin only)"""
        console.print("\n[bold red]✅ Reference Number Validator[/bold red]")

        try:
            from .scripts.validate_refs import main as ref_val_main
            ref_val_main()
        except ImportError:
            console.print("[red]❌ Reference validator not available[/red]")
        except Exception as e:
            console.print(f"[red]❌ Error: {str(e)}[/red]")

    def _refresh_data(self):
        """Refresh user data"""
        console.print("\n[bold cyan]🔄 Refreshing Data...[/bold cyan]")

        if self.api_manager:
            self._load_user_data()
            if self.user_data:
                console.print("[green]✅ Data refreshed successfully[/green]")
            else:
                console.print("[yellow]⚠️ Could not refresh data[/yellow]")
        else:
            console.print("[red]❌ Not connected to portal[/red]")

    def _about(self):
        """Show about information"""
        about_panel = Panel(
            """
[bold cyan]UMAT Student Portal CLI[/bold cyan]

Version: 1.0.0
Developer: UMAT Kit Team

This is an interactive command-line interface for UMAT students
to access their portal information and utilities.

[bold]Features:[/bold]
• View student profile and academic information
• Generate secure passwords
• Admin tools for reference number management

[bold]Support:[/bold]
For technical support, contact the IT department.
            """.strip(),
            title="ℹ️ About",
            border_style="blue"
        )
        console.print(about_panel)

    def _course_registration_menu(self):
        """Display course registration menu"""
        console.print("\n")
        console.rule("[bold cyan]📚 Course Registration[/bold cyan]", style="cyan")

        # Create registration menu
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Option", style="bold cyan")
        table.add_column("Description", style="white")

        table.add_row("1", "📝 Regular Registration")
        table.add_row("2", "🔄 Resit Registration")
        table.add_row("0", "🔙 Back to Main Menu")

        console.print(table)

        while True:
            try:
                choice = Prompt.ask("\n[bold cyan]Select registration type[/bold cyan]", default="0")

                if choice == "0":
                    break
                elif choice == "1":
                    self._show_regular_registration()
                elif choice == "2":
                    self._show_resit_registration()
                else:
                    console.print("[red]❌ Invalid option. Please try again.[/red]")

                if choice != "0":
                    self._pause()

            except KeyboardInterrupt:
                break

    def _show_regular_registration(self):
        """Display regular course registration"""
        console.print("\n")
        console.rule("[bold green]📝 Regular Course Registration[/bold green]", style="green")

        if not self.api_manager:
            console.print("[red]❌ API Manager not available[/red]")
            return

        # Show loading message
        with console.status("[bold green]Loading regular registration data...", spinner="dots"):
            registration_data = self.api_manager.get_regular_registration()

        if not registration_data.get('success'):
            error_msg = registration_data.get('error', 'Unknown error occurred')
            console.print(f"[red]❌ Failed to load registration data: {error_msg}[/red]")
            return

        courses = registration_data.get('courses', [])
        summary = registration_data.get('summary', {})

        if not courses:
            console.print("[yellow]⚠️ No regular registration data found[/yellow]")
            return

        # Display registration summary
        self._display_registration_summary(summary, "Regular Registration Summary")

        # Display courses table
        self._display_courses_table(courses, "📝 Regular Courses")

    def _show_resit_registration(self):
        """Display resit course registration"""
        console.print("\n")
        console.rule("[bold yellow]🔄 Resit Course Registration[/bold yellow]", style="yellow")

        if not self.api_manager:
            console.print("[red]❌ API Manager not available[/red]")
            return

        # Show loading message
        with console.status("[bold yellow]Loading resit registration data...", spinner="dots"):
            registration_data = self.api_manager.get_resit_registration()

        if not registration_data.get('success'):
            error_msg = registration_data.get('error', 'Unknown error occurred')
            console.print(f"[red]❌ Failed to load registration data: {error_msg}[/red]")
            return

        courses = registration_data.get('courses', [])
        summary = registration_data.get('summary', {})

        if not courses:
            console.print("[yellow]⚠️ No resit registration data found[/yellow]")
            return

        # Display registration summary
        self._display_registration_summary(summary, "Resit Registration Summary")

        # Display courses table
        self._display_courses_table(courses, "🔄 Resit Courses")

    def _display_registration_summary(self, summary: Dict[str, Any], title: str):
        """Display registration summary information"""
        if not summary:
            return

        # Create summary table
        summary_table = Table(title=f"📊 {title}",
                            title_style="bold cyan",
                            border_style="cyan",
                            show_header=True,
                            header_style="bold cyan")

        summary_table.add_column("Metric", style="bold cyan", width=20)
        summary_table.add_column("Value", style="white", width=15)

        # Add summary rows
        summary_table.add_row("📚 Total Courses", str(summary.get('total_courses', 0)))
        summary_table.add_row("🎯 Total Credits", str(summary.get('total_credits', 0)))
        summary_table.add_row("✅ Registered", str(summary.get('registered_courses', 0)))
        summary_table.add_row("⏳ Pending", str(summary.get('pending_courses', 0)))
        summary_table.add_row("❌ Not Registered", str(summary.get('failed_courses', 0)))

        if summary.get('programme'):
            summary_table.add_row("🎓 Programme", summary.get('programme', 'N/A'))

        if summary.get('academic_period'):
            summary_table.add_row("📅 Academic Period", summary.get('academic_period', 'N/A'))

        console.print(summary_table)
        console.print()

    def _display_courses_table(self, courses: List[Dict[str, Any]], title: str):
        """Display courses in a formatted table"""
        if not courses:
            return

        # Create courses table
        courses_table = Table(title=title,
                            title_style="bold cyan",
                            border_style="cyan",
                            show_header=True,
                            header_style="bold cyan")

        courses_table.add_column("Code", style="bold yellow", width=10)
        courses_table.add_column("Course Name", style="white", width=35)
        courses_table.add_column("Credits", style="cyan", width=8, justify="center")
        courses_table.add_column("Status", style="white", width=25)
        courses_table.add_column("Examiner", style="blue", width=20)

        # Add course rows
        for course in courses:
            # Format status with color coding
            status = course.get('registration_status_desc', 'Unknown')
            status_code = course.get('registration_status', 0)

            if status_code == 1:  # Registered
                status_display = f"[green]✅ {status}[/green]"
            elif status_code == 2:  # Pending
                status_display = f"[yellow]⏳ {status}[/yellow]"
            elif status_code == 3:  # Not registered
                status_display = f"[red]❌ {status}[/red]"
            else:
                status_display = f"[dim]{status}[/dim]"

            courses_table.add_row(
                course.get('code', 'N/A'),
                course.get('name', 'N/A'),
                str(course.get('credit', 0)),
                status_display,
                course.get('first_examiner', 'N/A')
            )

        console.print(courses_table)

        # Display additional course details if available
        registered_count = len([c for c in courses if c.get('registration_status') == 1])
        total_credits = sum(c.get('credit', 0) for c in courses if c.get('registration_status') == 1)

        if registered_count > 0:
            console.print(f"\n[green]✅ Successfully registered for {registered_count} courses ({total_credits} credits)[/green]")

    def _academic_results_menu(self):
        """Display academic results"""
        console.print("\n")
        console.rule("[bold cyan]📊 Academic Results[/bold cyan]", style="cyan")

        if not self.api_manager:
            console.print("[red]❌ API Manager not available[/red]")
            return

        # Show loading message
        with console.status("[bold cyan]Loading academic results...", spinner="dots"):
            results_data = self.api_manager.get_academic_results()

        if not results_data.get('success'):
            error_msg = results_data.get('error', 'Unknown error occurred')
            console.print(f"[red]❌ Failed to load academic results: {error_msg}[/red]")
            return

        semesters = results_data.get('semesters', [])
        summary = results_data.get('summary', {})

        if not semesters:
            console.print("[yellow]⚠️ No academic results found[/yellow]")
            return

        # Display overall summary
        self._display_academic_summary(summary)

        # Display semester-by-semester results
        self._display_semester_results(semesters)

    def _display_academic_summary(self, summary: Dict[str, Any]):
        """Display overall academic summary"""
        if not summary:
            return

        # Create summary table
        summary_table = Table(title="🎓 Academic Performance Summary",
                            title_style="bold cyan",
                            border_style="cyan",
                            show_header=True,
                            header_style="bold cyan")

        summary_table.add_column("Metric", style="bold cyan", width=25)
        summary_table.add_column("Value", style="white", width=20)

        # Student information
        student_info = summary.get('student_info', {})
        if student_info.get('full_name'):
            summary_table.add_row("👤 Student Name", student_info.get('full_name', 'N/A'))

        summary_table.add_row("🆔 Student Number", summary.get('student_number', 'N/A'))
        summary_table.add_row("📋 Index Number", summary.get('index_number', 'N/A'))
        summary_table.add_row("📚 Current Level", summary.get('current_level', 'N/A'))
        summary_table.add_row("📅 Academic Year", summary.get('current_academic_year', 'N/A'))

        # Academic metrics
        summary_table.add_row("", "")  # Separator
        summary_table.add_row("📊 Total Semesters", str(summary.get('total_semesters', 0)))
        summary_table.add_row("🎯 Credits Registered", str(summary.get('total_credits_registered', 0)))
        summary_table.add_row("✅ Credits Earned", str(summary.get('total_credits_earned', 0)))

        # CWA with color coding
        cwa = summary.get('overall_cwa', 0.0)
        if cwa >= 70:
            cwa_display = f"[green]{cwa:.2f}[/green]"
        elif cwa >= 60:
            cwa_display = f"[yellow]{cwa:.2f}[/yellow]"
        elif cwa >= 50:
            cwa_display = f"[orange1]{cwa:.2f}[/orange1]"
        else:
            cwa_display = f"[red]{cwa:.2f}[/red]"

        summary_table.add_row("🏆 Overall CWA", cwa_display)

        # Course statistics
        summary_table.add_row("", "")  # Separator
        summary_table.add_row("📖 Total Courses", str(summary.get('total_courses', 0)))
        summary_table.add_row("✅ Passed Courses", f"[green]{summary.get('passed_courses', 0)}[/green]")
        summary_table.add_row("❌ Failed Courses", f"[red]{summary.get('failed_courses', 0)}[/red]")
        summary_table.add_row("⚠️ Trailed Courses", f"[yellow]{summary.get('trailed_courses', 0)}[/yellow]")

        console.print(summary_table)
        console.print()

    def _display_semester_results(self, semesters: List[Dict[str, Any]]):
        """Display detailed semester results"""
        if not semesters:
            return

        # Sort semesters by year and semester
        sorted_semesters = sorted(semesters, key=lambda x: (x.get('year', 0), x.get('semester', 0)))

        for semester_data in sorted_semesters:
            self._display_single_semester(semester_data)
            console.print()

    def _display_single_semester(self, semester_data: Dict[str, Any]):
        """Display results for a single semester"""
        year = semester_data.get('year', 0)
        semester = semester_data.get('semester', 0)
        academic_year = semester_data.get('academic_year', 'N/A')

        # Determine level name
        level_name = "Unknown"
        if year == 100:
            level_name = "Level 100"
        elif year == 200:
            level_name = "Level 200"
        elif year == 300:
            level_name = "Level 300"
        elif year == 400:
            level_name = "Level 400"

        semester_title = f"📚 {level_name} - Semester {semester} ({academic_year})"

        # Semester performance summary
        perf_table = Table(title=semester_title,
                          title_style="bold blue",
                          border_style="blue",
                          show_header=True,
                          header_style="bold blue")

        perf_table.add_column("Metric", style="bold blue", width=20)
        perf_table.add_column("Value", style="white", width=15)

        perf_table.add_row("📊 Credits Registered", str(semester_data.get('credit_registered', 0)))
        perf_table.add_row("✅ Credits Earned", str(semester_data.get('credit_earned', 0)))

        # Semester average with color coding
        sem_avg = semester_data.get('semester_average', 0.0)
        if sem_avg >= 70:
            avg_display = f"[green]{sem_avg:.2f}[/green]"
        elif sem_avg >= 60:
            avg_display = f"[yellow]{sem_avg:.2f}[/yellow]"
        elif sem_avg >= 50:
            avg_display = f"[orange1]{sem_avg:.2f}[/orange1]"
        else:
            avg_display = f"[red]{sem_avg:.2f}[/red]"

        perf_table.add_row("📈 Semester Average", avg_display)

        # CWA with color coding
        cwa = semester_data.get('cwa', 0.0)
        if cwa >= 70:
            cwa_display = f"[green]{cwa:.2f}[/green]"
        elif cwa >= 60:
            cwa_display = f"[yellow]{cwa:.2f}[/yellow]"
        elif cwa >= 50:
            cwa_display = f"[orange1]{cwa:.2f}[/orange1]"
        else:
            cwa_display = f"[red]{cwa:.2f}[/red]"

        perf_table.add_row("🏆 Cumulative CWA", cwa_display)

        console.print(perf_table)

        # Courses table
        courses = semester_data.get('courses', [])
        if courses:
            courses_table = Table(title=f"📖 Courses - {level_name} Semester {semester}",
                                title_style="bold green",
                                border_style="green",
                                show_header=True,
                                header_style="bold green")

            courses_table.add_column("Code", style="bold yellow", width=8)
            courses_table.add_column("Course Name", style="white", width=30)
            courses_table.add_column("Credits", style="cyan", width=7, justify="center")
            courses_table.add_column("Class", style="blue", width=6, justify="center")
            courses_table.add_column("Exam", style="blue", width=6, justify="center")
            courses_table.add_column("Total", style="bold white", width=6, justify="center")
            courses_table.add_column("Grade", style="white", width=6, justify="center")
            courses_table.add_column("Status", style="white", width=12)

            for course in courses:
                # Format scores
                class_score = course.get('class_score')
                exam_score = course.get('exam_score')
                full_score = course.get('full_score')

                class_display = f"{class_score:.1f}" if class_score is not None else "N/A"
                exam_display = f"{exam_score:.1f}" if exam_score is not None else "N/A"
                total_display = f"{full_score:.1f}" if full_score is not None else "N/A"

                # Special case handling
                special_case = course.get('special_case')
                if special_case == 'I':
                    total_display = "[yellow]Incomplete[/yellow]"
                elif special_case:
                    total_display = f"[yellow]{special_case}[/yellow]"

                # Grade with color coding
                letter = course.get('letter', 'N/A')
                if letter == 'A':
                    grade_display = f"[green]{letter}[/green]"
                elif letter == 'B':
                    grade_display = f"[blue]{letter}[/blue]"
                elif letter == 'C':
                    grade_display = f"[yellow]{letter}[/yellow]"
                elif letter == 'D':
                    grade_display = f"[orange1]{letter}[/orange1]"
                elif letter == 'F':
                    grade_display = f"[red]{letter}[/red]"
                else:
                    grade_display = f"[dim]{letter}[/dim]"

                # Status
                descriptions = course.get('descriptions', 'N/A')
                if descriptions == 'Excellent':
                    status_display = f"[green]{descriptions}[/green]"
                elif descriptions == 'Very Good':
                    status_display = f"[blue]{descriptions}[/blue]"
                elif descriptions == 'Good':
                    status_display = f"[yellow]{descriptions}[/yellow]"
                elif descriptions == 'Pass':
                    status_display = f"[orange1]{descriptions}[/orange1]"
                elif descriptions == 'Fail':
                    status_display = f"[red]{descriptions}[/red]"
                else:
                    status_display = f"[dim]{descriptions}[/dim]"

                courses_table.add_row(
                    course.get('code', 'N/A'),
                    course.get('course_name', 'N/A'),
                    str(course.get('credit', 0)),
                    class_display,
                    exam_display,
                    total_display,
                    grade_display,
                    status_display
                )

            console.print(courses_table)

        # Display remarks (failed/trailed courses) if any
        remarks = semester_data.get('remarks', [])
        if remarks:
            console.print(f"\n[red]⚠️ Courses with Issues ({level_name} Semester {semester}):[/red]")

            remarks_table = Table(border_style="red",
                                show_header=True,
                                header_style="bold red")

            remarks_table.add_column("Code", style="bold yellow", width=8)
            remarks_table.add_column("Course Name", style="white", width=25)
            remarks_table.add_column("Assignment", style="blue", width=10, justify="center")
            remarks_table.add_column("Quiz 1", style="blue", width=8, justify="center")
            remarks_table.add_column("Quiz 2", style="blue", width=8, justify="center")
            remarks_table.add_column("Class", style="blue", width=8, justify="center")
            remarks_table.add_column("Exam", style="blue", width=8, justify="center")
            remarks_table.add_column("Total", style="bold white", width=8, justify="center")
            remarks_table.add_column("Status", style="white", width=10)

            for remark in remarks:
                exam_details = remark.get('exam_score_details', {})

                # Format scores
                assignment = exam_details.get('assignment')
                quiz1 = exam_details.get('quiz_1')
                quiz2 = exam_details.get('quiz_2')
                class_assess = exam_details.get('class_assessment')
                exam = exam_details.get('exam')
                full = exam_details.get('full')

                assignment_display = f"{assignment:.1f}" if assignment is not None else "N/A"
                quiz1_display = f"{quiz1:.1f}" if quiz1 is not None else "N/A"
                quiz2_display = f"{quiz2:.1f}" if quiz2 is not None else "N/A"
                class_display = f"{class_assess:.1f}" if class_assess is not None else "N/A"
                exam_display = f"{exam:.1f}" if exam is not None else "N/A"
                total_display = f"{full:.1f}" if full is not None else "N/A"

                # Status
                status = exam_details.get('descriptions', 'N/A')
                status_display = f"[red]{status}[/red]" if status == 'Fail' else f"[yellow]{status}[/yellow]"

                remarks_table.add_row(
                    remark.get('code', 'N/A'),
                    remark.get('name', 'N/A'),
                    assignment_display,
                    quiz1_display,
                    quiz2_display,
                    class_display,
                    exam_display,
                    total_display,
                    status_display
                )

            console.print(remarks_table)

    def _bills_payment_menu(self):
        """Display bills and payment information"""
        console.print("\n")
        console.rule("[bold cyan]💰 Bills and Payment[/bold cyan]", style="cyan")

        if not self.api_manager:
            console.print("[red]❌ API Manager not available[/red]")
            return

        # Show loading message
        with console.status("[bold cyan]Loading bills and payment data...", spinner="dots"):
            bills_data = self.api_manager.get_bills_and_payments()

        if not bills_data.get('success'):
            error_msg = bills_data.get('error', 'Unknown error occurred')
            console.print(f"[red]❌ Failed to load bills and payment data: {error_msg}[/red]")
            return

        bill_summary = bills_data.get('bill_summary', {})
        student_bills = bills_data.get('student_bills', [])
        transactions = bills_data.get('transactions', {})
        payment_summary = bills_data.get('payment_summary', {})

        # Display payment summary
        self._display_payment_summary(payment_summary, bill_summary)

        # Display detailed bills
        if student_bills:
            self._display_detailed_bills(student_bills)

        # Display transaction history
        if transactions.get('school_fees') or transactions.get('other_fees'):
            self._display_transaction_history(transactions)

    def _display_payment_summary(self, payment_summary: Dict[str, Any], bill_summary: Dict[str, Any]):
        """Display payment summary overview"""
        if not payment_summary and not bill_summary:
            return

        # Create payment summary table
        summary_table = Table(title="💰 Payment Summary Overview",
                            title_style="bold cyan",
                            border_style="cyan",
                            show_header=True,
                            header_style="bold cyan")

        summary_table.add_column("Metric", style="bold cyan", width=25)
        summary_table.add_column("Amount", style="white", width=15)
        summary_table.add_column("Status", style="white", width=15)

        currency = payment_summary.get('currency', 'GHS')

        # Current bill information
        current_bill = bill_summary.get('current_bill', 0.0)
        previous_balance = bill_summary.get('previous_balance', 0.0)
        total_current_bill = bill_summary.get('total_current_bill', 0.0)

        summary_table.add_row("💳 Current Bill", f"{current_bill:,.2f} {currency}", "")
        summary_table.add_row("📋 Previous Balance", f"{previous_balance:,.2f} {currency}", "")
        summary_table.add_row("📊 Total Current Bill", f"{total_current_bill:,.2f} {currency}", "")

        # Payment information
        amount_paid = bill_summary.get('amount_paid', 0.0)
        outstanding_balance = bill_summary.get('outstanding_balance', 0.0)
        refund = bill_summary.get('refund', 0.0)

        summary_table.add_row("", "", "")  # Separator
        summary_table.add_row("💵 Amount Paid", f"{amount_paid:,.2f} {currency}", "")

        # Outstanding balance with color coding
        if outstanding_balance <= 0:
            balance_display = f"[green]{outstanding_balance:,.2f} {currency}[/green]"
            status_display = "[green]✅ Paid[/green]"
        elif outstanding_balance > 0:
            balance_display = f"[red]{outstanding_balance:,.2f} {currency}[/red]"
            status_display = "[red]❌ Outstanding[/red]"
        else:
            balance_display = f"[blue]{outstanding_balance:,.2f} {currency}[/blue]"
            status_display = "[blue]💰 Overpaid[/blue]"

        summary_table.add_row("⚖️ Outstanding Balance", balance_display, status_display)

        if refund > 0:
            summary_table.add_row("💸 Refund", f"[green]{refund:,.2f} {currency}[/green]", "[green]Available[/green]")

        # Additional information
        summary_table.add_row("", "", "")  # Separator

        # Scholarship status
        has_scholarship = bill_summary.get('has_current_scholarship_package', False)
        scholarship_status = "[green]✅ Yes[/green]" if has_scholarship else "[red]❌ No[/red]"
        summary_table.add_row("🎓 Scholarship Package", "", scholarship_status)

        # Payment statistics
        total_transactions = payment_summary.get('total_transactions', 0)
        latest_payment = payment_summary.get('latest_payment', 'N/A')

        summary_table.add_row("📈 Total Transactions", str(total_transactions), "")
        summary_table.add_row("📅 Latest Payment", latest_payment, "")

        console.print(summary_table)
        console.print()

    def _display_detailed_bills(self, student_bills: List[Dict[str, Any]]):
        """Display detailed bill breakdown"""
        if not student_bills:
            return

        console.print("[bold blue]📋 Detailed Bill Breakdown[/bold blue]")
        console.print()

        # Sort bills by academic year
        sorted_bills = sorted(student_bills,
                            key=lambda x: x.get('academic_period', {}).get('academic_year', ''),
                            reverse=True)

        for bill in sorted_bills:
            academic_period = bill.get('academic_period', {})
            academic_year = academic_period.get('academic_year', 'N/A')
            total_amount = bill.get('total_amount', 0.0)

            # Skip bills with zero or negative amounts for display
            if total_amount <= 0:
                continue

            bill_title = f"📄 Bill for {academic_year}"

            # Bill header
            bill_table = Table(title=bill_title,
                             title_style="bold green",
                             border_style="green",
                             show_header=True,
                             header_style="bold green")

            bill_table.add_column("Fee Item", style="white", width=35)
            bill_table.add_column("Amount (GHS)", style="cyan", width=15, justify="right")

            # Add compositions (fee breakdown)
            compositions = bill.get('compositions', [])
            total_calculated = 0.0

            for comp in compositions:
                item = comp.get('item', 'N/A')
                amount = comp.get('amount', 0.0)
                total_calculated += amount

                # Color code amounts
                if amount > 0:
                    amount_display = f"[green]{amount:,.2f}[/green]"
                else:
                    amount_display = f"[red]{amount:,.2f}[/red]"

                bill_table.add_row(item, amount_display)

            # Add total row
            bill_table.add_row("", "")  # Separator
            total_display = f"[bold yellow]{total_amount:,.2f}[/bold yellow]"
            bill_table.add_row("[bold]TOTAL", total_display)

            console.print(bill_table)
            console.print()

    def _display_transaction_history(self, transactions: Dict[str, Any]):
        """Display payment transaction history"""
        school_fees = transactions.get('school_fees', [])
        other_fees = transactions.get('other_fees', [])

        if not school_fees and not other_fees:
            return

        console.print("[bold blue]💳 Payment Transaction History[/bold blue]")
        console.print()

        # Display school fees transactions
        if school_fees:
            self._display_fee_transactions("🎓 School Fee Payments", school_fees)

        # Display other fees transactions
        if other_fees:
            self._display_fee_transactions("📋 Other Fee Payments", other_fees)

    def _display_fee_transactions(self, title: str, transactions: List[Dict[str, Any]]):
        """Display fee transactions table"""
        if not transactions:
            return

        # Sort transactions by payment date (most recent first)
        sorted_transactions = sorted(transactions,
                                   key=lambda x: x.get('payment_date', ''),
                                   reverse=True)

        # Create transactions table
        trans_table = Table(title=title,
                          title_style="bold blue",
                          border_style="blue",
                          show_header=True,
                          header_style="bold blue")

        trans_table.add_column("Date", style="cyan", width=18)
        trans_table.add_column("Amount", style="green", width=12, justify="right")
        trans_table.add_column("Academic Year", style="yellow", width=12)
        trans_table.add_column("Semester", style="white", width=8, justify="center")
        trans_table.add_column("Payment Method", style="white", width=25)
        trans_table.add_column("Receipt No.", style="blue", width=12)
        trans_table.add_column("Status", style="white", width=10)

        total_amount = 0.0

        for transaction in sorted_transactions:
            payment_date = transaction.get('payment_date', 'N/A')
            amount = transaction.get('amount', 0.0)
            academic_year = transaction.get('academic_year', 'N/A')
            semester = transaction.get('semester', 0)
            narration = transaction.get('narration', 'N/A')
            receipt_no = transaction.get('receipt_no', 'N/A')
            transaction_status = transaction.get('transaction_status', 0)

            total_amount += amount

            # Format date
            if payment_date != 'N/A':
                try:
                    # Extract just the date part
                    date_part = payment_date.split(' ')[0]
                    payment_date = date_part
                except:
                    pass

            # Format amount
            amount_display = f"{amount:,.2f}"

            # Format semester
            semester_display = f"Sem {semester}" if semester > 0 else "N/A"

            # Format status
            if transaction_status == 1:
                status_display = "[green]✅ Success[/green]"
            else:
                status_display = "[red]❌ Failed[/red]"

            # Clean up receipt number
            if receipt_no == 'None' or not receipt_no:
                receipt_no = "N/A"

            trans_table.add_row(
                payment_date,
                amount_display,
                academic_year,
                semester_display,
                narration,
                receipt_no,
                status_display
            )

        # Add total row
        trans_table.add_row("", "", "", "", "", "", "")  # Separator
        trans_table.add_row(
            "[bold]TOTAL",
            f"[bold green]{total_amount:,.2f}[/bold green]",
            "", "", "", "", ""
        )

        console.print(trans_table)
        console.print()

    def _course_assessment_menu(self):
        """Interactive course assessment interface"""
        console.print("\n")
        console.rule("[bold cyan]📝 Course Assessment[/bold cyan]", style="cyan")

        if not self.api_manager:
            console.print("[red]❌ API Manager not available[/red]")
            return

        # Show loading message
        with console.status("[bold cyan]Loading course assessment data...", spinner="dots"):
            assessment_data = self.api_manager.get_course_assessments()

        if not assessment_data.get('success'):
            error_msg = assessment_data.get('error', 'Unknown error occurred')
            console.print(f"[red]❌ Failed to load course assessment data: {error_msg}[/red]")
            return

        courses = assessment_data.get('courses', [])
        summary = assessment_data.get('summary', {})

        if not courses:
            console.print("[yellow]⚠️ No course assessments found[/yellow]")
            return

        # Display assessment summary
        self._display_assessment_summary(summary, assessment_data.get('categories_info', {}))

        # Assessment mode selection
        while True:
            console.print("\n")
            console.rule("[bold blue]📚 Course Assessment Options[/bold blue]", style="blue")

            # Display available courses
            course_table = Table(title="Available Courses for Assessment",
                               title_style="bold blue",
                               border_style="blue",
                               show_header=True,
                               header_style="bold blue")

            course_table.add_column("#", style="bold cyan", width=3, justify="center")
            course_table.add_column("Course Code", style="bold yellow", width=12)
            course_table.add_column("Course Name", style="white", width=35)
            course_table.add_column("Lecturer", style="green", width=25)
            course_table.add_column("Credits", style="cyan", width=8, justify="center")
            course_table.add_column("Status", style="white", width=15)

            pending_courses = []
            for i, course in enumerate(courses, 1):
                # Check if course has any existing ratings
                has_ratings = any(
                    question.get('score') is not None
                    for group in course.get('assessment_groups', [])
                    for question in group.get('questions', [])
                )

                status = "[green]✅ Rated[/green]" if has_ratings else "[yellow]⏳ Pending[/yellow]"
                if not has_ratings:
                    pending_courses.append(course)

                course_table.add_row(
                    str(i),
                    course.get('code', 'N/A'),
                    course.get('name', 'N/A'),
                    course.get('lecturer', 'N/A'),
                    str(course.get('credit', 0)),
                    status
                )

            console.print(course_table)

            # Assessment mode options
            console.print("\n[bold cyan]Assessment Options:[/bold cyan]")
            console.print("• Enter 'auto' for 🤖 Automated Assessment (All courses at once)")
            console.print("• Enter 'manual' for 👤 Manual Assessment (Course by course)")
            console.print("• Enter course number (1-{}) for individual assessment".format(len(courses)))
            console.print("• Enter 'v' to view assessment summary")
            console.print("• Enter 'b' to go back to main menu")

            choice = Prompt.ask("\n[bold cyan]Select option[/bold cyan]", default="b").strip().lower()

            if choice == 'b':
                break
            elif choice == 'v':
                self._display_categories_breakdown(assessment_data.get('categories_breakdown', {}))
                continue
            elif choice == 'auto':
                if pending_courses:
                    self._automated_course_assessment(pending_courses)
                else:
                    console.print("[yellow]⚠️ All courses have already been assessed[/yellow]")
                    self._pause()
                continue
            elif choice == 'manual':
                self._manual_assessment_mode(courses)
                continue

            try:
                course_index = int(choice) - 1
                if 0 <= course_index < len(courses):
                    selected_course = courses[course_index]
                    self._interactive_course_assessment(selected_course)
                else:
                    console.print("[red]❌ Invalid course number[/red]")
            except ValueError:
                console.print("[red]❌ Invalid input. Please enter a valid option[/red]")

    def _interactive_course_assessment(self, course: Dict[str, Any]):
        """Interactive assessment for a single course"""
        course_code = course.get('code', 'N/A')
        course_name = course.get('name', 'N/A')
        lecturer = course.get('lecturer', 'N/A')
        course_id = course.get('id')

        console.print("\n")
        console.rule(f"[bold magenta]📚 Assessing: {course_code} - {course_name}[/bold magenta]", style="magenta")

        # Display course info
        course_info_table = Table(border_style="magenta", show_header=False)
        course_info_table.add_column("Field", style="bold magenta", width=15)
        course_info_table.add_column("Value", style="white", width=40)

        course_info_table.add_row("👨‍🏫 Lecturer:", lecturer)
        course_info_table.add_row("🎯 Credits:", str(course.get('credit', 0)))
        course_info_table.add_row("🆔 Course ID:", str(course_id))

        console.print(course_info_table)
        console.print()

        # Collect ratings for all questions
        ratings = {}
        total_questions = 0

        # Process each assessment group/category
        for group in course.get('assessment_groups', []):
            category_code = group.get('category_code', 'N/A')
            category_name = group.get('name', 'N/A')
            questions = group.get('questions', [])

            if not questions:
                continue

            console.print(f"\n[bold yellow]📂 Category {category_code}: {category_name}[/bold yellow]")

            # Category explanation
            category_explanations = {
                'A': "🎯 Evaluates course objectives, content presentation, and assessment methods",
                'B': "📚 Assesses teaching methods, clarity, pace, and lecturer knowledge",
                'C': "👨‍🏫 Reviews lecturer's appearance, punctuality, and classroom management",
                'D': "📝 Evaluates assignments, feedback, tutorials, and learning experience"
            }

            if category_code in category_explanations:
                console.print(f"[dim]{category_explanations[category_code]}[/dim]")

            console.print()

            # Rate each question in the category
            for question in questions:
                question_id = question.get('id')
                description = question.get('description', 'N/A')
                current_score = question.get('score')
                question_number = question.get('number', 0)

                total_questions += 1

                # Display question
                console.print(f"[bold cyan]Question {question_number}:[/bold cyan] {description}")

                # Show current rating if exists
                if current_score is not None:
                    console.print(f"[green]Current Rating: {current_score}/5[/green]")

                # Rating options
                console.print("[dim]Rating Scale: 1=Very Poor, 2=Poor, 3=Average, 4=Good, 5=V. Good[/dim]")

                # Get rating from user
                while True:
                    try:
                        rating_input = Prompt.ask(
                            f"[bold cyan]Rate this question (1-5)[/bold cyan]",
                            default=str(current_score) if current_score else "3"
                        )

                        rating = int(rating_input)
                        if 1 <= rating <= 5:
                            ratings[question_id] = rating

                            # Show confirmation
                            rating_labels = {1: "Very Poor", 2: "Poor", 3: "Average", 4: "Good", 5: "V. Good"}
                            console.print(f"[green]✅ Rated: {rating}/5 ({rating_labels[rating]})[/green]")
                            break
                        else:
                            console.print("[red]❌ Please enter a number between 1 and 5[/red]")
                    except ValueError:
                        console.print("[red]❌ Please enter a valid number[/red]")

                console.print()

        # Get optional remarks
        console.print("[bold cyan]📝 Additional Comments (Optional):[/bold cyan]")
        remarks = Prompt.ask(
            "[dim]Enter any additional comments about this course/lecturer[/dim]",
            default=""
        )

        # Show assessment summary
        console.print("\n")
        console.rule("[bold green]📊 Assessment Summary[/bold green]", style="green")

        summary_table = Table(border_style="green", show_header=True, header_style="bold green")
        summary_table.add_column("Metric", style="bold green", width=20)
        summary_table.add_column("Value", style="white", width=15)

        summary_table.add_row("📚 Course", f"{course_code}")
        summary_table.add_row("❓ Questions Rated", f"{len(ratings)}/{total_questions}")
        summary_table.add_row("📊 Average Rating", f"{sum(ratings.values())/len(ratings):.1f}/5.0" if ratings else "N/A")
        summary_table.add_row("💬 Comments", "Yes" if remarks.strip() else "No")

        console.print(summary_table)

        # Confirm submission
        console.print("\n[bold yellow]⚠️  Please review your assessment before submitting[/bold yellow]")

        if len(ratings) < total_questions:
            console.print(f"[red]❌ Warning: {total_questions - len(ratings)} questions are not rated[/red]")
            console.print("[red]All questions must be rated before submission[/red]")
            self._pause()
            return

        confirm = Prompt.ask(
            "\n[bold cyan]Submit this assessment?[/bold cyan]",
            choices=["y", "n"],
            default="y"
        )

        if confirm.lower() == 'y':
            # Submit assessment
            with console.status("[bold cyan]Submitting assessment...", spinner="dots"):
                result = self.api_manager.submit_course_assessment(course_id, ratings, remarks)

            if result.get('success'):
                console.print(f"\n[bold green]✅ Assessment submitted successfully![/bold green]")
                console.print(f"[green]Course: {result.get('course_code', 'N/A')} - {result.get('course_name', 'N/A')}[/green]")
                console.print(f"[green]Questions Rated: {result.get('total_questions', 0)}[/green]")
            else:
                console.print(f"\n[bold red]❌ Failed to submit assessment[/bold red]")
                console.print(f"[red]Error: {result.get('error', 'Unknown error')}[/red]")

                # Show validation details if available
                validation = result.get('validation', {})
                if validation:
                    missing_questions = validation.get('missing_questions', [])
                    if missing_questions:
                        console.print(f"\n[yellow]Missing ratings for {len(missing_questions)} questions:[/yellow]")
                        for q in missing_questions[:5]:  # Show first 5
                            console.print(f"  • Q{q.get('number', 0)}: {q.get('description', 'N/A')}")
        else:
            console.print("[yellow]Assessment cancelled[/yellow]")

        self._pause()

    def _automated_course_assessment(self, pending_courses: List[Dict[str, Any]]):
        """Automated assessment for all pending courses"""
        import random

        console.print("\n")
        console.rule("[bold green]🤖 Automated Course Assessment[/bold green]", style="green")

        console.print("[bold cyan]📋 Automated Assessment Information:[/bold cyan]")
        console.print("• 🎯 Rating Range: 3-5 (Average to Very Good)")
        console.print("• 🎲 Random Selection: Each question gets a random rating")
        console.print("• ⚡ Speed: All courses assessed instantly")
        console.print("• 📝 Comments: Optional automated comments")

        console.print(f"\n[bold yellow]📚 Courses to be assessed: {len(pending_courses)}[/bold yellow]")

        # Show courses that will be assessed
        for i, course in enumerate(pending_courses, 1):
            console.print(f"  {i}. {course.get('code', 'N/A')} - {course.get('name', 'N/A')}")

        # Confirm automated assessment
        confirm = Prompt.ask(
            "\n[bold cyan]Proceed with automated assessment?[/bold cyan]",
            choices=["y", "n"],
            default="y"
        )

        if confirm.lower() != 'y':
            console.print("[yellow]Automated assessment cancelled[/yellow]")
            return

        # Ask for optional general comment
        general_comment = Prompt.ask(
            "\n[bold cyan]Enter general comment for all courses (optional)[/bold cyan]",
            default=""
        ).strip()

        # Perform automated assessment
        all_assessments = {}
        total_questions = 0

        console.print("\n")
        console.rule("[bold blue]🎲 Generating Random Ratings[/bold blue]", style="blue")

        with console.status("[bold green]Generating automated assessments...", spinner="dots"):
            for course in pending_courses:
                course_id = course.get('id')
                course_code = course.get('code', 'N/A')

                ratings = {}
                course_questions = 0

                # Generate random ratings for all questions
                for group in course.get('assessment_groups', []):
                    for question in group.get('questions', []):
                        question_id = question.get('id')
                        if question_id:
                            # Random rating between 3-5 (Average, Good, Very Good)
                            rating = random.choice([3, 4, 5])
                            ratings[question_id] = rating
                            course_questions += 1
                            total_questions += 1

                all_assessments[course_id] = {
                    'course': course,
                    'ratings': ratings,
                    'questions_count': course_questions
                }

        # Display assessment summary
        console.print("\n")
        console.rule("[bold green]📊 Automated Assessment Summary[/bold green]", style="green")

        summary_table = Table(title="Assessment Generation Summary",
                             title_style="bold green",
                             border_style="green",
                             show_header=True,
                             header_style="bold green")

        summary_table.add_column("Course", style="bold yellow", width=12)
        summary_table.add_column("Course Name", style="white", width=30)
        summary_table.add_column("Questions", style="cyan", width=10, justify="center")
        summary_table.add_column("Avg Rating", style="green", width=12, justify="center")
        summary_table.add_column("Status", style="white", width=15)

        for course_id, assessment in all_assessments.items():
            course = assessment['course']
            ratings = assessment['ratings']
            avg_rating = sum(ratings.values()) / len(ratings) if ratings else 0

            summary_table.add_row(
                course.get('code', 'N/A'),
                course.get('name', 'N/A')[:30] + "..." if len(course.get('name', '')) > 30 else course.get('name', 'N/A'),
                str(assessment['questions_count']),
                f"{avg_rating:.1f}/5.0",
                "[green]✅ Ready[/green]"
            )

        console.print(summary_table)

        # Overall statistics
        console.print(f"\n[bold cyan]📈 Overall Statistics:[/bold cyan]")
        console.print(f"• 📚 Total Courses: {len(pending_courses)}")
        console.print(f"• ❓ Total Questions: {total_questions}")
        console.print(f"• 💬 General Comment: {'Yes' if general_comment else 'No'}")

        # Final confirmation before submission
        console.print("\n[bold yellow]⚠️  Final Review Before Submission[/bold yellow]")
        console.print("[dim]All ratings have been randomly generated between 3-5 (Average to Very Good)[/dim]")

        final_confirm = Prompt.ask(
            "\n[bold red]Submit ALL automated assessments to UMAT servers?[/bold red]",
            choices=["y", "n"],
            default="n"
        )

        if final_confirm.lower() != 'y':
            console.print("[yellow]Assessment submission cancelled[/yellow]")
            return

        # Submit all assessments at once (matches web interface behavior)
        console.print("\n")
        console.rule("[bold blue]📤 Submitting All Assessments[/bold blue]", style="blue")

        # Prepare assessments for bulk submission
        bulk_assessments = []
        for course_id, assessment in all_assessments.items():
            bulk_assessments.append({
                'course_id': course_id,
                'ratings': assessment['ratings']
            })

        console.print(f"[bold cyan]📦 Submitting {len(bulk_assessments)} courses in one request...[/bold cyan]")

        with console.status("[bold cyan]Submitting all assessments to UMAT servers...", spinner="dots"):
            result = self.api_manager.submit_all_course_assessments(bulk_assessments, general_comment)

        if result.get('success'):
            console.print(f"[green]✅ All assessments submitted successfully![/green]")
            successful_submissions = result.get('courses_submitted', len(bulk_assessments))
            failed_submissions = 0
        else:
            console.print(f"[red]❌ Bulk submission failed: {result.get('error', 'Unknown error')}[/red]")
            successful_submissions = 0
            failed_submissions = len(bulk_assessments)

        # Final results
        console.print("\n")
        console.rule("[bold green]🎉 Automated Assessment Complete[/bold green]", style="green")

        results_table = Table(title="Submission Results",
                             title_style="bold green",
                             border_style="green",
                             show_header=True,
                             header_style="bold green")

        results_table.add_column("Metric", style="bold green", width=20)
        results_table.add_column("Count", style="white", width=10, justify="center")
        results_table.add_column("Percentage", style="cyan", width=15, justify="center")

        total_courses = len(pending_courses)
        success_rate = (successful_submissions / total_courses * 100) if total_courses > 0 else 0

        results_table.add_row("✅ Successful", str(successful_submissions), f"{success_rate:.1f}%")
        results_table.add_row("❌ Failed", str(failed_submissions), f"{100-success_rate:.1f}%")
        results_table.add_row("📚 Total Courses", str(total_courses), "100.0%")
        results_table.add_row("❓ Total Questions", str(total_questions), "-")

        console.print(results_table)

        if successful_submissions > 0:
            console.print(f"\n[bold green]🎉 Successfully submitted {successful_submissions} course assessments![/bold green]")

        if failed_submissions > 0:
            console.print(f"\n[bold red]⚠️  {failed_submissions} assessments failed to submit. Please try manual assessment for failed courses.[/bold red]")

        self._pause()

    def _manual_assessment_mode(self, courses: List[Dict[str, Any]]):
        """Manual assessment mode - course by course"""
        while True:
            console.print("\n")
            console.rule("[bold blue]👤 Manual Assessment Mode[/bold blue]", style="blue")

            # Display available courses
            course_table = Table(title="Select Course for Manual Assessment",
                               title_style="bold blue",
                               border_style="blue",
                               show_header=True,
                               header_style="bold blue")

            course_table.add_column("#", style="bold cyan", width=3, justify="center")
            course_table.add_column("Course Code", style="bold yellow", width=12)
            course_table.add_column("Course Name", style="white", width=35)
            course_table.add_column("Lecturer", style="green", width=25)
            course_table.add_column("Credits", style="cyan", width=8, justify="center")
            course_table.add_column("Status", style="white", width=15)

            for i, course in enumerate(courses, 1):
                # Check if course has any existing ratings
                has_ratings = any(
                    question.get('score') is not None
                    for group in course.get('assessment_groups', [])
                    for question in group.get('questions', [])
                )

                status = "[green]✅ Rated[/green]" if has_ratings else "[yellow]⏳ Pending[/yellow]"

                course_table.add_row(
                    str(i),
                    course.get('code', 'N/A'),
                    course.get('name', 'N/A'),
                    course.get('lecturer', 'N/A'),
                    str(course.get('credit', 0)),
                    status
                )

            console.print(course_table)

            # Course selection menu
            console.print("\n[bold cyan]Manual Assessment Options:[/bold cyan]")
            console.print("• Enter course number (1-{}) to assess manually".format(len(courses)))
            console.print("• Enter 'b' to go back to assessment options")

            choice = Prompt.ask("\n[bold cyan]Select course[/bold cyan]", default="b").strip().lower()

            if choice == 'b':
                break

            try:
                course_index = int(choice) - 1
                if 0 <= course_index < len(courses):
                    selected_course = courses[course_index]
                    self._interactive_course_assessment(selected_course)
                else:
                    console.print("[red]❌ Invalid course number[/red]")
            except ValueError:
                console.print("[red]❌ Invalid input. Please enter a number or 'b' to go back[/red]")

    def _display_assessment_summary(self, summary: Dict[str, Any], categories_info: Dict[str, str]):
        """Display course assessment summary"""
        if not summary:
            return

        # Create summary table
        summary_table = Table(title="📝 Course Assessment Summary",
                            title_style="bold cyan",
                            border_style="cyan",
                            show_header=True,
                            header_style="bold cyan")

        summary_table.add_column("Metric", style="bold cyan", width=25)
        summary_table.add_column("Value", style="white", width=20)

        summary_table.add_row("📚 Total Courses", str(summary.get('total_courses', 0)))
        summary_table.add_row("❓ Total Questions", str(summary.get('total_questions', 0)))
        summary_table.add_row("🎯 Total Credits", str(summary.get('total_credits', 0)))
        summary_table.add_row("👨‍🏫 Total Lecturers", str(len(summary.get('lecturers', []))))
        summary_table.add_row("📋 Assessment Categories", str(len(summary.get('assessment_categories', []))))

        console.print(summary_table)
        console.print()

        # Display lecturers and their courses
        courses_by_lecturer = summary.get('courses_by_lecturer', {})
        if courses_by_lecturer:
            lecturers_table = Table(title="👨‍🏫 Lecturers and Their Courses",
                                  title_style="bold blue",
                                  border_style="blue",
                                  show_header=True,
                                  header_style="bold blue")

            lecturers_table.add_column("Lecturer", style="bold yellow", width=30)
            lecturers_table.add_column("Courses", style="white", width=40)
            lecturers_table.add_column("Credits", style="cyan", width=8, justify="center")

            for lecturer, courses in courses_by_lecturer.items():
                course_list = []
                total_credits = 0
                for course in courses:
                    course_list.append(f"{course['code']} ({course['credit']} cr)")
                    total_credits += course['credit']

                courses_display = "\n".join(course_list)
                lecturers_table.add_row(lecturer, courses_display, str(total_credits))

            console.print(lecturers_table)
            console.print()

    def _display_categories_breakdown(self, categories_breakdown: Dict[str, Dict[str, Any]]):
        """Display assessment categories breakdown"""
        if not categories_breakdown:
            return

        console.print("[bold blue]📋 Assessment Categories Breakdown[/bold blue]")
        console.print()

        # Sort categories by code
        sorted_categories = sorted(categories_breakdown.items())

        for category_code, category_data in sorted_categories:
            category_name = category_data.get('name', 'N/A')
            total_questions = category_data.get('total_questions', 0)
            courses_count = category_data.get('courses_count', 0)

            # Create category table
            category_table = Table(title=f"📂 Category {category_code}: {category_name}",
                                 title_style="bold green",
                                 border_style="green",
                                 show_header=True,
                                 header_style="bold green")

            category_table.add_column("Metric", style="bold green", width=20)
            category_table.add_column("Value", style="white", width=15)

            category_table.add_row("❓ Total Questions", str(total_questions))
            category_table.add_row("📚 Courses Count", str(courses_count))
            category_table.add_row("📊 Avg Questions/Course", f"{total_questions/courses_count:.1f}" if courses_count > 0 else "0")

            console.print(category_table)

            # Display sample questions
            sample_questions = category_data.get('sample_questions', [])
            if sample_questions:
                console.print(f"\n[bold green]Sample Questions for Category {category_code}:[/bold green]")
                for i, question in enumerate(sample_questions, 1):
                    console.print(f"  {i}. {question}")

            console.print()

    def _display_course_assessments(self, formatted_courses: List[Dict[str, Any]]):
        """Display detailed course assessments"""
        if not formatted_courses:
            return

        console.print("[bold blue]📝 Course Assessment Details[/bold blue]")
        console.print()

        for course in formatted_courses:
            self._display_single_course_assessment(course)
            console.print()

    def _display_single_course_assessment(self, course: Dict[str, Any]):
        """Display assessment for a single course"""
        course_code = course.get('code', 'N/A')
        course_name = course.get('name', 'N/A')
        lecturer = course.get('lecturer', 'N/A')
        credit = course.get('credit', 0)
        total_questions = course.get('total_questions', 0)

        # Course header
        course_title = f"📚 {course_code}: {course_name}"

        # Course info table
        course_info_table = Table(title=course_title,
                                title_style="bold magenta",
                                border_style="magenta",
                                show_header=True,
                                header_style="bold magenta")

        course_info_table.add_column("Information", style="bold magenta", width=20)
        course_info_table.add_column("Details", style="white", width=30)

        course_info_table.add_row("👨‍🏫 Lecturer", lecturer)
        course_info_table.add_row("🎯 Credit Hours", str(credit))
        course_info_table.add_row("❓ Total Questions", str(total_questions))
        course_info_table.add_row("📋 Categories", str(len(course.get('categories', []))))

        console.print(course_info_table)

        # Display categories and questions
        categories = course.get('categories', [])
        for category in categories:
            self._display_assessment_category(category, course_code)

    def _display_assessment_category(self, category: Dict[str, Any], course_code: str):
        """Display assessment category with questions"""
        category_code = category.get('code', 'N/A')
        category_name = category.get('name', 'N/A')
        question_count = category.get('question_count', 0)

        console.print(f"\n[bold yellow]📂 Category {category_code}: {category_name} ({question_count} questions)[/bold yellow]")

        # Questions table
        questions_table = Table(border_style="yellow",
                              show_header=True,
                              header_style="bold yellow")

        questions_table.add_column("Q#", style="bold cyan", width=4, justify="center")
        questions_table.add_column("Question", style="white", width=50)
        questions_table.add_column("Current Score", style="green", width=12, justify="center")
        questions_table.add_column("Rating Scale", style="blue", width=25)

        questions = category.get('questions', [])
        for question in questions:
            question_number = question.get('number', 0)
            description = question.get('description', 'N/A')
            current_score = question.get('current_score')

            # Format current score
            if current_score is not None:
                score_display = f"[green]{current_score}[/green]"
            else:
                score_display = "[dim]Not Rated[/dim]"

            # Format rating scale
            answer_options = question.get('answer_options', [])
            if answer_options:
                scale_parts = []
                for option in answer_options:
                    scale_parts.append(f"{option['value']}={option['label']}")
                rating_scale = ", ".join(scale_parts)
            else:
                rating_scale = "N/A"

            questions_table.add_row(
                str(question_number),
                description,
                score_display,
                rating_scale
            )

        console.print(questions_table)

        # Category explanation
        category_explanations = {
            'A': "🎯 Evaluates course objectives, content presentation, and assessment methods",
            'B': "📚 Assesses teaching methods, clarity, pace, and lecturer knowledge",
            'C': "👨‍🏫 Reviews lecturer's appearance, punctuality, and classroom management",
            'D': "📝 Evaluates assignments, feedback, tutorials, and learning experience"
        }

        if category_code in category_explanations:
            console.print(f"[dim]{category_explanations[category_code]}[/dim]")

    def _pause(self):
        """Pause for user input"""
        try:
            Prompt.ask("\n[dim]Press Enter to continue[/dim]", default="")
        except KeyboardInterrupt:
            pass

    def logout(self):
        """Logout user"""
        if self.api_manager:
            self.api_manager.logout()

        console.print("\n[green]👋 Logged out successfully. Thank you for using UMAT Portal![/green]")

def main():
    """Main portal entry point"""
    portal = StudentPortal()

    try:
        portal.show_banner()

        if portal.authenticate():
            portal.show_dashboard()
        else:
            console.print("\n[red]❌ Authentication failed. Please try again later.[/red]")

    except KeyboardInterrupt:
        console.print("\n[yellow]👋 Goodbye![/yellow]")
    except Exception as e:
        console.print(f"\n[red]❌ An unexpected error occurred: {str(e)}[/red]")
    finally:
        portal.logout()

if __name__ == "__main__":
    main()