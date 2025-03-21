from utils.constants import INQUIRER_KEYBINDINGS, MAIN_MENU_OPTIONS, spinner
from InquirerPy import inquirer
from rich.console import Console
from rich.panel import Panel
from managers.file_manager import FileManager
from managers.data_manager import DataManager
from managers.task_manager import TaskManager
from managers.download_manager import DownloadManager
from tasks.task import Task

console = Console()

# TODO: ask to create creds on start
# TODO: add ignore employees
# TODO: create new abcenses task remove.py using txt
# TODO: make last downloads and analyze appear on main screen
# TODO: configure the panel to be central and prettier
# TODO: key and task model?


def main():
    # config = Config()
    file_manager = FileManager()
    task_manager = TaskManager()
    data_manager = DataManager()
    download_manager = DownloadManager()

    file_manager.move_downloads_to_data_dir()
    while True:
        tasks = task_manager.get_tasks()
        option = menu(tasks)
        match option.lower():
            case "baixar dados":
                download_manager.menu()

            case "analisar dados":
                data_manager.analyze()

            case "tarefas":
                task_manager.menu(tasks)

            case "configurações":
                pass
                # config.menu(console)

            case "sair":
                raise KeyboardInterrupt


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
        choices=MAIN_MENU_OPTIONS,
        keybindings=INQUIRER_KEYBINDINGS,
    ).execute()
    return answers


def get_tasks_panel(tasks: list[Task]) -> Panel:
    task_options = [f"[bold cyan]•[/] {task.option}" for task in tasks if task.option]

    if not task_options:
        task_options.append("[green]• Nenhuma tarefa pendente.[/green]")

        return Panel.fit(
            "[green]• Nenhuma tarefa pendente.[/green]",
            title="[bold]Tarefas Pendentes[/bold]",
            border_style="green",
            padding=(1, 2),
        )

    return Panel.fit(
        "\n".join(task_options),
        title="[bold]Tarefas Pendentes[/bold]",
        border_style="yellow",
        padding=(1, 2),
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        spinner("Saindo")
