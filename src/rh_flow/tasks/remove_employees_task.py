from utils.constants import spinner
import time
from tasks.task_runner import TaskRunner
import keyboard
from pyperclip import copy
from rich.console import Console
from rich.panel import Panel
from InquirerPy import inquirer


class RemoveEmployeesTask(TaskRunner):
    @staticmethod
    def menu():
        console = Console()
        console.print(
            Panel.fit(
                "Remover Funcionários",
                style="bold cyan",
            )
        )

        proceed = inquirer.confirm(message="Continuar?", default=True).execute()
        if proceed:
            ret = RemoveEmployeesTask()
            ret.run()
        return

    def run(self, df):
        for i, series in df.iterrows():
            if df.empty:
                print(
                    "[bold yellow]Nenhum funcionário para remover do Ahgora no momento.[/bold yellow]\n"
                )
                return
            print(
                f"\n[bold yellow]{'-' * 15} FUNCIONÁRIO DESLIGADO! {'-' * 15}[/bold yellow]"
            )
            print(series)

            print(
                f"Pressione {super().KEY_CONTINUE} para copiar a [bold white]Data de Desligamento[/bold white]."
            )
            print(
                f"Pressione {super().KEY_NEXT} para próximo [bold white]funcionário[/bold white]."
            )
            print(f"Pressione {super().KEY_STOP} para [bold white]sair...[/bold white]")
            name = series["name"]
            print(f"(name '{name}' copiado para a área de transferência!)")
            copy(name)
            while True:
                if keyboard.is_pressed(super().KEY_CONTINUE.key):
                    date = series["dismissal_date"]
                    print(f"(id '{date}' copiado para a área de transferência!)")
                    copy(date)
                    time.sleep(0.5)
                    continue
                if keyboard.is_pressed(super().KEY_NEXT.key):
                    time.sleep(0.5)
                    break
                if keyboard.is_pressed(super().KEY_STOP.key):
                    time.sleep(0.5)
                    spinner()
                    return
            if keyboard.is_pressed(super().KEY_NEXT.key):
                time.sleep(0.5)
                continue
