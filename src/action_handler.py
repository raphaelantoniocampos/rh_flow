from dataclasses import dataclass
from time import sleep

import inquirer
import keyboard
import pyautogui
from pyperclip import copy


@dataclass
class Key:
    key: str
    colored: str


class ActionHandler:
    KEY_SEMI_AUTO = Key("F1", "[bold cyan1]F2[/bold cyan1]")
    KEY_CONTINUE = Key("F2", "[bold green1]F2[/bold green1]")
    KEY_NEXT = Key("F3", "[bold yellow]F3[/bold yellow]")
    KEY_STOP = Key("F4", "[bold red3]F4[/bold red3]")

    def __init__(self, actions_to_do):
        self.actions_to_do = actions_to_do

    def run(self):
        option = self._show_actions_menu()[2:]
        print(option)
        match option:
            case "Adicionar funcionários":
                print("ESSE 1")
                sleep(1)
                self.add_employees(self.actions_to_do.to_add)

            case "Remover funcionários":
                print("ESSE 2")
                sleep(1)
                self.remove_employees(self.actions_to_do.to_remove)

            case "Sair":
                print("SALIR 1")
                return

    def _show_actions_menu(self):
        actions = []

        if self.actions_to_do.to_add is not None:
            actions.append("Adicionar funcionários")

        if self.actions_to_do.to_remove is not None:
            actions.append("Remover funcionários")

        if not actions:
            actions.append("[green]• Nenhuma ação pendente.[/green]")

        choices = [f"{index}. {action}" for index, action in enumerate(actions, start=1)]
        choices.append(f"{len(choices) + 1}. Sair")
        questions = [
            inquirer.List(
                "option",
                message="Selecione uma opção",
                choices=choices
            ),
        ]
        answers = inquirer.prompt(questions)
        return answers["option"]

    def add_employees(self, df):
        print(f"Novos funcionários para Adicionar no Ahgora: {len(df)}")
        ok_input = inquirer.prompt([inquirer.Confirm("start", message="Começar?")])
        sleep(0.5)
        if not ok_input["start"]:
            return

    def remove_employees(self, df):
        print(f"Novos funcionários para Remover do Ahgora: {len(df)}")
        ok_input = inquirer.prompt([inquirer.Confirm("start", message="Começar?")])
        sleep(0.5)
        if not ok_input["start"]:
            return

    def _manual_add(self, df, verb: str):
        print(f"Novos funcionários para {verb} no Ahgora: {len(df)}")
        ok_input = inquirer.prompt([inquirer.Confirm("start", message="Começar?")])
        sleep(0.5)
        if not ok_input["start"]:
            return
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
            print(f"Pressione {self.KEY_STOP.colored} para [bold white]sair...[/bold white]")
            name = series.iloc(0)[0]
            copy(name)
            print(f"(Nome '{name}' copiado para a área de transferência!)")
            for index, field in series.items():
                if index == 0:
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

    def _semi_auto_add(self, row):
        print(
            f"\nClique em [bright_blue]Novo Funcionário[/], clique no [bright_blue]Nome[/] e Aperte {KEY_SEMI_AUTO.colored} para começar ou {KEY_STOP} para sair."
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

        print(f"Confira o PIS-PASEP e Pressione {self.KEY_SEMI_AUTO.colored} para continuar")
        print(str(row["PIS-PASEP"]))

        pyautogui.write(str(row["PIS-PASEP"]), interval=0.2)
        sleep(0.2)

        pyautogui.press("tab")
        sleep(0.2)
        while True:
            if keyboard.is_pressed(self.KEY_SEMI_AUTO.colored):
                sleep(0.1)
                break

        sleep(0.2)

        pyautogui.press("tab")
        sleep(0.2)

        pyautogui.write(row["CPF"], interval=0.02)
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

        pyautogui.write(row["Matricula"], interval=0.02)
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
            f"Insira a Localização\n[yellow]{row['Localizacao']}\n[/]Pressione {self.KEY_NEXT.colored} para sair..."
        )

        while True:
            if keyboard.is_pressed(self.KEY_NEXT.key):
                return
