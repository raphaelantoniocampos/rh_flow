#!/usr/bin/env python3
from rich.console import Console
from rich.syntax import Syntax

console = Console()

json_data = '{"name": "Alice", "language": "Python"}'
syntax = Syntax(json_data, "json", theme="monokai", line_numbers=True)
console.print(syntax)
