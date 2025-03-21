import time

import keyboard
from pyperclip import copy
from rich import print
from utils.constants import spinner, Key

from tasks.task import Task
from tasks.task_runner import TaskRunner


class RemoveEmployeesTask(TaskRunner):
    KEY_CONTINUE = Key("F2", "green")
    KEY_NEXT = Key("F3", "yellow")
    KEY_STOP = Key("F4", "red3")

    def __init__(self, task: Task):
        super().__init__(task)

    def run(self):
        df = self.task.df
        for i, series in df.iterrows():
            print(
                f"\n[bold yellow]{'-' * 15} FUNCIONÁRIO DESLIGADO! {'-' * 15}[/bold yellow]"
            )
            print(series)

            print(
                f"Pressione {self.KEY_CONTINUE} para copiar a [bold white]Data de Desligamento[/bold white]."
            )
            print(
                f"Pressione {self.KEY_NEXT} para próximo [bold white]funcionário[/bold white]."
            )
            print(f"Pressione {self.KEY_STOP} para [bold white]sair...[/bold white]")
            name = series["name"]
            copy(name)
            print(f"(Nome '{name}' copiado para a área de transferência!)")
            while True:
                if keyboard.is_pressed(self.KEY_CONTINUE.key):
                    date = series["dismissal_date"]
                    print(f"(DATA '{date}' copiado para a área de transferência!)")
                    copy(date)
                    time.sleep(0.5)
                    print(f"Pressione {self.KEY_NEXT} para próximo [bold white]funcionário[/bold white].")
                    continue
                if keyboard.is_pressed(self.KEY_NEXT.key):
                    time.sleep(0.5)
                    break
                if keyboard.is_pressed(self.KEY_STOP.key):
                    time.sleep(0.5)
                    super().exit_task()
                    spinner()
                    return
            if keyboard.is_pressed(self.KEY_NEXT.key):
                time.sleep(0.5)
                continue

        super().exit_task()

        
