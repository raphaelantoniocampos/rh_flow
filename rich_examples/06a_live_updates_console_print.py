#!/usr/bin/env python3
import time
from rich.console import Console

console = Console()

for i in range(10):
    console.print(f"[bold green]Update {i+1}/10[/bold green]", end="\r")
    time.sleep(0.5)
console.print("\nDone!")
