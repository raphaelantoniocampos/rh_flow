from time import sleep

from fiorilli_app import FiorilliApp
from rich import print

INTERVAL = 0.2
WRITE_INTERVAL = 0.01


class Exporter:
    def __init__(self, working_dir):
        self.working_dir = working_dir

    def run(self):
        fiorilli_app = FiorilliApp(
            working_dir=self.working_dir,
            interval=INTERVAL,
            write_interval=WRITE_INTERVAL,
        )

        print("--- Iniciando Exportação ---")
        fiorilli_app.export_data()

        print("[bold green]--- Exportação Concluida ---[/bold green]")
        sleep(1)

        # for file_name in os.listdir(data_dir):
        #     file_path = os.path.join(data_dir, file_name)
        #     if os.path.getsize(file_path) == 0:
        #         os.remove(file_path)
        #
        # afastamentos = [
        #     file_name
        #     for file_name in os.listdir(data_dir)
        #     if os.getsize(os.path.join(data_dir, file_name)) > 0
        # ]
        #
        # if afastamentos:
        #     df_list = [
        #         read_csv(os.path.join(data_dir, file_name), sep=",", header=None)
        #         for file_name in afastamentos
        #     ]
        #     afastamentos_df = os.path.concat(df_list)
        #     afastamentos_df.columns = [
        #         "Matricula",
        #         "Motivo",
        #         "Data Inicio",
        #         "Hora Inicio",
        #         "Data Fim",
        #         "Hora Fim",
        #     ]
        #     print("--- Afastamentos Baixados ---")
        #     print(afastamentos_df)
        #
        #     start_import = input("Iniciar Importação? (s/n)")
        #     if start_import == "s" or start_import == "":
        #         ahgora_app = AhgoraApp(
        #             download_dir=data_dir,
        #             assets_path=join(working_dir, "leaves", "ahgora_app", "assets"),
        #             interval=INTERVAL,
        #             write_interval=WRITE_INTERVAL,
        #             import_files=afastamentos,
        #         )
        #         ahgora_app.run()
        # else:
        #     print(f"Nenhum afastamento pro dia {export_date}.")
        #
        # sleep(1)
        # print("--- Concluído ---")
        # sleep(1)
        # print("--- Fechando Automação ---")
        # sleep(3)
