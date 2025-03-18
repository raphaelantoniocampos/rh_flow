#!/usr/bin/env python3
import os
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

console = Console()

# Dictionary of examples: key, title, filename, and description.
examples = {
    "1": (
        "Basic Colours",
        "01_basic_colors.py",
        "Demonstrates how to print coloured and styled text.",
    ),
    "2": (
        "Emojis and Markdown",
        "02_emojis_markdown.py",
        "Shows emoji support and Markdown rendering.",
    ),
    "3": (
        "Syntax Highlighting",
        "03_syntax_highlight.py",
        "Highlights JSON code with a colour theme.",
    ),
    "4": ("Tables", "04_tables.py", "Creates a formatted table with multiple columns."),
    "5": (
        "Progress Bar",
        "05_progress_bar.py",
        "Displays an interactive progress bar.",
    ),
    "6a": (
        "Live Updates (console print)",
        "06a_live_updates_console_print.py",
        "Updates terminal output live using console print.",
    ),
    "6b": (
        "Live Updates (Text object)",
        "06b_live_updates_text_object.py",
        "Updates terminal output live using a Text object.",
    ),
    "7": (
        "Rich Logging",
        "07_logging.py",
        "Demonstrates colour-coded logging with Rich.",
    ),
    "8": ("Rich Tree", "08_tree.py", "do tree"),
    "9": ("Rich Layout", "09_layout.py", "do layout"),
    "10": ("Rich Spinner", "10_spinner.py", "do spinner"),
}


def clear_screen():
    """Clears the terminal screen."""
    os.system("clear" if os.name == "posix" else "cls")


def show_menu():
    """Displays the main menu."""
    clear_screen()

    console.print(
        Panel(
            "[bold cyan]Welcome to Rich Examples![/bold cyan] 🚀\n\n"
            "Enter the corresponding number to run an example.\n"
            "Type [bold magenta]'q'[/bold magenta] to quit.",
            title="[bold magenta]Rich Menu[/bold magenta]",
            expand=False,
        )
    )

    table = Table(title="Available Examples", header_style="bold magenta")
    table.add_column("Option", justify="center", style="cyan", no_wrap=True)
    table.add_column("Description", style="green")

    for key, (title, _, _) in examples.items():
        table.add_row(f"[bold yellow]{key}[/bold yellow]", title)

    console.print(table)


def run_example(choice):
    """Runs the chosen script."""
    if choice in examples:
        script_title, script_filename, script_desc = examples[choice]

        if not os.path.exists(script_filename):
            console.print(
                f"[bold red]Error:[/bold red] File '{script_filename}' not found!"
            )
            return

        clear_screen()
        console.print(
            Panel(
                f"[bold green]{script_title}[/bold green]\n\n"
                f"[italic]{script_desc}[/italic]\n\n"
                f"[bold cyan]File:[/bold cyan] {script_filename}",
                title="[bold green]Information[/bold green]",
                expand=False,
            )
        )

        # Run the chosen script immediately
        os.system(f"{script_filename}")

        # Wait for user input before returning to the menu
        console.input(
            "\n[bold magenta]Press Enter to return to the menu...[/bold magenta]"
        )
    else:
        console.print("[bold red]Invalid choice![/bold red]")


def main():
    """Main function to run the menu loop."""
    while True:
        show_menu()
        choice = (
            Prompt.ask("[bold cyan]Enter your choice[/bold cyan]", default="q")
            .strip()
            .lower()
        )
        if choice == "q":
            console.print("\n[bold magenta]Exiting...[/bold magenta] 🚀\n")
            break
        run_example(choice)


if __name__ == "__main__":
    main()
