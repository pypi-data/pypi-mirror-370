"""
UMAT Student Email Activation
Generates student email credentials based on UMAT standard
"""

from rich.console import Console
from rich.panel import Panel

console = Console()


class StudentEmailActivator:
    """Generate UMAT student email credentials"""

    def generate_email_credentials(self, vle_credentials):
        """Generate email credentials from VLE credentials"""
        # Create initials from first name and other names
        initials = vle_credentials['first_name'][0].lower()
        if vle_credentials['other_names']:
            # Take first letter of each other name
            other_initials = ''.join([name[0].lower() for name in vle_credentials['other_names'].split()])
            initials += other_initials

        # Generate username (email local part): initials + surname + last4digits
        username_base = f"{initials}{vle_credentials['surname'].lower()}{vle_credentials['last4_digits']}"

        # Generate email
        email = f"{vle_credentials['dept_code']}-{username_base}@st.umat.edu.gh"

        return {
            'email': email,
            'password': vle_credentials['password'],  # Same password as VLE
            'initials': initials,
            'username_base': username_base
        }

    def display_email_credentials(self, vle_credentials, email_credentials):
        """Display email activation credentials"""
        email_panel = Panel(
            f"""[bold cyan]STUDENT EMAIL ACTIVATION[/bold cyan]

[bold]Department Code:[/bold] {vle_credentials['dept_code'].upper()}
[bold]First Name:[/bold] {vle_credentials['first_name'].upper()}
[bold]Other Name(s):[/bold] {vle_credentials['other_names'].upper() if vle_credentials['other_names'] else 'N/A'}
[bold]Surname:[/bold] {vle_credentials['surname'].upper()}
[bold]Reference Number:[/bold] {vle_credentials['username']}

[bold green]Email ID:[/bold green] {email_credentials['email']}
[bold green]Password:[/bold green] {email_credentials['password']}

[bold blue]Gmail URL:[/bold blue] https://mail.google.com/""",
            title="📧 Email Credentials",
            border_style="blue",
            padding=(1, 2)
        )

        console.print()
        console.print(email_panel)

        # Additional information
        info_panel = Panel(
            f"""[bold yellow]📋 CREDENTIAL GENERATION DETAILS[/bold yellow]

[dim]• Initials extracted: [/dim][cyan]{email_credentials['initials']}[/cyan]
[dim]• Username base: [/dim][cyan]{email_credentials['username_base']}[/cyan]
[dim]• Last 4 digits: [/dim][cyan]{vle_credentials['last4_digits']}[/cyan]
[dim]• Department code: [/dim][cyan]{vle_credentials['dept_code']}[/cyan]

[bold red]⚠️ IMPORTANT NOTES:[/bold red]
• Use your [bold]Reference Number[/bold] as VLE username
• Both VLE and Email use the [bold]same password[/bold]
• Email format: [cyan]{vle_credentials['dept_code']}-{email_credentials['username_base']}@st.umat.edu.gh[/cyan]
• Password format: [cyan]{vle_credentials['surname'].lower()}{vle_credentials['last4_digits']}[/cyan]""",
            title="ℹ️ Information",
            border_style="yellow",
            padding=(1, 2)
        )

        console.print()
        console.print(info_panel)

        return email_credentials