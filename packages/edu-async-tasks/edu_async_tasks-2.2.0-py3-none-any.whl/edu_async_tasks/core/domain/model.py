from dataclasses import (
    dataclass,
    field,
)
from logging import (
    getLogger,
)
from typing import (
    Optional,
    Union,
)
from uuid import (
    UUID,
)

from celery.exceptions import (
    Ignore,
)
from celery.result import (
    AsyncResult,
)
from django.core.cache import (
    cache,
)
from django.utils.functional import (
    cached_property,
)

import edu_async_tasks


@dataclass
class TaskResultFile:
    """Файл в результатах асинхронной задачи."""

    description: Optional[str]
    url: str


@dataclass
class TaskResult:
    """Результат асинхронной задачи."""

    values: dict
    files: list[TaskResultFile] = field(default_factory=list)
    progress: str = ''
    error: str = ''
    state: str = ''


def uuid_or_none(value) -> Union[UUID, None]:
    """Преобразует строку в UUID или возвращает None."""
    if value is None or isinstance(value, UUID):
        return value

    try:
        return UUID(value)

    except (AttributeError, ValueError):
        return None


def normalize_organization_id(value: Optional[Union[int, str, UUID]]) -> Optional[str]:
    """Преобразует UUID или числовое значение к строковому типу."""
    if value is None:
        return None
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, int):
        return str(value)

    s = str(value).strip()

    return s


class EduAsyncTasksException(Exception):
    """Базовое исключение."""


class TasksNotCancellable(EduAsyncTasksException):
    def __init__(self, msg='Необходимо выбрать только выполняющиеся задачи', *args, **kwargs):
        super().__init__(msg, *args, **kwargs)


class TaskUniqueException(EduAsyncTasksException):
    def __init__(self, msg='Задача в очереди или выполняется', *args, **kwargs):
        super().__init__(msg, *args, **kwargs)


class TaskLocker:
    """Класс, отвечающий за блокировку задач."""

    # формат ключа в кэше
    LOCK_ID_FORMAT = 'async_task:lock:{task_name}_{params}'

    DEFAULT_LOCK_MSG = 'Задача уже выполняется или находится в очереди'
    DEFAULT_LOCK_VALUE = 'value'

    def __init__(
        self,
        task_name: str = '',
        params: Optional[dict] = None,
        task_id: Optional[str] = None,
        expire_on: Optional[int] = None,
    ):
        self.task_name = task_name
        self.task_id = task_id
        self.params = params if params is not None else {}
        self.expire_on = expire_on if expire_on is not None else edu_async_tasks.get_config().default_lock_expire

    @cached_property
    def lock_id(self) -> str:
        """Ключ в кэше."""
        return self.LOCK_ID_FORMAT.format(
            task_name=self.task_name, params='&'.join(f'{k}={v}' for k, v in self.params.items())
        )

    def acquire_lock(self) -> str:
        """Установка блокировки."""
        value = self.task_id or self.DEFAULT_LOCK_VALUE
        cache.set(self.lock_id, value, self.expire_on)
        getLogger(__name__).debug(f'Lock acquired for Task {self.task_name} ({self.params}) with value: {value}')

        return self.lock_id

    def delete_lock(self) -> None:
        """Удаление блокировки."""
        self.delete_lock_by_id(self.lock_id)

    @staticmethod
    def delete_lock_by_id(lock_id: str) -> bool:
        """Удаление блокировки по ключу.

        :param lock_id: ключ
        """
        return cache.delete(lock_id)

    def is_locked(self) -> bool:
        """Установлена ли блокировка."""
        is_locked = False

        value = cache.get(self.lock_id)

        if value:
            is_locked = True

            # Возможна ситуация, когда задача по которой была выставлена блокировка
            # завершила свою работу, при этом блокировка не была снята. Поэтому проверяем
            # статус задачи по которой выставлялась блокировка:
            if value != self.DEFAULT_LOCK_VALUE and uuid_or_none(value):
                # значит в value должен быть task_id предыдущей задачи и по нему пытаемся определить её статус
                async_result = AsyncResult(value)
                if async_result and async_result.ready():
                    # задача есть, но она уже завершилась - снимаем блокировку
                    self.delete_lock()
                    is_locked = False

        return is_locked

    def raise_if_locked(self, message: Optional[str] = None):
        """Если блокировано, то вызывает исключение.

        :raises: edu_async_tasks.exceptions.TaskUniqueException
        """
        if self.is_locked():
            getLogger(__name__).debug(f'Add failed. Task {self.task_name} currently locked ({self.params})')

            raise TaskUniqueException(message or self.DEFAULT_LOCK_MSG)


class PeriodicTaskLocker(TaskLocker):
    """Класс отвечающий за блокировку задач.

    Переопределён для возможности игнорирования повторного запуска для уже
    запущенных периодических задач.
    """

    def raise_if_locked(self, message: Optional[str] = None):
        """Если блокировано, то вызывает исключение."""
        if self.is_locked():
            getLogger(__name__).debug(f'Add failed. Task {self.task_name} currently locked ({self.params})')

            raise Ignore()
