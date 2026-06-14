"""Display module — Rich terminal output for the email security pipeline.

All output goes through Rich (no bare print calls in other modules).
Functions are module-level, not class-based — import and call directly.
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from .models import Category, ClassificationResult, EmailMessage, Priority

console = Console()

# ---------------------------------------------------------------------------
# Category → colour mapping
# ---------------------------------------------------------------------------
_CATEGORY_STYLES: dict[Category, str] = {
    Category.SQL_INJECTION: "bold red",
    Category.XSS: "bold red",
    Category.VULNERABILITY: "bold yellow",
    Category.BUG_REPORT: "yellow",
    Category.CRITICAL_ALERT: "bold red on white",
    Category.PHISHING: "bold magenta",
    Category.GENERAL_INQUIRY: "green",
    Category.SPAM: "dim",
}

# Priority → colour mapping
_PRIORITY_STYLES: dict[Priority, str] = {
    Priority.CRITICAL: "bold red",
    Priority.HIGH: "bold yellow",
    Priority.MEDIUM: "bold blue",
    Priority.LOW: "bold green",
}


def _confidence_bar(confidence: int, width: int = 10) -> str:
    """Render a simple block-character confidence bar.

    Args:
        confidence: Integer 0–100.
        width: Total bar width in characters.

    Returns:
        String like ``████░░░░░░ 72%``.
    """
    filled = round(confidence / 100 * width)
    bar = "█" * filled + "░" * (width - filled)
    return f"{bar} {confidence}%"


def print_classification_result(email: EmailMessage, result: ClassificationResult) -> None:
    """Print a formatted Rich panel showing classification details.

    Args:
        email: The parsed email that was classified.
        result: The classification output from the Ollama model.
    """
    category_style = _CATEGORY_STYLES.get(result.category, "white")
    priority_style = _PRIORITY_STYLES.get(result.priority, "white")
    classified_at_str = result.classified_at.strftime("%Y-%m-%d %H:%M:%S")

    table = Table(show_header=True, header_style="bold cyan", box=box.SIMPLE, expand=True)
    table.add_column("Field", style="bold", width=16)
    table.add_column("Value")

    table.add_row("From", email.sender)
    table.add_row("Subject", email.subject)
    table.add_row("Category", f"[{category_style}]{result.category.value}[/{category_style}]")
    table.add_row("Priority", f"[{priority_style}]{result.priority.value}[/{priority_style}]")
    table.add_row("Confidence", _confidence_bar(result.confidence))
    table.add_row("Summary", result.summary)
    table.add_row("Action", result.recommended_action)
    table.add_row("Model", result.model_used)
    table.add_row("Classified At", classified_at_str)

    panel = Panel(
        table,
        title="[bold cyan]📧 Email Classification Result[/bold cyan]",
        border_style="cyan",
        expand=True,
    )
    console.print(panel)


def print_scan_header(count: int) -> None:
    """Print a styled header announcing the start of an inbox scan.

    Args:
        count: Number of unread emails found.
    """
    console.rule(f"[bold cyan]🔍 Scanning inbox — found {count} unread email(s)[/bold cyan]")


def print_scan_complete(processed: int, errors: int) -> None:
    """Print a summary line when a scan finishes.

    Args:
        processed: Number of emails successfully classified.
        errors: Number of emails that could not be processed.
    """
    style = "bold green" if errors == 0 else "bold yellow"
    console.print(
        f"[{style}]✅ Scan complete — {processed} classified, {errors} errors[/{style}]"
    )


def print_error(message: str) -> None:
    """Print a styled red error panel.

    Args:
        message: Error message to display.
    """
    console.print(Panel(f"[bold red]{message}[/bold red]", title="❌ Error", border_style="red"))


def print_test_mode_banner() -> None:
    """Print a yellow warning banner indicating test mode is active."""
    console.print(
        Panel(
            "[bold yellow]⚠️  TEST MODE — Using fixture emails, no IMAP connection[/bold yellow]",
            border_style="yellow",
        )
    )
