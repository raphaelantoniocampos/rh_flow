from dataclasses import dataclass
from time import sleep

import inquirer
import keyboard
import pyautogui
from rich import print
from pyperclip import copy


@dataclass
class Key:
    key: str
    colored: str


class ActionHandler:
    KEY_SEMI_AUTO = Key("F4", "[bold cyan1]F4[/bold cyan1]")
    KEY_CONTINUE = Key("F2", "[bold green1]F2[/bold green1]")
    KEY_NEXT = Key("F3", "[bold yellow]F3[/bold yellow]")
    KEY_STOP = Key("F5", "[bold red3]F5[/bold red3]")

    def __init__(self, actions, data_manager):
        self.actions = actions
        self.data_manager = data_manager

        # save_dir = os.path.join(self.data_dir, "to_do")
        # if not new_employees.empty:
        #     new_employees.to_csv(
        #         os.path.join(save_dir, "new_employees.csv"), index=False, encoding="utf-8"
        #     )

    def run(self):
        option = self._show_actions_menu()
        match option[3:]:
            case "Adicionar funcionários":
                df = self.actions.to_add
                sleep(1)
                print(f"Novos funcionários para Adicionar no Ahgora: {len(df)}")
                see_list = inquirer.prompt(
                    [
                        inquirer.Confirm(
                            "yes",
                            message="Ver lista de funcionários",
                        )
                    ]
                )
                if see_list["yes"]:
                    sleep(0.5)
                    df = self.data_manager.update_employees_to_ignore(df)

                ok_input = inquirer.prompt(
                    [inquirer.Confirm("yes", message="Começar?")]
                )
                sleep(0.5)
                if not ok_input["yes"]:
                    return
                self.add_employees(df)

            case "Remover funcionários":
                sleep(1)
                self.remove_employees(self.actions.to_remove)

            case "Sair":
                return

    def _show_actions_menu(self):
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

    def add_employees(self, df):
        for i, series in df.iterrows():
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

    def remove_employees(self, df):
        print(f"Novos funcionários para Remover do Ahgora: {len(df)}")
        ok_input = inquirer.prompt([inquirer.Confirm("yes", message="Começar?")])
        sleep(0.5)
        if not ok_input["yes"]:
            return

    def _semi_auto_add(self, row):
        print(
            f"\nClique em [bright_blue]Novo Funcionário[/], clique no [bright_blue]Nome[/] e Aperte {self.KEY_SEMI_AUTO.colored} para começar ou {self.KEY_STOP.colored} para sair."
        )
        while True:
            if keyboard.is_pressed(self.KEY_SEMI_AUTO.key):
                sleep(0.5)
                break
            if keyboard.is_pressed(self.KEY_STOP.key):
                sleep(0.1)
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
