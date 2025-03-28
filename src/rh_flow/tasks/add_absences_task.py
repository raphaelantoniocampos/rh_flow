import os
import tempfile
from pathlib import Path

from pyperclip import copy
from rich import print

from rh_flow.managers.file_manager import FileManager
from rh_flow.models.key import Key, wait_key_press
from rh_flow.models.task import Task
from rh_flow.tasks.task_runner import TaskRunner
from rh_flow.utils.constants import DATA_DIR, spinner


class AddAbsencesTask(TaskRunner):
    KEY_CONTINUE = Key("F2", "green", "continuar")
    KEY_STOP = Key("F4", "red3", "sair")

    def __init__(self, task: Task):
        with tempfile.TemporaryDirectory() as tmpdirname:
            self.temp_dir_path = Path(tmpdirname)
            super().__init__(task)

    def run(self):
        print(f"\n[bold yellow]{'-' * 15} AFASTAMENTOS! {'-' * 15}[/bold yellow]")
        absences = (DATA_DIR / "fiorilli" / "absences.csv").read_bytes()

        temp_absences = self.temp_dir_path / "absences.csv"
        filter_file = self.temp_dir_path / "filter.txt"
        new_absences_file = self.temp_dir_path / "new_absences.txt"

        temp_absences.write_bytes(absences)

        self.insert_file("absences.csv")
        if wait_key_press([self.KEY_CONTINUE, self.KEY_STOP]) == "sair":
            return

        spinner("Aguarde", 1)
        print(
            "\nInsira os erros de registros no arquivo e salve (Ctrl+S) no arquivo [violet]filter.txt[/]"
        )
        filter_file.touch()
        os.startfile(filter_file)

        if wait_key_press([self.KEY_CONTINUE, self.KEY_STOP]) == "sair":
            return

        spinner("Aguarde", 1)

        filter_numbers_file = self.read_filter_numbers(filter_file)

        file_size = self.filter_lines(
            temp_absences, new_absences_file, filter_numbers_file
        )

        if file_size == 0:
            print("\nNenhum novo afastamento.")
            self.exit_task(temp_absences)

        print(f"\n[bold]{file_size} NOVOS AFASTAMENTOS![/bold]\n")
        print(
            "Arquivo '[bold green]new_absences.txt[/bold green]' gerado com sucesso!"
        )

        self.insert_file("new_absences.txt")
        wait_key_press(self.KEY_CONTINUE)

        spinner("Aguarde", 1)
        self.exit_task(temp_absences)
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

    def insert_file(self, file_name):
        print(
            f"Insira o arquivo [bold green]{file_name}[/bold green] na importação de afastamentos AHGORA."
        )
        print("Selecione [bold white]pw_afimport_01[/bold white].")
        print("Clique em [white on dark_green] Obter Registros[/white on dark_green].")
        copy(str(self.temp_dir_path))
        print(
            f"Caminho '{str(self.temp_dir_path)}' copiado para a área de transferência!)\n"
        )

    def exit_task(self, temp_absences):
        file_manager = FileManager()
        file_manager.move_file(
            source=temp_absences,
            destination=DATA_DIR / "tasks" / "absences.csv",
        )
        super().exit_task(download=False)
        spinner()
