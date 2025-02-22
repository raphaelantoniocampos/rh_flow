from pathlib import Path
import time

import inquirer
from rich import print
from rich.console import Console
from rich.panel import Panel

from file_downloader import FileDownloader
from data_manager import DataManager, Actions
from action_handler import ActionHandler

WORKING_DIR = Path.cwd()

console = Console()

OPTIONS = {
    1: "Baixar arquivos",
    2: "Analisar dados",
    3: "Ações",
    4: "Sair",
}


def main():
    data_manager = DataManager(WORKING_DIR)
    while True:
        try:
            actions = data_manager.get_actions()
            option = show_menu(actions)
            match option:
                case "Baixar arquivos":
                    print("[bold red]DESATIVADO NO MOMENTO[/bold red]")
                    time.sleep(1)
                    continue
                    file_downloader = FileDownloader(WORKING_DIR)
                    file_downloader.run()

                case "Analisar dados":
                    data_manager.analyze()

                case "Ações":
                    action_handler = ActionHandler(actions, data_manager)
                    action_handler.run()

                case "Sair":
                    break

        except KeyboardInterrupt:
            break

    print("Saindo...")


def show_menu(actions: Actions):
    console.print(
        Panel.fit(
            f"{'-' * 14}RH FLOW{'-' * 14}\nBem-vindo ao Sistema de. Automação",
            style="bold blue",
        )
    )
    console.print("\n")

    actions_panel = get_actions_panel(actions)
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


def get_actions_panel(actions: Actions) -> Panel:
    actions_list = []

    if actions.to_add is not None:
        actions_list.append(
            f"[bold cyan]•[/] Adicionar [cyan]{len(actions.to_add)}[/] funcionários ao Ahgora"
        )

    if actions.to_remove is not None:
        actions_list.append(
            f"[bold cyan]•[/] Remover [cyan]{len(actions.to_remove)}[/] funcionários do Ahgora"
        )

    if not actions:
        actions_list.append("[green]• Nenhuma ação pendente.[/green]")

        return Panel.fit(
            "[green]• Nenhuma ação pendente.[/green]",
            title="[bold]Ações Pendentes[/bold]",
            border_style="green",
            padding=(1, 2),
        )

    return Panel.fit(
        "\n".join(actions_list),
        title="[bold]Ações Pendentes[/bold]",
        border_style="yellow",
        padding=(1, 2),
    )


if __name__ == "__main__":
    main()
