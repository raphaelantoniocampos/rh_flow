import time

import keyboard
import pyautogui
from pyperclip import copy
from rich import print

from rh_flow.tasks.task import Task
from rh_flow.tasks.task_runner import TaskRunner
from rh_flow.utils.constants import Key, spinner


class AddEmployeesTask(TaskRunner):
    KEY_CONTINUE = Key("F2", "green")
    KEY_NEXT = Key("F3", "yellow")
    KEY_STOP = Key("F4", "red3")

    def __init__(self, task: Task):
        super().__init__(task)

    def run(self) -> None:
        df = self.task.df
        for i, series in df.iterrows():
            print(
                f"\n[bold yellow]{'-' * 15} NOVO FUNCIONÁRIO! {'-' * 15}[/bold yellow]"
            )
            print(series)
            print(
                f"\nPressione {self.KEY_CONTINUE} para [bold white]adicionar[/bold white] o funcionário."
            )
            print(
                f"Pressione {self.KEY_NEXT} para o [bold white]próximo[/bold white] funcionário."
            )
            print(f"Pressione {self.KEY_STOP} para [bold white]sair...[/bold white]")
            name = series.get("name")
            copy(name)
            print(f"Nome '{name}' copiado para a área de transferência!)")
            while True:
                if keyboard.is_pressed(self.KEY_CONTINUE.key):
                    time.sleep(0.5)
                    self._auto_new(series)
                    break
                if keyboard.is_pressed(self.KEY_NEXT.key):
                    time.sleep(0.5)
                    break
                if keyboard.is_pressed(self.KEY_STOP.key):
                    time.sleep(0.5)
                    super().exit_task()
                    spinner()
                    return

        super().exit_task()

    def _auto_new(self, row):
        print(
            f"\nClique em [bright_blue]Novo Funcionário[/], clique no [bright_blue]Nome[/] e Aperte {self.KEY_CONTINUE} para começar ou {self.KEY_NEXT} para voltar."
        )
        while True:
            if keyboard.is_pressed(self.KEY_CONTINUE.key):
                time.sleep(0.5)
                break
            if keyboard.is_pressed(self.KEY_STOP.key):
                spinner()
                return

        pyautogui.write(row["name"], interval=0.02)
        time.sleep(0.2)

        pyautogui.press("tab", presses=7, interval=0.005)
        time.sleep(0.2)

        pyautogui.write(str(row["pis_pasep"]), interval=0.02)
        time.sleep(0.2)

        pyautogui.press("tab")
        time.sleep(0.2)

        spinner(
            wait_string="[yellow]Processando PIS-PASEP[/yellow]",
            wait_time=5,
        )
        print(
            f"PIS-PASEP: [yellow]{row['pis_pasep']}[/]\nAperte {self.KEY_CONTINUE} para continuar."
        )
        while True:
            if keyboard.is_pressed(self.KEY_CONTINUE.key):
                time.sleep(0.5)
                break
        print("[bold green]Continuando![/bold green]")

        pyautogui.press("tab")
        time.sleep(0.2)

        pyautogui.write(str(row["cpf"]), interval=0.02)
        time.sleep(0.2)

        for i in range(5):
            pyautogui.hotkey("shift", "tab")
            time.sleep(0.005)

        pyautogui.write(row["birth_date"], interval=0.02)
        time.sleep(0.2)

        pyautogui.hotkey("shift", "tab")
        time.sleep(0.1)

        pyautogui.write(row["sex"], interval=0.02)
        time.sleep(0.2)

        pyautogui.press("tab", presses=19, interval=0.005)
        time.sleep(0.2)

        pyautogui.write("es", interval=0.02)
        time.sleep(0.2)

        pyautogui.press("tab")
        time.sleep(0.2)

        pyautogui.write(str(row["id"]), interval=0.02)
        time.sleep(0.2)

        pyautogui.press("tab", presses=2, interval=0.005)
        time.sleep(0.2)

        pyautogui.write(row["admission_date"], interval=0.02)
        time.sleep(0.2)

        pyautogui.press("tab", presses=3, interval=0.005)
        time.sleep(0.2)

        pyautogui.write("12345", interval=0.02)
        time.sleep(0.5)

        pyautogui.press("tab", presses=7, interval=0.005)
        time.sleep(0.2)

        pyautogui.write(row["position"], interval=0.02)
        time.sleep(0.2)

        pyautogui.press("tab", presses=2, interval=0.005)
        time.sleep(0.2)

        pyautogui.write(row["department"][:15], interval=0.02)
        time.sleep(0.2)

        pyautogui.press("tab", presses=3, interval=0.005)
        time.sleep(0.2)

        pyautogui.scroll(-350)
        time.sleep(0.2)

        pyautogui.press("space")
        time.sleep(0.2)

        print(
            f"Insira o Departamento\n[yellow]{row['department']}\n[/]Pressione {self.KEY_NEXT} para o próximo funcionário..."
        )

        while True:
            if keyboard.is_pressed(self.KEY_NEXT.key):
                time.sleep(0.5)
                return
