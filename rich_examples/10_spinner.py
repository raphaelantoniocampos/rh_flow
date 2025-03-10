#!/usr/bin/env python3
import time
from rich.console import Console

console = Console()

with console.status("[bold green]Processing...[/bold green]", spinner="dots"):
    # Simulate a task taking some time
    time.sleep(3)

console.print("[bold green]Done![/bold green]")
