from rich.console import Console

import time
from pathlib import Path

import inquirer
import keyboard
import pandas as pd
import pyautogui
from action import Action
from config import Config
from data_manager import DataManager
from pyperclip import copy
from rich import print


class Key:
    def __init__(self, name: str, color: str):
        self.name = name
        self.color = color
        self.key = str(name)

    def __str__(self):
        return f"[bold {self.color}]{self.name.upper()}[/bold {self.color}]"


KEY_CONTINUE = Key("F2", "green3")
KEY_NEXT = Key("F3", "yellow1")
KEY_STOP = Key("F4", "red3")


class ActionHandler:
    def __init__(self, base_dir_path: Path, config: Config, data_manager: DataManager):
        self.data_dir_path = Path(base_dir_path / "data")
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
            # self.name_to_action("absences"),
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
                action.df = self.config.update_employees_to_ignore(action)

            ok_input = inquirer.prompt(
                [inquirer.Confirm("yes", message="Começar?", default="yes")]
            )
            time.sleep(0.5)
            if not ok_input["yes"]:
                return

            action.fun(action.df)

    def _show_actions_menu(self, actions) -> dict[str, str]:
        options = []

        for action in actions:
            options.append(action.option)

        choices = [f"{index}. {order}" for index, order in enumerate(options, start=1)]
        choices.append(f"{len(choices) + 1}. Voltar")
        questions = [
            inquirer.List(
                "option", message="Selecione uma opção", choices=choices, carousel=True
            ),
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
                f"\nPressione {KEY_CONTINUE} para [bold white]adicionar[/bold white] o funcionário."
            )
            print(
                f"Pressione {KEY_NEXT} para o [bold white]próximo[/bold white] funcionário."
            )
            print(f"Pressione {KEY_STOP} para [bold white]sair...[/bold white]")
            name = series.get("name")
            copy(name)
            print(f"Nome '{name}' copiado para a área de transferência!)")
            while True:
                if keyboard.is_pressed(KEY_CONTINUE.key):
                    time.sleep(0.5)
                    self._auto_new(series)
                    break
                if keyboard.is_pressed(KEY_NEXT.key):
                    time.sleep(0.5)
                    break
                if keyboard.is_pressed(KEY_STOP.key):
                    time.sleep(0.5)
                    print("Interrompido pelo usuário.")
                    return

    def _auto_new(self, row):
        print(
            f"\nClique em [bright_blue]Novo Funcionário[/], clique no [bright_blue]Nome[/] e Aperte {KEY_CONTINUE} para começar ou {KEY_NEXT} para voltar."
        )
        while True:
            if keyboard.is_pressed(KEY_CONTINUE.key):
                time.sleep(0.5)
                break
            if keyboard.is_pressed(KEY_STOP.key):
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
            f"Insira a Localização\n[yellow]{row['location']}\n[/]Pressione {KEY_NEXT} para o próximo funcionário..."
        )

        while True:
            if keyboard.is_pressed(KEY_NEXT.key):
                time.sleep(0.5)
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
                if keyboard.is_pressed(KEY_CONTINUE.key):
                    date = series["dismissal_date"]
                    print(f"(id '{date}' copiado para a área de transferência!)")
                    copy(date)
                    time.sleep(0.5)
                    continue
                if keyboard.is_pressed(KEY_NEXT.key):
                    time.sleep(0.5)
                    break
                if keyboard.is_pressed(KEY_STOP.key):
                    time.sleep(0.5)
                    print("Interrompido pelo usuário.")
                    return
            if keyboard.is_pressed(KEY_NEXT.key):
                time.sleep(0.5)
                continue

    def _process_pis_pasep(self, time):
        console = Console()
        with console.status(
            "[yellow1]Processando pis_pasep...[/yellow1]", spinner="dots"
        ):
            time.sleep(time)

        console.print("[bold green3]Continuando![/bold green3]")
        return
