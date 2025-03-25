from datetime import datetime

from InquirerPy import inquirer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from rh_flow.managers.file_manager import FileManager
from rh_flow.managers.data_manager import DataManager
from rh_flow.managers.task_manager import TaskManager
from rh_flow.managers.download_manager import DownloadManager
from rh_flow.tasks.task import Task
from rh_flow.utils.constants import (
    INQUIRER_KEYBINDINGS,
    MAIN_MENU_OPTIONS,
    PT_MONTHS,
    PT_WEEKDAYS,
    spinner,
)

console = Console()

# TODO: ask to create creds on start
# TODO: make last downloads and analyze appear on main screen
# TODO: configure the panel to be central and prettier


class Header:
    """Display header with clock."""

    def __rich__(self) -> Panel:
        now = datetime.now()

        en_weekday = now.strftime("%a")
        en_month = now.strftime("%b")
        day = now.strftime("%d")
        year = now.strftime("%Y")

        pt_weekday = PT_WEEKDAYS.get(en_weekday, en_weekday)
        pt_month = PT_MONTHS.get(en_month, en_month)

        time_str = now.strftime("%H[blink]:[/]%M[blink]:[/]%S")

        grid = Table.grid(expand=True)
        grid.add_column(justify="left")
        grid.add_column(justify="center", ratio=1)
        grid.add_column(justify="right")
        grid.add_row(
            f"{pt_weekday} {day} {pt_month} {year}",
            "[b]Integração[/b] Fiorilli/Ahgora",
            time_str,
        )
        return Panel(
            grid,
            style="cyan",
        )

def main():
    # config = Config()
    file_manager = FileManager()
    task_manager = TaskManager()
    data_manager = DataManager()
    download_manager = DownloadManager()
    file_manager.move_downloads_to_data_dir()

    while True:
        header = Header()
        console.print(header)
        tasks = task_manager.get_tasks()

        option = menu_table(tasks)
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

            case "live display":
                pass
                # live_display(tasks)

            case "sair":
                raise KeyboardInterrupt


def menu_table(tasks: list[Task]):
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
