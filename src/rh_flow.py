from datetime import datetime
from time import sleep

from InquirerPy import inquirer
from rich import box
from rich.align import Align
from rich.console import Console, Group
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.table import Table

from rh_flow.managers.data_manager import DataManager
from rh_flow.managers.download_manager import DownloadManager
from rh_flow.managers.file_manager import FileManager
from rh_flow.managers.task_manager import TaskManager
from rh_flow.tasks.task import Task
from rh_flow.utils.constants import (
    INQUIRER_KEYBINDINGS,
    MAIN_MENU_OPTIONS,
    PT_WEEKDAYS,
    PT_MONTHS,
    spinner,
)

console = Console()

# TODO: ask to create creds on start
# TODO: make last downloads and analyze appear on main screen
# TODO: configure the panel to be central and prettier


def live_display(tasks):
    def make_layout() -> Layout:
        """Define the layout."""
        layout = Layout(name="root")

        layout.split(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=7),
        )
        layout["main"].split_row(
            Layout(name="body", ratio=2, minimum_size=60),
            Layout(name="side"),
        )
        layout["side"].split(Layout(name="box1"), Layout(name="box2"))
        return layout

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
                time_str,
                "[b]Integração[/b] Fiorilli/Ahgora",
                f"{pt_weekday} {day} {pt_month} {year}",
            )
            return Panel(
                grid,
                style="cyan",
            )

    def main_menu(tasks) -> Panel:
        """Some example content."""

        menu_table = Table.grid(padding=(0, 2))
        menu_table.add_column(style="green", justify="left")
        menu_table.add_column(style="bold white", justify="left")
        menu_table.add_column(style="dim", justify="right")

        # Adicionando opções
        menu_table.add_row(
            "1",
            "Baixar Dados",
            "(Obter dados mais recentes)",
        )
        menu_table.add_row(
            "2",
            "Analisar Dados",
            "(Processar informações)",
        )
        menu_table.add_row(
            "3",
            "Tarefas",
            f"({len(tasks)} pendentes)",
        )
        menu_table.add_row(
            "4",
            "Configurações",
            "(Ajustes do sistema)",
        )
        menu_table.add_row(
            "5",
            "Live Display",
            "(Monitoramento em tempo real)",
        )
        menu_table.add_row(
            "Q",
            "Sair",
            "(Encerrar o programa)",
        )

        # menu = Table.grid(padding=1)
        # menu.add_column(no_wrap=True)
        # menu_table.add_row(
        #     "Twitter",
        #     "[u blue link=https://twitter.com/textualize]https://twitter.com/textualize",
        # )
        # menu_table.add_row(
        #     "CEO",
        #     "[u blue link=https://twitter.com/willmcgugan]https://twitter.com/willmcgugan",
        # )
        # menu_table.add_row(
        #     "Textualize",
        #     "[u blue link=https://www.textualize.io]https://www.textualize.io",
        # )

        message = Table.grid(padding=1)
        message.add_column()
        message.add_column(no_wrap=True)
        message.add_row(menu_table)

        message_panel = Panel(
            Align.center(
                Group("\n", Align.center(menu_table)),
                vertical="middle",
            ),
            box=box.ROUNDED,
            padding=(1, 2),
            title="[b red]Thanks for trying out Rich!",
            border_style="bright_blue",
        )
        return message_panel

    def make_syntax() -> Syntax:
        code = """\
    def ratio_resolve(total: int, edges: List[Edge]) -> List[int]:
        sizes = [(edge.size or None) for edge in edges]

        # While any edges haven't been calculated
        while any(size is None for size in sizes):
            # Get flexible edges and index to map these back on to sizes list
            flexible_edges = [
                (index, edge)
                for index, (size, edge) in enumerate(zip(sizes, edges))
                if size is None
            ]
            # Remaining space in total
            remaining = total - sum(size or 0 for size in sizes)
            if remaining <= 0:
                # No room for flexible edges
                sizes[:] = [(size or 0) for size in sizes]
                break
            # Calculate number of characters in a ratio portion
            portion = remaining / sum((edge.ratio or 1) for _, edge in flexible_edges)

            # If any edges will be less than their minimum, replace size with the minimum
            for index, edge in flexible_edges:
                if portion * edge.ratio <= edge.minimum_size:
                    sizes[index] = edge.minimum_size
                    break
            else:
                # Distribute flexible space and compensate for rounding error
                # Since edge sizes can only be integers we need to add the remainder
                # to the following line
                _modf = modf
                remainder = 0.0
                for index, edge in flexible_edges:
                    remainder, size = _modf(portion * edge.ratio + remainder)
                    sizes[index] = int(size)
                break
        # Sizes now contains integers only
        return cast(List[int], sizes)
        """
        syntax = Syntax(code, "python", line_numbers=True)
        return syntax

    job_progress = Progress(
        "{task.description}",
        SpinnerColumn(),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    )
    job_progress.add_task("[green]Cooking")
    job_progress.add_task("[magenta]Baking", total=1500)
    job_progress.add_task("[cyan]Mixing", total=2000)

    total = sum(task.total for task in job_progress.tasks)
    overall_progress = Progress()
    overall_task = overall_progress.add_task("All Jobs", total=int(total))

    progress_table = Table.grid(expand=True)
    progress_table.add_row(
        Panel(
            overall_progress,
            title="Overall Progress",
            border_style="green",
            padding=(2, 2),
        ),
        Panel(job_progress, title="[b]Jobs", border_style="red", padding=(1, 2)),
    )

    layout = make_layout()
    layout["header"].update(Header())
    layout["body"].update(main_menu(tasks))
    layout["box2"].update(Panel(make_syntax(), border_style="green"))
    layout["box1"].update(Panel(layout.tree, border_style="red"))
    layout["footer"].update(progress_table)

    with Live(layout, refresh_per_second=10, screen=True):
        while not overall_progress.finished:
            sleep(0.1)
            for job in job_progress.tasks:
                if not job.finished:
                    job_progress.advance(job.id)

            completed = sum(task.completed for task in job_progress.tasks)
            overall_progress.update(overall_task, completed=completed)


def main():
    # config = Config()
    file_manager = FileManager()
    task_manager = TaskManager()
    data_manager = DataManager()
    download_manager = DownloadManager()

    file_manager.move_downloads_to_data_dir()
    while True:
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
                live_display(tasks)

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
