
from tasks.task import Task
from tasks.task_runner import TaskRunner


class ChangePositionsTask(TaskRunner):
    def __init__(self, task: Task):
        super().__init__(task)

    # def menu():
    #     console = Console()
    #     console.print(
    #         Panel.fit(
    #             "Alterar Cargos",
    #             style="bold cyan",
    #         )
    #     )
    #
    #     proceed = inquirer.confirm(message="Proceed?", default=True).execute()
    #     if proceed:
    #         cpt = ChangePositionsTask()
    #         cpt.run()
    #     return

    def run(self, task:Task):
        return
