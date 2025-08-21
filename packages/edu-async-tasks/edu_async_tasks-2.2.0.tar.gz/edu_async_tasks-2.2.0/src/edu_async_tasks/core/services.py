from typing import (
    Iterable,
)

from celery.result import (
    AsyncResult,
)

from m3_db_utils.models import (
    ModelEnumValue,
)

from edu_async_tasks.core.adapters.db import (
    running_tasks_repository,
)
from edu_async_tasks.core.domain.model import (
    TasksNotCancellable,
)

from . import (
    domain,
)
from .models import (
    AsyncTaskStatus,
    RunningTask,
)


def get_running_task_result(running_task: 'RunningTask') -> domain.TaskResult:
    """Возвращает информацию о состоянии и результатах асинхронной задачи."""

    task_id = str(running_task.id)
    async_result = AsyncResult(task_id)
    result = domain.TaskResult(
        values={},
        files=[],
        state=async_result.state,
    )

    if async_result.result:
        if isinstance(async_result.result, Exception):
            if async_result.traceback:
                result.error = async_result.traceback
            else:
                result.error = async_result.result.__repr__()

        elif isinstance(async_result.result, dict):
            result.progress = async_result.result.get('progress', 'Неизвестно')
            result.values = async_result.result.get('values', {})
            result.files = async_result.result.get('files', [])

    else:
        # Результат задачи отсутствует. Проверим, не истёк ли строк хранения результата
        task_key = async_result.backend.get_key_for_task(task_id)
        task_result_is_none = async_result.backend.get(task_key) is None

        if task_result_is_none and AsyncTaskStatus.is_finished(running_task.status):
            result.progress = 'Истек срок хранения результатов задачи'
            result.state = ''

    return result


def ensure_tasks_cancellable(*running_tasks: Iterable[RunningTask]):
    all_tasks_are_cancellable = all(
        AsyncTaskStatus.is_cancellable(running_task.status) for running_task in running_tasks
    )

    if not all_tasks_are_cancellable:
        raise TasksNotCancellable()


def revoke_async_tasks(*ids: str):
    """Прерывает выполнение асинхронных задач."""
    running_tasks = running_tasks_repository.get_by_ids(*ids)
    ensure_tasks_cancellable(*running_tasks)

    for task in running_tasks:
        result = AsyncResult(str(task.id))
        status = AsyncTaskStatus.from_state(result.state)

        if AsyncTaskStatus.is_cancellable(status):
            if status == AsyncTaskStatus.STARTED:
                terminate = True
            else:
                terminate = False

            result.revoke(terminate=terminate)
            update_running_task(task.id, status=AsyncTaskStatus.REVOKED)


def update_running_task(task_id: str, **params):
    """Обновляет запись задачи RunningTask."""
    if 'status' in params and isinstance(params['status'], ModelEnumValue):
        params['status_id'] = params.pop('status').key

    RunningTask.objects.filter(id=task_id).update(**params)
