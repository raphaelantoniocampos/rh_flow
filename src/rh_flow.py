from dataclasses import dataclass
import pandas as pd
import time
import os

import inquirer
from rich import print
from rich.console import Console
from rich.panel import Panel

from file_downloader import FileDownloader
from data_analyzer import DataAnalyzer
from action_handler import ActionHandler

WORKING_DIR = os.getcwd()

console = Console()

OPTIONS = {
    1: "Baixar arquivos",
    2: "Analisar dados",
    3: "Ações",
    4: "Sair",
}

@dataclass
class ActionsToDo:
    to_add: pd.DataFrame | None
    to_remove: pd.DataFrame | None

def main():
    while True:
        try:
            actions_to_do = get_actions_to_do()
            option = show_menu(actions_to_do)
            match option:
                case "Baixar arquivos":
                    print("[bold red]DESATIVADO NO MOMENTO[/bold red]")
                    time.sleep(1)
                    continue
                    file_downloader = FileDownloader(WORKING_DIR)
                    file_downloader.run()

                case "Analisar dados":
                    data_analyzer = DataAnalyzer(WORKING_DIR)
                    data_analyzer.run()

                case "Ações":
                    action_handler = ActionHandler(actions_to_do)
                    action_handler.run()

                case "Sair":
                    break

        except KeyboardInterrupt:
            break

    print("Saindo...")


def show_menu(actions_to_do: ActionsToDo):
    console.print(
        Panel.fit(
            f"{'-' * 14}RH FLOW{'-' * 14}\nBem-vindo ao Sistema de. Automação",
            style="bold blue",
        )
    )
    console.print("\n")

    actions_panel = get_actions_panel(actions_to_do)
    console.print(actions_panel)

    questions = [
        inquirer.List(
            "option",
            message="Selecione uma opção",
            choices=OPTIONS.values(),
        ),
    ]
    answers = inquirer.prompt(questions)
    return answers["option"]

def get_actions_to_do() -> ActionsToDo:
    to_process_dir = os.path.join(WORKING_DIR, 'data', 'to_do')

    new_employees_path = os.path.join(to_process_dir, 'new_employees.csv')
    dismissed_employees_path = os.path.join(to_process_dir, 'dismissed_employees.csv')

    data_to_process = ActionsToDo(None, None)

    if os.path.isfile(new_employees_path):
        df_new = pd.read_csv(new_employees_path)
        data_to_process.to_add = df_new

    if os.path.isfile(dismissed_employees_path):
        df_dismissed = pd.read_csv(dismissed_employees_path)
        data_to_process.to_remove = df_dismissed

    return data_to_process

def get_actions_panel(actions_to_do: ActionsToDo) -> Panel:
    actions = []

    if actions_to_do.to_add is not None:
        actions.append(f"[bold cyan]•[/] Adicionar [cyan]{len(actions_to_do.to_add)}[/] funcionários ao Ahgora")

    if actions_to_do.to_remove is not None:
        actions.append(f"[bold cyan]•[/] Remover [cyan]{len(actions_to_do.to_remove)}[/] funcionários do Ahgora")

    if not actions:
        actions.append("[green]• Nenhuma ação pendente.[/green]")

        return Panel.fit(
            "[green]• Nenhuma ação pendente.[/green]",
            title="[bold]Ações Pendentes[/bold]",
            border_style="green",
            padding=(1, 2),
        )

    return Panel.fit(
        "\n".join(actions),
        title="[bold]Ações Pendentes[/bold]",
        border_style="yellow",
        padding=(1, 2),
    )


if __name__ == "__main__":
    main()
