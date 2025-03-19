from tasks.add_employees_task import AddEmployeesTask
from tasks.task import Task


class TaskManager:
    def get_tasks(self) -> list[Task]:
        return [
            self.name_to_task("add_employees"),
            self.name_to_task("dismissed_employees"),
            self.name_to_task("change_positions"),
            self.name_to_task("add_absences"),
        ]

    def name_to_task(self, name: str) -> Task:
        task = Task(name, self._task_name_to_fun(name))
        if name == "add_employees" and not task.df.empty:
            ignore_ids = self.config.data.get("ignore", {}).keys()
            filtered_df = task.df[~task.df["id"].isin(ignore_ids)]
            task = task.update_df(filtered_df)
        return task

    def _task_name_to_fun(self, name: str):
        def fun(df):
            return

        if name == "add_employees":
            fun = AddEmployeesTask._add_employees
        if name == "dismissed_employees":
            fun = self._remove_employees
        if name == "change_positions":
            fun = fun
        if name == "add_absences":
            fun = fun

        return fun

