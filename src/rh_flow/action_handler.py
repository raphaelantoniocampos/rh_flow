from dataclasses import dataclass
from time import sleep

import inquirer
import keyboard
import pyautogui
from rich import print
from pyperclip import copy
import pandas as pd

from config import Config
from data_manager import DataManager
from pathlib import Path
from action import Action


@dataclass
class Key:
    key: str
    colored: str


KEY_SEMI_AUTO = Key("F4", "[bold cyan1]F4[/bold cyan1]")
KEY_CONTINUE = Key("F2", "[bold green1]F2[/bold green1]")
KEY_NEXT = Key("F3", "[bold yellow]F3[/bold yellow]")
KEY_STOP = Key("F5", "[bold red3]F5[/bold red3]")


class ActionHandler:
    def __init__(self, working_dir: Path, config: Config, data_manager: DataManager):
        self.data_dir_path = Path(working_dir / "data")
        self.config = config
        self.data_manager = data_manager
        self.actions = self.get_actions()

    def run(self):
        while True:
            option: str = self._show_actions_menu()[3:]
            if option == "Sair":
                return
            for action in self.actions:
                if option == action.option:
                    sleep(1)
                    if action.length == 0:
                        print(action.order_string)
                        return
                    self._prepare_list_and_run(action)

    def get_actions(self) -> list[Action]:
        return [
            Action("new", self._add_employees),
            Action("dismissed", self._remove_employees),
            Action("position", None),
            Action("absences", None),
        ]

    def _prepare_list_and_run(
        self,
        action: Action,
    ):
        sleep(1)
        ignore_ids = self.config.data.get("ignore", {}).keys()
        action.df = action.df[~action.df["id"].isin(ignore_ids)]
        print(action.order_string)
        see_list = inquirer.prompt(
            [
                inquirer.Confirm(
                    "yes",
                    message="Ver lista de funcionários",
                )
            ]
        )

        if see_list["yes"] is None:
            return

        see_list: dict[str, bool] = see_list["yes"]
        if see_list:
            sleep(0.5)
            df = self.config.update_employees_to_ignore(action)

        ok_input = inquirer.prompt(
            [inquirer.Confirm("yes", message="Começar?", default="yes")]
        )
        sleep(0.5)
        if not ok_input["yes"]:
            return

        action.fun(df)

    def _show_actions_menu(self) -> dict[str, str]:
        options = []

        for action in self.actions:
            options.append(action.option)

        choices = [f"{index}. {order}" for index, order in enumerate(options, start=1)]
        choices.append(f"{len(choices) + 1}. Sair")
        questions = [
            inquirer.List("option", message="Selecione uma opção", choices=choices),
        ]
        answers = inquirer.prompt(questions)
        return answers["option"]

    def _add_employees(self, df: pd.DataFrame) -> None:
        for i, series in df.iterrows():
            print(
                f"\n[bold yellow]{'-' * 15} NOVO FUNCIONÁRIO! {'-' * 15}[/bold yellow]"
            )
            print(series)
            print(
                f"\nPressione {KEY_SEMI_AUTO.colored} para o processo [bold white]semi automático[/bold white]."
            )
            print(
                f"Pressione {KEY_CONTINUE.colored} para o próximo [bold white]campo[/bold white]."
            )
            print(
                f"Pressione {KEY_NEXT.colored} para próximo [bold white]funcionário[/bold white]."
            )
            print(f"Pressione {KEY_STOP.colored} para [bold white]sair...[/bold white]")
            for index, field in series.items():
                if index == "id":
                    continue
                copy(field)
                print(f"({index} '{field}' copiado para a área de transferência!)")
                while True:
                    if keyboard.is_pressed(KEY_SEMI_AUTO.key):
                        sleep(0.5)
                        self._semi_aunew(series)
                        break
                    if keyboard.is_pressed(KEY_CONTINUE.key):
                        sleep(0.5)
                        break
                    if keyboard.is_pressed(KEY_NEXT.key):
                        break
                    if keyboard.is_pressed(KEY_STOP.key):
                        sleep(0.5)
                        print("Interrompido pelo usuário.")
                        return
                if keyboard.is_pressed(KEY_NEXT.key):
                    sleep(0.5)
                    break

    def _remove_employees(self, df):
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
                f"Pressione {KEY_CONTINUE.colored} para copiar a [bold white]Data de Desligamento[/bold white]."
            )
            print(
                f"Pressione {KEY_NEXT.colored} para próximo [bold white]funcionário[/bold white]."
            )
            print(f"Pressione {KEY_STOP.colored} para [bold white]sair...[/bold white]")
            name = series["name"]
            print(f"(name '{name}' copiado para a área de transferência!)")
            copy(name)
            while True:
                if keyboard.is_pressed(KEY_CONTINUE.key):
                    date = series["dismissal_date"]
                    print(f"(id '{date}' copiado para a área de transferência!)")
                    copy(date)
                    sleep(0.5)
                    continue
                if keyboard.is_pressed(KEY_NEXT.key):
                    sleep(0.5)
                    break
                if keyboard.is_pressed(KEY_STOP.key):
                    sleep(0.5)
                    print("Interrompido pelo usuário.")
                    return
            if keyboard.is_pressed(KEY_NEXT.key):
                sleep(0.5)
                continue

    def _semi_aunew(self, row):
        print(
            f"\nClique em [bright_blue]Novo Funcionário[/], clique no [bright_blue]name[/] e Aperte {KEY_SEMI_AUTO.colored} para começar ou {KEY_STOP.colored} para sair."
        )
        while True:
            if keyboard.is_pressed(KEY_SEMI_AUTO.key):
                sleep(0.5)
                break
            if keyboard.is_pressed(KEY_STOP.key):
                print("Interrompido pelo usuário.")
                return

        pyautogui.write(row["name"], interval=0.02)
        sleep(0.2)

        pyautogui.press("tab", presses=7, interval=0.005)
        sleep(0.2)

        print(f"Confira o pis_pasep e Pressione {KEY_SEMI_AUTO.colored} para continuar")
        print(str(row["pis_pasep"]))

        pyautogui.write(str(row["pis_pasep"]), interval=0.02)
        sleep(0.2)

        pyautogui.press("tab")
        sleep(0.2)
        while True:
            if keyboard.is_pressed(KEY_SEMI_AUTO.key):
                sleep(0.1)
                break

        sleep(0.2)

        pyautogui.press("tab")
        sleep(0.2)

        pyautogui.write(str(row["cpf"]), interval=0.02)
        sleep(0.2)

        for i in range(5):
            pyautogui.hotkey("shift", "tab")
            sleep(0.005)

        pyautogui.write(row["birth_date"], interval=0.02)
        sleep(0.2)

        pyautogui.hotkey("shift", "tab")
        sleep(0.1)

        pyautogui.write(row["sex"], interval=0.02)
        sleep(0.2)

        pyautogui.press("tab", presses=19, interval=0.005)
        sleep(0.2)

        pyautogui.write("es", interval=0.02)
        sleep(0.2)

        pyautogui.press("tab")
        sleep(0.2)

        pyautogui.write(str(row["id"]), interval=0.02)
        sleep(0.2)

        pyautogui.press("tab", presses=2, interval=0.005)
        sleep(0.2)

        pyautogui.write(row["admission_date"], interval=0.02)
        sleep(0.2)

        pyautogui.press("tab", presses=3, interval=0.005)
        sleep(0.2)

        pyautogui.write("12345", interval=0.02)
        sleep(0.5)

        pyautogui.press("tab", presses=7, interval=0.005)
        sleep(0.2)

        pyautogui.write(row["position"], interval=0.02)
        sleep(0.2)

        pyautogui.press("tab", presses=2, interval=0.005)
        sleep(0.2)

        pyautogui.write(row["location"][:15], interval=0.02)
        sleep(0.2)

        pyautogui.press("tab", presses=3, interval=0.005)
        sleep(0.2)

        pyautogui.scroll(-350)
        sleep(0.2)

        pyautogui.press("space")
        sleep(0.2)

        print(
            f"Insira a Localização\n[yellow]{row['location']}\n[/]Pressione {KEY_NEXT.colored} para o próximo funcionário..."
        )

        while True:
            if keyboard.is_pressed(KEY_NEXT.key):
                return
