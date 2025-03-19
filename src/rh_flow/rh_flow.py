from InquirerPy import inquirer
from rich import print
from rich.console import Console
from rich.panel import Panel
from tasks.download_task import DownloadTask
from utils.config import Config
from file_manager import FileManager
from data_manager import DataManager
from tasks.task_manager import TaskManager
from tasks.task import Task


console = Console()

OPTIONS = [
    "1. Baixar arquivos",
    "2. Analisar dados",
    "3. Ações",
    "4. Configurações",
    "5. Sair",
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
        FileManager.move_files_from_downloads_dir()
        data_manager = DataManager()
        task_manager = TaskManager()
        while True:
            tasks = task_manager.get_tasks()
            option = menu(tasks)[3:]
            match option:
                case "Baixar arquivos":
                    download_task = DownloadTask()
                    download_task.menu()

                case "Analisar dados":
                    data_manager.analyze()

                case "Ações":
                    task_manager.run(config, tasks)

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

    questions = [
        inquirer.List(
            "option", message="Selecione uma opção", choices=OPTIONS, carousel=True
        ),
    ]
    answers = inquirer.prompt(questions)
    return answers["option"]


def get_tasks_panel(tasks: list[Task]) -> Panel:
    orders = []
    for task in tasks:
        if task.get_len() > 0:
            orders.append(task.order)

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
    DownloadTask.menu()
    
# main()
