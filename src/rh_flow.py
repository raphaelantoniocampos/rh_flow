import os
from dataclasses import dataclass

import inquirer
from pandas import DataFrame
from rich import print
from rich.console import Console
from rich.panel import Panel

from exporter import Exporter
from synchronizer import Synchronizer
from updater import Updater

WORKING_DIR = os.getcwd()

console = Console()

OPTIONS = {
    1: "Exportar Dados",
    2: "Sincronizar Dados",
    3: "Adicionar Funcionários ao Ahgora",
    4: "Sair",
}


@dataclass
class DataToProcess:
    to: str | None
    df: DataFrame | None
    length: int | None


def main():
    data_to_process = []
    while True:
        try:
            option = show_menu(data_to_process)
            match option:
                case "Exportar Dados":
                    exporter = Exporter(WORKING_DIR)
                    exporter.run()

                case "Sincronizar Dados":
                    sync = Synchronizer(WORKING_DIR)
                    new_employees, dismissed_employees = sync.run()
                    data_to_process.append(
                        DataToProcess("Adicionar Funcionários ao Ahgora", new_employees, len(new_employees))
                    )
                    data_to_process.append(
                        DataToProcess("Desligar Funcionários no Ahgora", dismissed_employees, len(dismissed_employees))
                    )

                case "Adicionar Funcionários ao Ahgora":
                    updater = Updater()
                    updater.add_employees(data_to_process["Add"])

                case "Sair":
                    break

        except KeyboardInterrupt:
            break

    print("Saindo...")


def show_menu(data_to_process: dict):
    console.print(
        Panel.fit(
            f"{'-' * 13}RH FLOW{'-' * 13}\nBem-vindo ao Sistema de. Automação",
            style="bold blue",
        )
    )
    console.print("\n")
    match data_to_process:
        case []:
            console.print("[green]Sem novos dados para processar.\n")
        case _:
            console.print("[yellow]Existem dados para processar:\n")
            for data in data_to_process:
                console.print(
                    f"[bold cyan]•[/] {data.to}: {data.length}\n--- RESUMO ---{data.df}\n"
                )

    questions = [
        inquirer.List(
            "option",
            message="Selecione uma opção",
            choices=OPTIONS.values(),
        ),
    ]
    answers = inquirer.prompt(questions)
    return answers["option"]


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
