#!/usr/bin/env python3
from rich.console import Console
from rich.markdown import Markdown

console = Console()

# Displaying emojis and styled text
console.print(":rocket: [bold cyan]Rich is brilliant![/bold cyan] :smile:")

# Rendering Markdown
md_content = """
# Markdown Title

**Bold text**

- Item 1
- Item 2
"""
md = Markdown(md_content)
console.print(md)
