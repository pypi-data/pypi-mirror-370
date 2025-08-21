from time import (
    sleep,
)

from testapp.entrypoints.celery import (
    app,
)

from edu_async_tasks.core.domain.model import (
    TaskResultFile,
)
from edu_async_tasks.core.tasks import (
    AsyncTask,
)


class NullTask(AsyncTask):
    def process(self, *args, **kwargs):
        return super().process(*args, **kwargs)


null_task = NullTask()


app.register_task(null_task)


class SleepTask(AsyncTask):
    def process(self, *args, n=5, **kwargs):
        print(f'Sleeping {n} seconds..')
        sleep(n)
        print('..done')
        return super().process(*args, **kwargs)


sleep_task = SleepTask()


app.register_task(sleep_task)


class LockableTask(NullTask):
    locker_config = {
        'lock_params': {'school_id': 1745},
    }


lockable_task = LockableTask()


app.register_task(lockable_task)


class ResultStorageTask(AsyncTask):
    def process(self, *args, steps=3, **kwargs):
        for step in range(1, steps + 1):
            # Обновляем прогресс
            self.set_progress(
                progress=f'Выполнен шаг {step} из {steps}',
                values={'completed_steps': step, 'total_steps': steps},
                files=[TaskResultFile(description=f'Отчёт: часть №{step}', url=f'report_part_{step}.xls')],
            )


file_generating_task = ResultStorageTask()


app.register_task(file_generating_task)
