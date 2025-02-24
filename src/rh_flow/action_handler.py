from dataclasses import dataclass
from time import sleep

import inquirer
import keyboard
import pyautogui
from rich import print
from pyperclip import copy
import pandas as pd

from data_manager import Actions
from config import Config


@dataclass
class Key:
    key: str
    colored: str


class ActionHandler:
    KEY_SEMI_AUTO = Key("F4", "[bold cyan1]F4[/bold cyan1]")
    KEY_CONTINUE = Key("F2", "[bold green1]F2[/bold green1]")
    KEY_NEXT = Key("F3", "[bold yellow]F3[/bold yellow]")
    KEY_STOP = Key("F5", "[bold red3]F5[/bold red3]")

    NO_EMPLOYEE_TO_ADD_STR = "[bold yellow]Nenhum novo funcionário para adicionar no momento.[/bold yellow]\n"
    NO_EMPLOYEE_TO_REMOVE_STR = "[bold yellow]Nenhum funcionário para remover do Ahgora no momento.[/bold yellow]\n"

    def __init__(self, actions: Actions, config: Config):
        self.actions: Actions = actions
        self.config: Config = config

    def run(self):
        while True:
            option: str = self._show_actions_menu()[3:]
            match option:
                case "Adicionar funcionários":
                    sleep(1)
                    if self.actions.to_add is None:
                        print(self.NO_EMPLOYEE_TO_ADD_STR)
                        return
                    df: pd.DataFrame = self.actions.to_add
                    self._prepare_list_and_run(
                        df,
                        self.NO_EMPLOYEE_TO_ADD_STR,
                        "add",
                        self._add_employees,
                    )
                    break

                case "Remover funcionários":
                    sleep(1)
                    if self.actions.to_remove is None:
                        print(self.NO_EMPLOYEE_TO_REMOVE_STR)
                        return
                    df: pd.DataFrame = self.actions.to_remove
                    self._prepare_list_and_run(
                        df,
                        self.NO_EMPLOYEE_TO_REMOVE_STR,
                        "remove",
                        self._remove_employees,
                    )
                    break

                case "Sair":
                    return

    def _prepare_list_and_run(
        self,
        df: pd.DataFrame,
        no_employee_str: str,
        to: str,
        action_function,
    ):
        if to == "add":
            action_to_str = "Adicionar no Ahgora"
        if to == "remove":
            action_to_str = "Remover do Ahgora"

        if df.empty:
            print(no_employee_str)
            return

        sleep(1)
        print(f"Novos funcionários para {action_to_str}: {len(df)}")
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
            df = self.config.update_employees_to_ignore(df, to)

        ok_input = inquirer.prompt([inquirer.Confirm("yes", message="Começar?")])
        sleep(0.5)
        if not ok_input["yes"]:
            return

        if df.empty:
            print(no_employee_str)
            return

        action_function(df)

    def _show_actions_menu(self) -> dict[str, str]:
        actions = []

        if self.actions.to_add is not None:
            actions.append("Adicionar funcionários")

        if self.actions.to_remove is not None:
            actions.append("Remover funcionários")

        if not actions:
            actions.append("[green]• N[enhuma ação pendente.[/green]")

        choices = [
            f"{index}. {action}" for index, action in enumerate(actions, start=1)
        ]
        choices.append(f"{len(choices) + 1}. Sair")
        questions = [
            inquirer.List("option", message="Selecione uma opção", choices=choices),
        ]
        answers = inquirer.prompt(questions)
        return answers["option"]

    def _add_employees(self, df: pd.DataFrame) -> None:
        for i, series in df.iterrows():
            if df.empty:
                print(
                    "[bold yellow]Nenhum novo funcionário para adicionar no momento.[/bold yellow]\n"
                )
                return
            print(
                f"\n[bold yellow]{'-' * 15} NOVO FUNCIONÁRIO! {'-' * 15}[/bold yellow]"
            )
            print(series)
            print(
                f"\nPressione {self.KEY_SEMI_AUTO.colored} para o processo [bold white]semi automático[/bold white]."
            )
            print(
                f"Pressione {self.KEY_CONTINUE.colored} para o próximo [bold white]campo[/bold white]."
            )
            print(
                f"Pressione {self.KEY_NEXT.colored} para próximo [bold white]funcionário[/bold white]."
            )
            print(
                f"Pressione {self.KEY_STOP.colored} para [bold white]sair...[/bold white]"
            )
            for index, field in series.items():
                if index == "Matricula":
                    continue
                copy(field)
                print(f"({index} '{field}' copiado para a área de transferência!)")
                while True:
                    if keyboard.is_pressed(self.KEY_SEMI_AUTO.key):
                        sleep(0.5)
                        self._semi_auto_add(series)
                        break
                    if keyboard.is_pressed(self.KEY_CONTINUE.key):
                        sleep(0.5)
                        break
                    if keyboard.is_pressed(self.KEY_NEXT.key):
                        break
                    if keyboard.is_pressed(self.KEY_STOP.key):
                        sleep(0.5)
                        print("Interrompido pelo usuário.")
                        return
                if keyboard.is_pressed(self.KEY_NEXT.key):
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
                f"\nPressione {self.KEY_SEMI_AUTO.colored} para o processo [bold white]semi automático[/bold white]."
            )
            print(
                f"Pressione {self.KEY_CONTINUE.colored} para o próximo [bold white]campo[/bold white]."
            )
            print(
                f"Pressione {self.KEY_NEXT.colored} para próximo [bold white]funcionário[/bold white]."
            )
            print(
                f"Pressione {self.KEY_STOP.colored} para [bold white]sair...[/bold white]"
            )
            print(f"(Nome '{df[i]['Nome']}' copiado para a área de transferência!)")
            while True:
                if keyboard.is_pressed(self.KEY_NEXT.key):
                    break
                if keyboard.is_pressed(self.KEY_STOP.key):
                    sleep(0.5)
                    print("Interrompido pelo usuário.")
                    return
            if keyboard.is_pressed(self.KEY_NEXT.key):
                sleep(0.5)
                break

    def _semi_auto_add(self, row):
        print(
            f"\nClique em [bright_blue]Novo Funcionário[/], clique no [bright_blue]Nome[/] e Aperte {self.KEY_SEMI_AUTO.colored} para começar ou {self.KEY_STOP.colored} para sair."
        )
        while True:
            if keyboard.is_pressed(self.KEY_SEMI_AUTO.key):
                sleep(0.5)
                break
            if keyboard.is_pressed(self.KEY_STOP.key):
                print("Interrompido pelo usuário.")
                return

        pyautogui.write(row["Nome"], interval=0.02)
        sleep(0.2)

        pyautogui.press("tab", presses=7, interval=0.005)
        sleep(0.2)

        print(
            f"Confira o PIS-PASEP e Pressione {self.KEY_SEMI_AUTO.colored} para continuar"
        )
        print(str(row["PIS-PASEP"]))

        pyautogui.write(str(row["PIS-PASEP"]), interval=0.02)
        sleep(0.2)

        pyautogui.press("tab")
        sleep(0.2)
        while True:
            if keyboard.is_pressed(self.KEY_SEMI_AUTO.key):
                sleep(0.1)
                break

        sleep(0.2)

        pyautogui.press("tab")
        sleep(0.2)

        pyautogui.write(str(row["CPF"]), interval=0.02)
        sleep(0.2)

        for i in range(5):
            pyautogui.hotkey("shift", "tab")
            sleep(0.005)

        pyautogui.write(row["Data Nascimento"], interval=0.02)
        sleep(0.2)

        pyautogui.hotkey("shift", "tab")
        sleep(0.1)

        pyautogui.write(row["Sexo"], interval=0.02)
        sleep(0.2)

        pyautogui.press("tab", presses=19, interval=0.005)
        sleep(0.2)

        pyautogui.write("es", interval=0.02)
        sleep(0.2)

        pyautogui.press("tab")
        sleep(0.2)

        pyautogui.write(str(row["Matricula"]), interval=0.02)
        sleep(0.2)

        pyautogui.press("tab", presses=2, interval=0.005)
        sleep(0.2)

        pyautogui.write(row["Data Admissao"], interval=0.02)
        sleep(0.2)

        pyautogui.press("tab", presses=3, interval=0.005)
        sleep(0.2)

        pyautogui.write("12345", interval=0.02)
        sleep(0.5)

        pyautogui.press("tab", presses=7, interval=0.005)
        sleep(0.2)

        pyautogui.write(row["Cargo"], interval=0.02)
        sleep(0.2)

        pyautogui.press("tab", presses=2, interval=0.005)
        sleep(0.2)

        pyautogui.write(row["Localizacao"][:15], interval=0.02)
        sleep(0.2)

        pyautogui.press("tab", presses=3, interval=0.005)
        sleep(0.2)

        pyautogui.scroll(-350)
        sleep(0.2)

        pyautogui.press("space")
        sleep(0.2)

        print(
            f"Insira a Localização\n[yellow]{row['Localizacao']}\n[/]Pressione {self.KEY_NEXT.colored} para o próximo funcionário..."
        )

        while True:
            if keyboard.is_pressed(self.KEY_NEXT.key):
                return
