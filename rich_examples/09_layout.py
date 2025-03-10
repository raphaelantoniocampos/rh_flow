#!/usr/bin/env python3
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel

console = Console()

# Create the main layout
layout = Layout()
layout.split(
    Layout(name="upper", size=3),
    Layout(name="lower")
)

# Update the upper panel
layout["upper"].update(Panel("This is the upper panel", title="Upper"))

# Split the lower layout into two columns
layout["lower"].split_row(
    Layout(Panel("Left lower panel", title="Left")),
    Layout(Panel("Right lower panel", title="Right"))
)

console.print(layout)
