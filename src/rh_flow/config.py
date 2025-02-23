from rich.console import Console
import inquirer
from rich import print
from rich.panel import Panel

from utils import Utils

class Config:
    def __init__(self, console: Console, utils: Utils):
        self.console = console
        self.utils = utils

    def manage_ignored(self):
        ignore_data = self.utils.read().get("ignore", {})
        
        if not ignore_data:
            print("[bold yellow]Nenhum funcionário está sendo ignorado no momento.[/bold yellow]")
            return

        self.console.print(Panel.fit(
            "[bold]Funcionários Ignorados[/bold]",
            border_style="yellow"
        ))
        for matricula, data in ignore_data.items():
            self.console.print(
                f"[cyan]•[/] [bold]{matricula}[/]: {data['Nome']} ({data['Vinculo']})"
            )

        questions = [
            inquirer.List(
                "action",
                message="O que deseja fazer?",
                choices=["Remover um funcionário", "Voltar"],
            ),
        ]
        answers = inquirer.prompt(questions)
        action = answers["action"]

        if action == "Remover um funcionário":
            questions = [
                inquirer.Text(
                    "matricula",
                    message="Digite a matrícula do funcionário a ser removido",
                ),
            ]
            answers = inquirer.prompt(questions)
            matricula = answers["matricula"]

            self.utils.remove("ignore", matricula)
