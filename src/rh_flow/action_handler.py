import pandas as pd
import time

import inquirer
import keyboard
from rich import print
from pyperclip import copy

from config import Config
from data_manager import DataManager
from pathlib import Path
from action import Action


class Key:
    def __init__(self, key: str):
        self.key = key

    def __str__(self):
        return f"[bold cyan1]{self.key.upper()}[/bold cyan1]"


KEY_AUTO = Key("F4")
KEY_CONTINUE = Key("F2")
KEY_NEXT = Key("F3")
KEY_STOP = Key("F5")


class ActionHandler:
    def __init__(self, working_dir: Path, config: Config, data_manager: DataManager):
        self.data_dir_path = Path(working_dir / "data")
        self.config = config
        self.data_manager = data_manager

    def run(self, actions):
        while True:
            option: str = self._show_actions_menu(actions)[3:]
            if option == "Voltar":
                return
            for action in actions:
                if option == action.option:
                    time.sleep(1)
                    if action.len == 0:
                        print(action.order)
                        return
                    self._prepare_list_and_run(action)

    def get_actions(self) -> list[Action]:
        return [
            self.name_to_action("new"),
            self.name_to_action("dismissed"),
            self.name_to_action("position"),
            self.name_to_action("absences"),
        ]


    def name_to_action(self, name: str) -> Action:
        action = Action(name, self._action_name_to_fun(name))
        if name == "new" and not action.df.empty:
            ignore_ids = self.config.data.get("ignore", {}).keys()
            filtered_df = action.df[~action.df["id"].isin(ignore_ids)]
            action = action.update_df(filtered_df)
        return action

    def _action_name_to_fun(self, name: str):
        def fun(df):
            return

        if name == "new":
            fun = self._add_employees
        if name == "dismissed":
            fun = self._remove_employees
        if name == "position":
            fun = fun
        if name == "absences":
            fun = fun

        return fun

    def _prepare_list_and_run(
        self,
        action: Action,
    ):
        time.sleep(1)
        print(action.order)
        print("\n")
        if action.df.size > 0:
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
                time.sleep(0.5)
                df = self.config.update_employees_to_ignore(action)

            ok_input = inquirer.prompt(
                [inquirer.Confirm("yes", message="Começar?", default="yes")]
            )
            time.sleep(0.5)
            if not ok_input["yes"]:
                return

            action.fun(df)

    def _show_actions_menu(self, actions) -> dict[str, str]:
        options = []

        for action in actions:
            options.append(action.option)

        choices = [f"{index}. {order}" for index, order in enumerate(options, start=1)]
        choices.append(f"{len(choices) + 1}. Voltar")
        questions = [
            inquirer.List("option",  message="Selecione uma opção", choices=choices, carousel=True),
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
                f"\nPressione {KEY_AUTO} para o processo [bold white]semi automático[/bold white]."
            )
            print(
                f"Pressione {KEY_CONTINUE} para o próximo [bold white]campo[/bold white]."
            )
            print(
                f"Pressione {KEY_NEXT} para próximo [bold white]funcionário[/bold white]."
            )
            print(f"Pressione {KEY_STOP} para [bold white]sair...[/bold white]")
            for index, field in series.items():
                if index == "id":
                    continue
                copy(field)
                print(f"({index} '{field}' copiado para a área de transferência!)")
                while True:
                    if keyboard.is_pressed(KEY_AUTO):
                        time.sleep(0.5)
                        self._auto_new(series)
                        break
                    if keyboard.is_pressed(KEY_CONTINUE):
                        time.sleep(0.5)
                        break
                    if keyboard.is_pressed(KEY_NEXT):
                        break
                    if keyboard.is_pressed(KEY_STOP):
                        time.sleep(0.5)
                        print("Interrompido pelo usuário.")
                        return
                if keyboard.is_pressed(KEY_NEXT):
                    time.sleep(0.5)
                    break

    def _auto_new(self, row):
        print(
            f"\nClique em [bright_blue]Novo Funcionário[/], clique no [bright_blue]name[/] e Aperte {KEY_AUTO} para começar ou {KEY_STOP} para sair."
        )
        while True:
            if keyboard.is_pressed(KEY_AUTO):
                time.sleep(0.5)
                break
            if keyboard.is_pressed(KEY_STOP):
                print("Interrompido pelo usuário.")
                return

        pyautogui.write(row["name"], interval=0.02)
        time.sleep(0.2)

        pyautogui.press("tab", presses=7, interval=0.005)
        time.sleep(0.2)

        print(f"Confira o pis_pasep e Pressione {KEY_AUTO} para continuar")
        print(str(row["pis_pasep"]))

        pyautogui.write(str(row["pis_pasep"]), interval=0.02)
        time.sleep(0.2)

        pyautogui.press("tab")
        time.sleep(0.2)
        while True:
            if keyboard.is_pressed(KEY_AUTO):
                time.sleep(0.1)
                break

        time.sleep(0.2)

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
            f"Insira a Localização\n[yellow]{row['location']}\n[/]Pressione {KEY_NEXT} para o próximo funcionário..."
        )

        while True:
            if keyboard.is_pressed(KEY_NEXT):
                return

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
                f"Pressione {KEY_CONTINUE} para copiar a [bold white]Data de Desligamento[/bold white]."
            )
            print(
                f"Pressione {KEY_NEXT} para próximo [bold white]funcionário[/bold white]."
            )
            print(f"Pressione {KEY_STOP} para [bold white]sair...[/bold white]")
            name = series["name"]
            print(f"(name '{name}' copiado para a área de transferência!)")
            copy(name)
            while True:
                if keyboard.is_pressed(KEY_CONTINUE):
                    date = series["dismissal_date"]
                    print(f"(id '{date}' copiado para a área de transferência!)")
                    copy(date)
                    time.sleep(0.5)
                    continue
                if keyboard.is_pressed(KEY_NEXT):
                    time.sleep(0.5)
                    break
                if keyboard.is_pressed(KEY_STOP):
                    time.sleep(0.5)
                    print("Interrompido pelo usuário.")
                    return
            if keyboard.is_pressed(KEY_NEXT):
                time.sleep(0.5)
                continue
