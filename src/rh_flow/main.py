from pathlib import Path

import inquirer
from __init__ import verify_paths
from action_handler import ActionHandler
from action import Action
from config import Config
from data_manager import DataManager
from file_downloader import FileDownloader
from rich import print
from rich.console import Console
from rich.panel import Panel

verify_paths()

BASE_DIR = Path.cwd()

console = Console()

OPTIONS = [
    "1. Baixar arquivos",
    "2. Analisar dados",
    "3. Ações",
    "4. Configurações",
    "5. Sair",
]


def main():
    try:
        while True:
            # TODO: make last downloads and analyze appear on main screen
            # TODO: configure the panel to be central and prettier
            config = Config(BASE_DIR)
            data_manager = DataManager(BASE_DIR, config)
            action_handler = ActionHandler(BASE_DIR, config, data_manager)

            actions = action_handler.get_actions()
            option = show_menu(actions)[3:]
            match option:
                case "Baixar arquivos":
                    file_downloader = FileDownloader(BASE_DIR, config)
                    file_downloader.run()

                case "Analisar dados":
                    data_manager.analyze()

                case "Ações":
                    action_handler.run(actions)

                case "Configurações":
                    config.config_panel(console)

                case "Sair":
                    raise KeyboardInterrupt

    except KeyboardInterrupt:
        print("Saindo...")


def show_menu(actions: list[Action]):
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
            "option", message="Selecione uma opção", choices=OPTIONS, carousel=True
        ),
    ]
    answers = inquirer.prompt(questions)
    return answers["option"]


def get_actions_panel(actions: list[Action]) -> Panel:
    orders = []
    for action in actions:
        if action.get_len() > 0:
            orders.append(action.order)

    if not orders:
        orders.append("[green]• Nenhuma ação pendente.[/green]")

        return Panel.fit(
            "[green]• Nenhuma ação pendente.[/green]",
            title="[bold]Ações Pendentes[/bold]",
            border_style="green",
            padding=(1, 2),
        )

    return Panel.fit(
        "\n".join(orders),
        title="[bold]Ações Pendentes[/bold]",
        border_style="yellow",
        padding=(1, 2),
    )


if __name__ == "__main__":
    main()
