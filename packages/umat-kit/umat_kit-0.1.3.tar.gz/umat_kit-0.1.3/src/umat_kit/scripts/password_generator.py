import re
import random
import string
from typing import List

from rich.console import Console
from rich.prompt import Prompt, IntPrompt
from rich.panel import Panel
from rich.table import Table

console = Console()


class PasswordGenerator:
    """Password generator class for creating secure passwords"""

    def __init__(self):
        self.lowercase = string.ascii_lowercase
        self.uppercase = string.ascii_uppercase
        self.digits = string.digits
        self.symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?"

    def generate_password(self, length=12, include_symbols=True, include_numbers=True, include_uppercase=True):
        """Generate a random password with specified criteria"""
        if length < 4:
            length = 4

        # Build character set
        chars = self.lowercase
        required_chars = [random.choice(self.lowercase)]

        if include_uppercase:
            chars += self.uppercase
            required_chars.append(random.choice(self.uppercase))

        if include_numbers:
            chars += self.digits
            required_chars.append(random.choice(self.digits))

        if include_symbols:
            chars += self.symbols
            required_chars.append(random.choice(self.symbols))

        # Fill remaining length with random characters
        remaining_length = length - len(required_chars)
        password_chars = required_chars + [random.choice(chars) for _ in range(remaining_length)]

        # Shuffle to avoid predictable patterns
        random.shuffle(password_chars)

        return ''.join(password_chars)

    def analyze_password_strength(self, password):
        """Analyze password strength and return a description"""
        score = 0
        feedback = []

        # Length check
        if len(password) >= 12:
            score += 2
        elif len(password) >= 8:
            score += 1
        else:
            feedback.append("too short")

        # Character variety checks
        if any(c.islower() for c in password):
            score += 1
        else:
            feedback.append("needs lowercase")

        if any(c.isupper() for c in password):
            score += 1
        else:
            feedback.append("needs uppercase")

        if any(c.isdigit() for c in password):
            score += 1
        else:
            feedback.append("needs numbers")

        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            score += 1
        else:
            feedback.append("needs symbols")

        # Determine strength
        if score >= 6:
            return "[bold green]Very Strong[/bold green] 💪"
        elif score >= 4:
            return "[bold yellow]Strong[/bold yellow] 👍"
        elif score >= 2:
            return "[bold orange]Moderate[/bold orange] ⚠️"
        else:
            return f"[bold red]Weak[/bold red] ❌ ({', '.join(feedback)})"


def parse_email_parts(email: str) -> tuple[str, str]:
    """Return (letters_part, last4_digits) from institutional email local part.

    Accepted formats (examples):
      gm-tmarthur7120@st.umat.edu.gh -> letters: tmarthur, last4: 7120
      cse-jdoe1234@st.umat.edu.gh -> letters: jdoe, last4: 1234
      jdoe1234@domain -> letters: jdoe, last4: 1234
    """
    if '@' not in email:
        raise ValueError('Invalid email: missing @')
    local = email.split('@', 1)[0]
    # Drop department prefix if present (e.g., gm-)
    if '-' in local:
        local = local.split('-', 1)[1]

    m = re.match(r'([A-Za-z]+?)(\d{2,})$', local)
    if not m:
        raise ValueError('Email local part must end with digits (at least 2).')

    letters = m.group(1)
    digits = m.group(2)
    last4 = digits[-4:] if len(digits) >= 4 else digits
    return letters, last4


def propose_surname_options(letters: str) -> List[str]:
    """Heuristically propose surname candidates from letters (initials + surname)."""
    candidates = []
    # Full letters (covers cases without initials)
    if len(letters) >= 3:
        candidates.append(letters)
    # Drop 1 or 2 leading initials (common pattern: first + other initials)
    if len(letters) - 1 >= 3:
        candidates.append(letters[1:])
    if len(letters) - 2 >= 3:
        candidates.append(letters[2:])
    # Also try dropping 3 if very long initials chain
    if len(letters) - 3 >= 3:
        candidates.append(letters[3:])
    # Deduplicate while preserving order
    seen = set()
    unique = []
    for c in candidates:
        lc = c.lower()
        if lc not in seen:
            seen.add(lc)
            unique.append(lc)
    return unique


def main() -> None:
    console.print(Panel.fit("Student Password Generator", style="bold cyan"))

    email = Prompt.ask("Enter your student email", default="gm-tmarthur7120@st.umat.edu.gh")
    try:
        letters, last4 = parse_email_parts(email.strip())
    except ValueError as e:
        console.print(f"[red]Error:[/] {e}")
        return

    options = propose_surname_options(letters)

    if not options:
        console.print("[yellow]Could not infer surname from email.\nPlease enter your surname (letters only).[/]")
        surname = Prompt.ask("Surname").strip().lower()
    else:
        table = Table(title="Choose your surname", show_lines=True)
        table.add_column("Option", justify="center")
        table.add_column("Surname", justify="left")
        for idx, s in enumerate(options, start=1):
            table.add_row(str(idx), s)
        table.add_row("0", "Enter manually")
        console.print(table)
        choice = IntPrompt.ask("Select option", default=1)
        if choice == 0:
            surname = Prompt.ask("Enter surname").strip().lower()
        else:
            if 1 <= choice <= len(options):
                surname = options[choice - 1].strip().lower()
            else:
                console.print("[yellow]Invalid choice; defaulting to option 1[/]")
                surname = options[0].strip().lower()

    if not re.fullmatch(r'[a-z]+', surname):
        console.print("[red]Surname must contain only letters.[/]")
        return

    password = f"{surname}{last4}".lower()

    console.print()
    info = Table(title="Generated Credentials", show_header=False)
    info.add_column("Key", style="bold")
    info.add_column("Value")
    info.add_row("Email", email)
    info.add_row("Derived surname", surname)
    info.add_row("Last 4 digits", last4)
    info.add_row("Password", f"[bold green]{password}[/]")
    info.add_row("Gmail URL", "https://mail.google.com/")
    info.add_row("VLE URL", "https://vle.umat.edu.gh")
    console.print(info)

    console.print(Panel.fit("Use this password for both your student email and VLE (Username is your Reference Number).", style="cyan"))


if __name__ == '__main__':
    main()