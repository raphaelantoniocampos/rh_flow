from dataclasses import dataclass
import pandas as pd
import time
import os

import inquirer
from rich import print
from rich.console import Console
from rich.panel import Panel

from synchronizer import Synchronizer
from updater import Updater

WORKING_DIR = os.getcwd()

console = Console()

OPTIONS = {
    1: "Exportar",
    2: "Sincronizar",
    3: "Processar",
    4: "Sair",
}

@dataclass
class DataToProcess:
    to_add: pd.DataFrame | None
    to_remove: pd.DataFrame | None

def main():
    while True:
        try:
            data_to_process = get_data_to_process()
            option = show_menu(data_to_process)
            match option:
                case "Exportar":
                    print("[bold red]DESATIVADO NO MOMENTO[/bold red]")
                    time.sleep(1)
                    # exporter = Exporter(WORKING_DIR)
                    # exporter.run()

                case "Sincronizar":
                    sync = Synchronizer(WORKING_DIR)
                    sync.run()

                case "Processar":
                    updater = Updater()
                    updater.add_employees(data_to_process["Add"])

                case "Sair":
                    break

        except KeyboardInterrupt:
            break

    print("Saindo...")


def show_menu(data_to_process: DataToProcess):
    console.print(
        Panel.fit(
            f"{'-' * 13}RH FLOW{'-' * 13}\nBem-vindo ao Sistema de. Automação",
            style="bold blue",
        )
    )
    console.print("\n")
    if data_to_process.to_add is not None :
        console.print(f"[bold cyan]•[/] Existem {len(data_to_process.to_add)} funcionários para adicionar no Ahgora:\n")
        console.print(f"--- RESUMO ---\n{data_to_process.to_add.head()}")
    if data_to_process.to_remove is not None :
        console.print(f"[bold cyan]•[/] Existem {len(data_to_process.to_remove)} funcionários para remover do Ahgora:\n")
        console.print(f"--- RESUMO ---\n{data_to_process.to_remove.head()}")

    if data_to_process.to_add is None and data_to_process.to_remove is None:
        console.print("[green]Sem novos dados para processar.\n")

    questions = [
        inquirer.List(
            "option",
            message="Selecione uma opção",
            choices=OPTIONS.values(),
        ),
    ]
    answers = inquirer.prompt(questions)
    return answers["option"]

def get_data_to_process() -> DataToProcess:
    to_process_dir = os.path.join(WORKING_DIR, 'data', 'to_process')

    new_employees_path = os.path.join(to_process_dir, 'new_employees.csv')
    dismissed_employees_path = os.path.join(to_process_dir, 'dismissed_employees.csv')

    data_to_process = DataToProcess(None, None)

    if os.path.isfile(new_employees_path):
        df_new = pd.read_csv(new_employees_path)
        data_to_process.to_add = df_new

    if os.path.isfile(dismissed_employees_path):
        df_dismissed = pd.read_csv(dismissed_employees_path)
        data_to_process.to_remove = df_dismissed

    return data_to_process

# def select_date():
#     last_week_day = _get_last_week_day()
#     print("Selecionar a data da Exportação.")
#
#     ok_input = input(
#         f"O último dia de semana foi {last_week_day}. Deseja continuar? (s/n)\n"
#     )
#     if ok_input == "s" or not ok_input:
#         return last_week_day
#
#     done = False
#     while not done:
#         export_date = input("Digite a data da Exportação: (dd/mm/aaaa)\n")
#         if len(export_date) == 10 and export_date[2] == "/" and export_date[5] == "/":
#             confirm = input(f"Data: {export_date} está correta? (s/n)\n")
#             if confirm == "s" or not confirm:
#                 return export_date
#         if len(export_date) == 8 and export_date.isdigit():
#             export_date = f"{export_date[:2]}/{export_date[2:4]}/{export_date[4:]}"
#             confirm = input(f"Data: {export_date} está correta? (s/n)\n")
#             if confirm == "s" or not confirm:
#                 return export_date
#         print("Formato de data inválido. Tente novamente.")


# def _get_last_week_day():
#     today = datetime.now()
#     last_week_day = today - timedelta(days=1)
#
#     if last_week_day.weekday() == 5:
#         last_week_day -= timedelta(days=1)
#     elif last_week_day.weekday() == 6:
#         last_week_day -= timedelta(days=2)
#
#     return last_week_day.strftime("%d/%m/%Y")

if __name__ == "__main__":
    main()
