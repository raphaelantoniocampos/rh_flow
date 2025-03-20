from utils.constants import INQUIRER_KEYBINDINGS
from InquirerPy import inquirer
from rich import print
from rich.console import Console
from rich.panel import Panel
from tasks.download_task import DownloadTask
from utils.config import Config
from managers.file_manager import FileManager
from managers.data_manager import DataManager
from managers.task_manager import TaskManager
from tasks.task import Task

console = Console()

OPTIONS = [
    "Baixar arquivos",
    "Analisar dados",
    "Tarefas",
    "Configurações",
    "Sair",
]

# TODO: ask to create creds on start
# TODO: task df na tela de task nao ta levando os ignore em conta
# TODO: Exportar buton firoilli now work
# TODO: adicionar opcao headless file downloader
# TODO: check fiorilli downloads
# TODO: check ahgora downloads
# TODO: fix position task
# TODO: create new abcenses task remove.py using txt
# TODO: file downloader multithread e separado
# TODO: file downloader segundo plano
# TODO: separate file_downloader into classes
# TODO: make add employees download ahgora again
# TODO: make last downloads and analyze appear on main screen
# TODO: configure the panel to be central and prettier
# TODO: refactor structure tree


def main():
    try:
        config = Config()
        FileManager.move_downloads_to_data_dir()
        dm = DataManager()
        tm = TaskManager()
        while True:
            tasks = tm.get_tasks()
            option = menu(tasks)
            match option:
                case "Baixar arquivos":
                    dt = DownloadTask()
                    dt.menu()

                case "Analisar dados":
                    dm.analyze()

                case "Tarefas":
                    tm.menu(tasks)

                case "Configurações":
                    config.config_panel(console)

                case "Sair":
                    raise KeyboardInterrupt

    except KeyboardInterrupt:
        print("Saindo...")


def menu(tasks: list[Task]):
    console.print(
        Panel.fit(
            f"{'-' * 14}RH FLOW{'-' * 14}\nBem-vindo ao Sistema de. Automação",
            style="bold blue",
        )
    )
    console.print("\n")

    tasks_panel = get_tasks_panel(tasks)
    console.print(tasks_panel)

    answers = inquirer.rawlist(
        message="Selecione uma opção",
        choices=OPTIONS,
        keybindings=INQUIRER_KEYBINDINGS,
    ).execute()
    return answers


def get_tasks_panel(tasks: list[Task]) -> Panel:
    orders = []
    for task in tasks:
        if task.__len__() > 0:
            orders.append(task.order)

    if not orders:
        orders.append("[green]• Nenhuma ação pendente.[/green]")

        return Panel.fit(
            "[green]• Nenhuma ação pendente.[/green]",
            title="[bold]Tarefas Pendentes[/bold]",
            border_style="green",
            padding=(1, 2),
        )

    return Panel.fit(
        "\n".join(orders),
        title="[bold]Tarefas Pendentes[/bold]",
        border_style="yellow",
        padding=(1, 2),
    )


if __name__ == "__main__":
    main()
