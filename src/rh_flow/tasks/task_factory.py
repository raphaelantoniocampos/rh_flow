from task import Task
from download_task import DownloadTask

class TaskFactory:
    @staticmethod
    def create_task(task_type: str, *args, **kwargs):
        """
        Factory method to create a task instance based on the type.

        :param task_type: Type of task to create (e.g., "new", "dismissed", "download").
        :param args: Arguments to pass to the task constructor.
        :param kwargs: Keyword arguments to pass to the task constructor.
        :return: An instance of the specified task.
        """
        if task_type.lower() == "new":
            return Task(name="new", *args, **kwargs)
        elif task_type.lower() == "dismissed":
            return Task(name="dismissed", *args, **kwargs)
        elif task_type.lower() == "position":
            return Task(name="position", *args, **kwargs)
        elif task_type.lower() == "absences":
            return Task(name="absences", *args, **kwargs)
        elif task_type.lower() == "download":
            return DownloadTask(*args, **kwargs)
        else:
            raise ValueError(f"Unsupported task type: {task_type}")
