#!/usr/bin/env python3
import time
from rich.console import Console
from rich.text import Text

console = Console()

for i in range(10):
    text = Text(f"Update {i+1}/10", style="bold green")
    console.print(text, end="\r")
    time.sleep(0.5)
console.print("\nDone!")
