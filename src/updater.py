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


class Updater:
    KEY_SEMI_AUTO = Key("F1", "[bold cyan1]F2[/bold cyan1]")
    KEY_CONTINUE = Key("F2", "[bold green1]F2[/bold green1]")
    KEY_NEXT = Key("F3", "[bold yellow]F3[/bold yellow]")
    KEY_STOP = Key("F4", "[bold red3]F4[/bold red3]")

    def run(self):
        questions = [
            inquirer.List(
                "option",
                message="Selecione uma opção",
                choices=[
                    "1. Adicionar Funcionários",
                    "2. Adição de Funcionários ao Ahgora",
                    "3. Sair",
                ],
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

    def _manual_add(df, verb: str):
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
                f"\nPressione {KEY_SEMI_AUTO.colored} para o processo [bold white]semi automático[/bold white]."
            )
            print(
                f"Pressione {KEY_CONTINUE.colored} para o próximo [bold white]campo[/bold white]."
            )
            print(
                f"Pressione {KEY_NEXT.colored} para próximo [bold white]funcionário[/bold white]."
            )
            print(f"Pressione {KEY_STOP.colored} para [bold white]sair...[/bold white]")
            name = series.iloc(0)[0]
            copy(name)
            print(f"(Nome '{name}' copiado para a área de transferência!)")
            for index, field in series.items():
                if index == 0:
                    continue
                copy(field)
                print(f"({index} '{field}' copiado para a área de transferência!)")
                while True:
                    if keyboard.is_pressed(KEY_SEMI_AUTO.key):
                        sleep(0.5)
                        _semi_auto_add(series)
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

    def _semi_auto_add(row):
        print(
            f"\nClique em [bright_blue]Novo Funcionário[/], clique no [bright_blue]Nome[/] e Aperte {KEY_SEMI_AUTO.colored} para começar ou {KEY_STOP} para sair."
        )
        while True:
            if keyboard.is_pressed(KEY_SEMI_AUTO.key):
                sleep(0.5)
                break
            if keyboard.is_pressed(KEY_STOP.key):
                sleep(0.1)
                print("Interrompido pelo usuário.")
                return

        pyautogui.write(row["Nome"], interval=0.02)
        sleep(0.2)

        pyautogui.press("tab", presses=7, interval=0.005)
        sleep(0.2)

        print(f"Confira o PIS-PASEP e Pressione {KEY_SEMI_AUTO.colored} para continuar")
        print(str(row["PIS-PASEP"]))

        pyautogui.write(str(row["PIS-PASEP"]), interval=0.2)
        sleep(0.2)

        pyautogui.press("tab")
        sleep(0.2)
        while True:
            if keyboard.is_pressed(KEY_SEMI_AUTO.colored):
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
            f"Insira a Localização\n[yellow]{row['Localizacao']}\n[/]Pressione {KEY_NEXT.colored} para sair..."
        )

        while True:
            if keyboard.is_pressed(KEY_NEXT.key):
                return
