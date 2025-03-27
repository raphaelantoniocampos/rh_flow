import time
from pyperclip import copy
from rich import print

from rh_flow.models.task import Task
from rh_flow.tasks.task_runner import TaskRunner
from rh_flow.utils.constants import spinner
from rh_flow.models.key import Key, wait_key_press


class UpdateEmployeesTask(TaskRunner):
    KEY_POSITION = Key("F1", "cyan", "copiar o cargo")
    KEY_DEPARTMENT = Key("F2", "purple", "copiar o departamento")
    KEY_NEXT = Key("F3", "yellow", "próximo")
    KEY_STOP = Key("F4", "red", "sair")

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
            copy(name)
            print(f"(Nome '{name}' copiado para a área de transferência!)")
            while True:
                match wait_key_press(
                    [
                        self.KEY_POSITION,
                        self.KEY_DEPARTMENT,
                        self.KEY_NEXT,
                        self.KEY_STOP,
                    ]
                ):
                    case "copiar o cargo":
                        copy(position_fiorilli)
                        print(
                            f"(Cargo '{position_fiorilli}' copiado para a área de transferência!)"
                        )
                        time.sleep(0.5)
                    case "copiar o departamento":
                        copy(department_fiorilli)
                        print(
                            f"(Departamento '{department_fiorilli}' copiado para a área de transferência!)"
                        )
                        time.sleep(0.5)
                    case "próximo":
                        spinner("Continuando")
                        break
                    case "sair":
                        super().exit_task()
                        spinner()
                        return

        print("[bold green]Não há mais cargos para alterar![/bold green]")
        super().exit_task()
