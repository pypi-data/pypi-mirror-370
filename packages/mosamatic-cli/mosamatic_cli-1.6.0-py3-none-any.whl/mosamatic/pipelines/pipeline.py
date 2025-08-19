from mosamatic.tasks.task import Task


class Pipeline(Task):
    def __init__(self, input, output, params=None, overwrite=False):
        super(Pipeline, self).__init__(input, output, params, overwrite)
        self._tasks = []

    def add_task(self, task):
        self._tasks.append(task)

    def run(self):
        for task in self._tasks:
            task.run()