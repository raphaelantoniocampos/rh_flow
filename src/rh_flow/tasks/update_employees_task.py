import time

import keyboard
from pyperclip import copy
from rich import print
from utils.constants import spinner, Key

from tasks.task import Task
from tasks.task_runner import TaskRunner


class UpdateEmployeesTask(TaskRunner):
    KEY_POSITION = Key("F1", "cyan")
    KEY_DEPARTMENT = Key("F2", "purple")
    KEY_NEXT = Key("F3", "yellow")
    KEY_STOP = Key("F4", "red")

    def __init__(self, task: Task):
        super().__init__(task)

    def run(self):
        df = self.task.df

        for i, series in df.iterrows():
            name = series["name_fiorilli"]
            id = series["id"]

            position_changed = (
                series["position_fiorilli_norm"] != series["position_ahgora_norm"]
            )
            department_changed = (
                series["department_fiorilli_norm"] != series["department_ahgora_norm"]
            )

            position_fiorilli = series["position_fiorilli"]
            position_ahgora = series["position_ahgora"]
            department_fiorilli = series["department_fiorilli"]
            department_ahgora = series["department_ahgora"]

            changes = []
            if position_changed:
                changes.append("CARGO")
            if department_changed:
                changes.append("DEPARTAMENTO")

            print(
                f"\n[bold yellow]{'-' * 15} FUNCIONÁRIO ALTERADO! {'-' * 15}[/bold yellow]"
            )
            print(f"{name} - {id}")
            print(f"Alterar {' e '.join(changes)}")
            print(f"Antigo Cargo (Ahgora): {position_ahgora}")
            print(
                f"Novo Cargo (Fiorilli): {f'[green]{position_fiorilli}[/]' if 'CARGO' in changes else f'{position_fiorilli}'}"
            )
            print(f"Antigo Departamento (Ahgora): [bold]{department_ahgora}[/bold]")
            print(
                f"Novo Departamento (Fiorilli): {f'[green]{department_fiorilli}[/]' if 'DEPARTAMENTO' in changes else f'{department_fiorilli}'}"
            )
            print("\n")

            if "CARGO" in changes:
                print(
                    f"Pressione {self.KEY_POSITION} para copiar o novo [bold white]Cargo[/bold white]."
                )
            if "DEPARTAMENTO" in changes:
                print(
                    f"Pressione {self.KEY_DEPARTMENT} para copiar o novo [bold white]Departamento[/bold white]."
                )
            print(
                f"Pressione {self.KEY_NEXT} para o [bold white]próximo[/bold white] funcionário."
            )
            print(f"Pressione {self.KEY_STOP} para [bold white]sair...[/bold white]")
            copy(name)
            print(f"(Nome '{name}' copiado para a área de transferência!)")
            while True:
                if keyboard.is_pressed(self.KEY_POSITION.key):
                    copy(position_fiorilli)
                    print(
                        f"(Cargo '{position_fiorilli}' copiado para a área de transferência!)"
                    )
                    time.sleep(0.5)
                    continue
                if keyboard.is_pressed(self.KEY_DEPARTMENT.key):
                    copy(department_fiorilli)
                    print(
                        f"(Departamento '{department_fiorilli}' copiado para a área de transferência!)"
                    )
                    time.sleep(0.5)
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
