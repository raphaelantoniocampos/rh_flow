import time
from pyperclip import copy
from rich import print

from rh_flow.models.task import Task
from rh_flow.tasks.task_runner import TaskRunner
from rh_flow.utils.constants import spinner
from rh_flow.models.key import Key, wait_key_press


class RemoveEmployeesTask(TaskRunner):
    KEY_CONTINUE = Key("F2", "green", "continuar")
    KEY_NEXT = Key("F3", "yellow", "próximo")
    KEY_STOP = Key("F4", "red3", "sair")

    def __init__(self, task: Task):
        super().__init__(task)

    def run(self):
        df = self.task.df

        print(
            "Abra o [bold violet]Ahgora[/bold violet] e vá para a página de funcionários."
        )
        url = "https://app.ahgora.com.br/funcionarios"
        copy(url)
        print(f"Link '{url}' copiado para a área de transferência!)")
        wait_key_press(self.KEY_CONTINUE)
        for i, series in df.iterrows():
            print(
                f"\n[bold yellow]{'-' * 15} FUNCIONÁRIO DESLIGADO! {'-' * 15}[/bold yellow]"
            )
            print(series)
            name = series["name"]
            copy(name)
            print(f"(Nome '{name}' copiado para a área de transferência!)")
            match wait_key_press([self.KEY_CONTINUE, self.KEY_NEXT, self.KEY_STOP]):
                case "continuar":
                    spinner("Continuando")
                    date = series["dismissal_date"]
                    print(f"(DATA '{date}' copiado para a área de transferência!)")
                    copy(date)
                    time.sleep(0.5)
                    wait_key_press(self.KEY_CONTINUE)
                case "próximo":
                    spinner("Continuando")
                case "sair":
                    super().exit_task()
                    spinner()
                    return

        print("[bold green]Não há mais funcionários desligados![/bold green]")
        super().exit_task()
