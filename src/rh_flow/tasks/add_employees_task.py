import time
import pyautogui
import pandas as pd
from rich.panel import Panel
from rich.console import Console
from InquirerPy import inquirer
import keyboard
from pyperclip import copy


class AddEmployeesTask:
    @staticmethod
    def menu():
        console = Console()
        console.print(
            Panel.fit(
                "Adicionar Funcionários",
                style="bold cyan",
            )
        )

        proceed = inquirer.confirm(message="Continuar?", default=True).execute()
        if proceed:
            aet = AddEmployeesTask()
            aet.run()
        with console.status("[bold green]Voltando...[/bold green]", spinner="dots"):
            time.sleep(0.5)
        return

    def run(self, df: pd.DataFrame) -> None:
        for i, series in df.iterrows():
            print(
                f"\n[bold yellow]{'-' * 15} NOVO FUNCIONÁRIO! {'-' * 15}[/bold yellow]"
            )
            print(series)
            print(
                f"\nPressione {super().KEY_CONTINUE} para [bold white]adicionar[/bold white] o funcionário."
            )
            print(
                f"Pressione {super().KEY_NEXT} para o [bold white]próximo[/bold white] funcionário."
            )
            print(f"Pressione {super().KEY_STOP} para [bold white]sair...[/bold white]")
            name = series.get("name")
            copy(name)
            print(f"Nome '{name}' copiado para a área de transferência!)")
            while True:
                if keyboard.is_pressed(super().KEY_CONTINUE.key):
                    time.sleep(0.5)
                    self._auto_new(series)
                    break
                if keyboard.is_pressed(super().KEY_NEXT.key):
                    time.sleep(0.5)
                    break
                if keyboard.is_pressed(super().KEY_STOP.key):
                    time.sleep(0.5)
                    print("Interrompido pelo usuário.")
                    return

    def _auto_new(self, row):
        print(
            f"\nClique em [bright_blue]Novo Funcionário[/], clique no [bright_blue]Nome[/] e Aperte {super().KEY_CONTINUE} para começar ou {super().KEY_NEXT} para voltar."
        )
        while True:
            if keyboard.is_pressed(super().KEY_CONTINUE.key):
                time.sleep(0.5)
                break
            if keyboard.is_pressed(super().KEY_STOP.key):
                print("Interrompido pelo usuário.")
                return

        pyautogui.write(row["name"], interval=0.02)
        time.sleep(0.2)

        pyautogui.press("tab", presses=7, interval=0.005)
        time.sleep(0.2)

        pyautogui.write(str(row["pis_pasep"]), interval=0.02)
        time.sleep(0.2)

        pyautogui.press("tab")
        time.sleep(0.2)

        self._process_pis_pasep(3)

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

        pyautogui.write(row["location"][:15], interval=0.02)
        time.sleep(0.2)

        pyautogui.press("tab", presses=3, interval=0.005)
        time.sleep(0.2)

        pyautogui.scroll(-350)
        time.sleep(0.2)

        pyautogui.press("space")
        time.sleep(0.2)

        print(
            f"Insira a Localização\n[yellow]{row['location']}\n[/]Pressione {super().KEY_NEXT} para o próximo funcionário..."
        )

        while True:
            if keyboard.is_pressed(super().KEY_NEXT.key):
                time.sleep(0.5)
                return

    def _process_pis_pasep(self, time):
        console = Console()
        with console.status(
            "[yellow]Processando pis_pasep...[/yellow]", spinner="dots"
        ):
            time.sleep(time)

        console.print("[bold green]Continuando![/bold green]")
        return
