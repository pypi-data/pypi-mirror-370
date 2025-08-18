"""
UMAT VLE Login Generator
Generates VLE credentials based on UMAT standard
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt

console = Console()


class VLELoginGenerator:
    """Generate UMAT VLE login credentials"""

    def __init__(self):
        self.dept_codes = {
            'Geomatic Engineering': 'gm',
            'Computing and Data Analytics': 'cda',
            'Computer Science and Engineering': 'cse',
            'Electrical and Electronic Engineering': 'eee',
            'Mechanical Engineering': 'me',
            'Civil Engineering': 'ce',
            'Chemical Engineering': 'che',
            'Mineral Engineering': 'min',
            'Geological Engineering': 'ge',
            'Environmental Engineering': 'env',
            'Petroleum Engineering': 'pe',
            'Materials Engineering': 'mat'
        }

    def parse_full_name(self, full_name):
        """Parse UMAT full name format: 'SURNAME, FirstName OtherNames (Title)'"""
        try:
            # Remove title if present
            if '(' in full_name:
                full_name = full_name.split('(')[0].strip()

            # Split by comma
            if ',' not in full_name:
                return None

            parts = full_name.split(',', 1)
            surname = parts[0].strip()

            # Split first name and other names
            name_part = parts[1].strip()
            name_words = name_part.split()

            if not name_words:
                return None

            first_name = name_words[0]
            other_names = ' '.join(name_words[1:]) if len(name_words) > 1 else ''

            return surname, first_name, other_names

        except Exception:
            return None

    def get_department_code(self, department):
        """Get department code based on department name"""
        # Try to find exact match first
        for dept_name, code in self.dept_codes.items():
            if dept_name.lower() in department.lower():
                return code

        # If no match found, ask user to select
        console.print(f"\n[yellow]Could not auto-detect department code for: {department}[/yellow]")
        console.print("[cyan]Please select your department:[/cyan]")

        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Option", style="cyan", width=8)
        table.add_column("Department", style="white")
        table.add_column("Code", style="green")

        dept_list = list(self.dept_codes.items())
        for i, (dept_name, code) in enumerate(dept_list, 1):
            table.add_row(str(i), dept_name, code)

        console.print(table)

        try:
            choice = int(Prompt.ask("Select department", default="1"))
            if 1 <= choice <= len(dept_list):
                return dept_list[choice - 1][1]
            else:
                return 'gm'  # Default fallback
        except:
            return 'gm'  # Default fallback

    def generate_credentials(self, full_name, student_number, department):
        """Generate VLE credentials using UMAT standard"""
        # Parse name
        name_parts = self.parse_full_name(full_name)
        if not name_parts:
            raise ValueError("Could not parse name format")

        surname, first_name, other_names = name_parts

        # Get department code
        dept_code = self.get_department_code(department)

        # Get last 4 digits of student number
        last4_digits = student_number[-4:] if len(student_number) >= 4 else student_number

        # Generate password: surname + last4digits (all lowercase)
        password = f"{surname.lower()}{last4_digits}"

        return {
            'username': student_number,  # VLE username is the reference number
            'password': password,
            'surname': surname,
            'first_name': first_name,
            'other_names': other_names,
            'dept_code': dept_code,
            'last4_digits': last4_digits
        }

    def display_credentials(self, credentials):
        """Display VLE credentials"""
        vle_panel = Panel(
            f"""[bold cyan]VLE LOGIN CREDENTIALS[/bold cyan]

[bold]Department Code:[/bold] {credentials['dept_code'].upper()}
[bold]First Name:[/bold] {credentials['first_name'].upper()}
[bold]Other Name(s):[/bold] {credentials['other_names'].upper() if credentials['other_names'] else 'N/A'}
[bold]Surname:[/bold] {credentials['surname'].upper()}
[bold]Reference Number:[/bold] {credentials['username']}

[bold green]Username:[/bold green] {credentials['username']}
[bold green]Password:[/bold green] {credentials['password']}

[bold blue]VLE URL:[/bold blue] https://vle.umat.edu.gh""",
            title="🎓 VLE Credentials",
            border_style="green",
            padding=(1, 2)
        )

        console.print(vle_panel)
        return credentials