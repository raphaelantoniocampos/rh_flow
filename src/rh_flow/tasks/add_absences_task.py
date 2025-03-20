try:
    from tasks.task_runner import TaskRunner
    from tasks.task import Task
except ModuleNotFoundError:
    pass


class AddAbsencesTask(TaskRunner):
    def __init__(self, task: Task):
        super().__init__(task)

    # @staticmethod
    # def menu():
    #     console = Console()
    #     console.print(
    #         Panel.fit(
    #             "Adicionar Afastamentos",
    #             style="bold cyan",
    #         )
    #     )
    #
    #
    #     proceed = inquirer.confirm(message="Continuar?", default=True).execute()
    #     if proceed:
    #         aat = AddAbsencesTask()
    #         aat.run()
    #
    #     with console.status("[bold green]Voltando...[/bold green]", spinner="dots"):
    #         time.sleep(0.25)

    def run(self):
        # Caminho para os arquivos
        registry_file = "registros.txt"  # Arquivo com as linhas de registro
        input_file = "dados.txt"  # Arquivo com as linhas a serem filtradas
        output_file = "fixed_lines.txt"  # Arquivo de saída com as linhas filtradas

        # Lê os números dos registros que devem ser removidos
        registry_numbers = self.read_registry_numbers(registry_file)

        # Filtra as linhas e escreve no arquivo de saída
        self.filter_lines(input_file, output_file, registry_numbers)

        print(f"Arquivo '{output_file}' gerado com sucesso!")

    def read_registry_numbers(self, file_path):
        """Lê o arquivo TXT e retorna uma lista com os números dos registros."""
        registry_numbers = []
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                if "Erro ao obter registros:" in line:
                    continue
                # Extrai o número do registro entre colchetes
                if "registro" in line:
                    start = line.find("[") + 1
                    end = line.find("]")
                    registry_number = int(line[start:end])
                    registry_numbers.append(registry_number)
        return registry_numbers

    def filter_lines(self, input_file, output_file, registry_numbers):
        """Filtra as linhas do arquivo de entrada e escreve no arquivo de saída."""
        with (
            open(input_file, "r", encoding="utf-8") as infile,
            open(output_file, "w", encoding="utf-8") as outfile,
        ):
            for index, line in enumerate(infile, start=1):
                # Verifica se o índice da linha não está na lista de números de registro
                if index not in registry_numbers:
                    outfile.write(line)

if __name__ == "__main__":
    AddAbsencesTask.run()
