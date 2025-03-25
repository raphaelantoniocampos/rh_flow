from rich import print

import time
import keyboard
from pyperclip import copy

from rh_flow.tasks.task import Task
from rh_flow.tasks.task_runner import TaskRunner

import os
from rh_flow.utils.constants import DATA_DIR, Key, spinner


class AddAbsencesTask(TaskRunner):
    KEY_CONTINUE = Key("F2", "green")
    KEY_STOP = Key("F4", "red3")

    def __init__(self, task: Task):
        super().__init__(task)

    def run(self):
        print(f"\n[bold yellow]{'-' * 15} AFASTAMENTOS! {'-' * 15}[/bold yellow]")

        absences_file = DATA_DIR / "tasks" / "absences.csv"
        filter_file = DATA_DIR / "tasks" / "filter.txt"
        new_absences_file = DATA_DIR / "tasks" / "new_absences.txt"

        print(
            "Insira o arquivo [bold green]absences.csv[/bold green] na importação de afastamentos AHGORA."
        )
        print("Selecione [bold white]pw_afimport_01[/bold white].")
        print("Clique em [white on dark_green] Obter Registros[/white on dark_green].")
        copy(str(absences_file.parent))
        print(
            f"Caminho '{str(absences_file.parent)}' copiado para a área de transferência!)"
        )

        if self.wait_continue_key() == "exit":
            return

        spinner("Aguarde", 10)
        print(
            "Insira os erros de registros no arquivo e salve (Ctrl+S) no arquivo [magenta]filter.txt[/]"
        )
        filter_file.unlink(missing_ok=True)
        filter_file.touch()
        os.startfile(filter_file)

        if self.wait_continue_key() == "exit":
            return

        filter_numbers_file = self.read_filter_numbers(filter_file)

        file_size = self.filter_lines(absences_file, new_absences_file, filter_numbers_file)

        if file_size == 0:
            print(
                "\nNenhum novo afastamento."
            )
            spinner(wait_time=3)
            return

        print(
            "\nArquivo '[bold green]new_absences.txt[/bold green]' gerado com sucesso!"
        )
        print(
            "Insira o arquivo [bold green]new_absences.txt[/bold green] na importação de afastamentos AHGORA."
        )
        copy(str(new_absences_file.parent))
        print(
            f"Caminho '{str(new_absences_file.parent)}' copiado para a área de transferência!)"
        )

        self.wait_continue_key()
        super().exit_task()
        spinner()
        return

    def read_filter_numbers(self, file_path):
        """Lê o arquivo TXT e retorna uma lista com os números dos registros."""
        filter_numbers = []
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                if "Erro ao obter registros:" in line:
                    continue
                if "registro" in line:
                    start = line.find("[") + 1
                    end = line.find("]")
                    filter_number = int(line[start:end])
                    filter_numbers.append(filter_number)
        return filter_numbers

    def filter_lines(self, absences_file, new_absences_file, filter_numbers_file):
        """Filtra as linhas do arquivo de entrada e escreve no arquivo de saída."""
        with (
            open(absences_file, "r", encoding="utf-8") as infile,
            open(new_absences_file, "w", encoding="utf-8") as outfile,
        ):
            lines_written = 0
            for index, line in enumerate(infile, start=1):
                if index not in filter_numbers_file:
                    outfile.write(line)
                    lines_written += 1
            return lines_written

    def wait_continue_key(self):
        print(
            f"\nPressione {self.KEY_CONTINUE} para [bold white]continuar[/bold white] ."
        )
        print(f"Pressione {self.KEY_STOP} para [bold white]sair...[/bold white]")
        while True:
            if keyboard.is_pressed(self.KEY_CONTINUE.key):
                time.sleep(0.5)
                return "continue"
            if keyboard.is_pressed(self.KEY_STOP.key):
                time.sleep(0.5)
                return "exit"
