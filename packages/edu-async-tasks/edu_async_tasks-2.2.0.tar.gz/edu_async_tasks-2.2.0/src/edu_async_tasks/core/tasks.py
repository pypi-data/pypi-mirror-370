"""Базовые классы для асинхронных задач."""

import time
from dataclasses import (
    asdict,
)
from datetime import (
    datetime,
)
from logging import (
    getLogger,
)
from typing import (
    Optional,
    Union,
)

from celery import (
    Task,
    states,
)
from celery.schedules import (
    maybe_schedule,
)
from django.conf import (
    settings,
)
from django.contrib.contenttypes.models import (
    ContentType,
)
from django.utils import (
    timezone,
)
from django.utils.functional import (
    classproperty,
)
from kombu import (
    uuid,
)

from .domain import (
    PeriodicTaskLocker,
    TaskLocker,
    TaskResultFile,
    normalize_organization_id,
)
from .models import (
    AsyncTaskStatus,
    AsyncTaskType,
    RunningTask,
)
from .services import (
    update_running_task,
)


class AsyncTask(Task):
    """Базовый класс асинхронных задач."""

    abstract = True

    task_type = AsyncTaskType.UNKNOWN

    # описание (имя) асинхронной задачи (отображается в реестре)
    # может быть передано опцией при постановке в очередь
    description = ''

    debug = getLogger(__name__).debug

    # класс отвечающий за невозможность одновременного запуска
    # задач по определенным критериям
    locker_class = TaskLocker

    # параметры, определяющие блокировку задачи,
    # можно дополнить в apply_async (при постановке в очередь)
    locker_config = {
        # словарь параметров, например {'school_id': 1745}
        'lock_params': None,
        # текст сообщения об ошибке
        'lock_message': None,
        # время в сек., когда снимется блокировка независимо от завершения задачи
        'lock_expire': None,
    }

    # ContentType для модели профиля пользователя. Может передаваться
    # в параметре profile_type при вызове apply_async
    profile_type = None

    # Логировать в базу данных создавая записи RunningTask
    logging_in_db = True

    @classproperty
    def name(cls):  # noqa: N805
        """Полное имя задачи в Celery."""
        return '{}.{}'.format(cls.__module__, cls.__name__)

    @staticmethod
    def get_running_task(task_id: str) -> Optional[RunningTask]:
        """Возвращает запись RunningTask по её id."""
        try:
            return RunningTask.objects.get(id=task_id)
        except RunningTask.DoesNotExist:
            return

    @classmethod
    def acquire_lock(cls, locker_config: dict, task_id: Optional[str] = None) -> Optional[str]:
        """Установка блокировки, если заданы параметры блокировки.

        :raises: async_tasks.exceptions.TaskUniqueException
        """
        lock_params = locker_config.get('lock_params')
        if lock_params:
            # была заданы параметры блокировки
            locker = cls.locker_class(
                task_name=cls.__name__,
                params=lock_params,
                task_id=task_id,
                expire_on=locker_config.get('lock_expire'),
            )
            locker.raise_if_locked(locker_config.get('lock_message'))

            lock_id = locker.acquire_lock()

            cls.debug(f'Locked task {cls.__name__} lock_id = {lock_id}')

            return lock_id

    def release_lock(self, lock_id: Optional[str]):
        """Снятие блокировки."""
        released = self.locker_class.delete_lock_by_id(lock_id)
        if released:
            self.debug(f'Unlock task {self.__name__} lock_id = {lock_id}: success')
        else:
            self.debug(f'Unlock task {self.__name__} lock_id = {lock_id}: lock not found')

    def set_read_from_replica(self, read: bool = True):
        """Установка чтения из реплики БД."""

    def apply_async(
        self, args=None, kwargs=None, task_id=None, producer=None, link=None, link_error=None, shadow=None, **options
    ):
        """Постановка задачи в очередь.

        Автор задачи задаётся снаружи через 2 поля в словаре kwargs:
            object_id и content_type
        """
        if kwargs is None:
            kwargs = {}

        task_id = task_id or uuid()

        # копируем, чтобы не влиять на другие инстансы данного класса задач
        locker_config = self.locker_config.copy()
        # параметры, определяющие блокировку, можно определить для конкретного исполнения
        lock_data = options.pop('lock_data', None)
        if lock_data:
            locker_config.update(lock_data)

        kwargs['lock_id'] = self.acquire_lock(locker_config, task_id=task_id)

        if self.logging_in_db:
            profile_type = kwargs.get('profile_type', self.profile_type)

            if profile_type is not None and not isinstance(profile_type, ContentType):
                profile_type = ContentType.objects.get_for_id(profile_type)

            profile_id = kwargs.get('profile_id')
            organization_id = normalize_organization_id(kwargs.get('organization_id'))

            RunningTask.objects.get_or_create(
                id=task_id,
                defaults=dict(
                    name=self.name,
                    task_type_id=self.task_type.key if self.task_type else AsyncTaskType.UNKNOWN.key,
                    description=kwargs.get('description', self.description),
                    status_id=AsyncTaskStatus.PENDING.key,
                    profile_id=profile_id,
                    profile_type=profile_type,
                    queued_at=timezone.now() if settings.USE_TZ else datetime.now(),
                    options=options if options else None,
                    organization_id=organization_id,
                ),
            )

        is_replica = options.get('is_replica', False)
        if is_replica:
            kwargs['is_replica'] = True

        async_result = super().apply_async(
            args=args,
            kwargs=kwargs,
            task_id=task_id,
            producer=producer,
            link=link,
            link_error=link_error,
            shadow=shadow,
            **options,
        )

        self.debug(f'Task {self.__name__} (id = {task_id}) added')

        return async_result

    def process(self, *args, **kwargs) -> Optional[dict]:
        """Основная логика работы задачи."""

    def run(self, *args, **kwargs):
        """Выполнение задачи."""
        # начальное состояние задачи
        self.state = {
            # результаты задачи
            'values': {},
            'files': [],
            # описание результата
            'description': '',
            # прогресс выполнения задачи
            'progress': 'Неизвестно',
            'exc_type': '',
            'exc_message': '',
        }
        self.update_state(state=AsyncTaskStatus.to_state(AsyncTaskStatus.STARTED), meta=self.state)
        self.set_read_from_replica(kwargs.get('is_replica', False))

        self.debug(f'Task {self.__name__} (id = {self.request.id}) started')
        self.set_progress(progress='Выполняется')
        time_start = time.time()

        process_state = self.process(*args, **kwargs)

        self.set_progress(
            progress=process_state.get('progress', 'Завершено') if process_state else 'Завершено',
            values={
                'Время выполнения': f'{((time.time() - time_start) / 60):.1f} мин.',
            },
        )

        return self.state

    def _update_running_task(self, task_id: str, **params):
        """Обновление записи RunningTask."""
        if self.logging_in_db:
            update_running_task(task_id, **params)

    def after_return(self, status: str, retval: Union[dict, Exception], task_id: str, args, kwargs, einfo):
        """Завершение задачи."""
        self.debug(f'Task {self.__name__} (id = {task_id}) finished')

        lock_id = kwargs.get('lock_id')
        if lock_id:
            self.release_lock(lock_id)

        if isinstance(retval, dict):
            state = retval.get('task_state', status)
        else:
            state = status

        self.update_state(state=state, meta=retval)

    def update_state(self, task_id=None, state=None, meta=None, **kwargs):
        """Обновление состояния задачи.

        Arguments:
            task_id (str): Id задачи.
            state (str): Новое состояние.
            meta (Dict): Мета-данные состояния.
        """
        if task_id is None:
            task_id = self.request.id

        if state == states.STARTED:
            self._update_running_task(
                task_id,
                status=AsyncTaskStatus.STARTED,
                started_at=timezone.now() if settings.USE_TZ else datetime.now(),
            )
        else:
            self._update_running_task(
                task_id,
                status=AsyncTaskStatus.from_state(state),
            )

        super().update_state(task_id=task_id, state=state, meta=meta, **kwargs)

    def set_progress(
        self,
        progress: Optional[str] = None,
        values: Optional[dict] = None,
        files: Optional[list[TaskResultFile]] = None,
        task_id: Optional[str] = None,
        task_state: str = states.STARTED,
    ):
        """Обновление состояния выполнения задачи.

        :param str task_id: id задачи celery
        :param str task_state: состояние задачи celery (celery.states)
        :param str progress: строковое описание состояния выполнения задачи
        :param dict values: значения задаваемые процедурой выполнения задачи
        :param list[TaskResultFile] files: файлы, которыми нужно дополнить результат выполнения задачи
        """
        if task_id is None:
            task_id = self.request.id

        if progress:
            self.state['progress'] = progress
        if values:
            self.state['values'].update(values)
        if files:
            self.state['files'].extend(map(asdict, files))

        self.backend.store_result(task_id, self.state, task_state)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Обработка ошибки.

        Запускается, если во время выполнения задачи возникла ошибка.
        """
        self.state['exc_type'] = type(exc).__name__
        self.state['exc_message'] = exc.__str__()

        self._update_running_task(
            task_id,
            status=AsyncTaskStatus.FAILURE,
            finished_at=timezone.now() if settings.USE_TZ else datetime.now(),
        )

    def on_success(self, retval, task_id, args, kwargs):
        """Обработка успешного завершения задачи."""
        self._update_running_task(
            task_id,
            status=AsyncTaskStatus.SUCCESS,
            finished_at=timezone.now() if settings.USE_TZ else datetime.now(),
        )


class PeriodicAsyncTask(AsyncTask):
    """Периодическая задача."""

    abstract = True
    ignore_result = True
    relative = False
    options = None
    compat = True

    def __init__(self):
        if not hasattr(self, 'run_every'):
            raise NotImplementedError('Periodic tasks must have a run_every attribute')

        self.run_every = maybe_schedule(self.run_every, self.relative)

        super().__init__()

    @classmethod
    def on_bound(cls, app):
        """Вызывается, когда задача связывается с приложением celery."""
        app.conf.beat_schedule[cls.name] = {
            'task': cls.name,
            'schedule': cls.run_every,
            'args': (),
            'kwargs': {},
            'options': cls.options or {},
            'relative': cls.relative,
        }


class UniquePeriodicAsyncTask(PeriodicAsyncTask):
    """Уникальные периодические задачи."""

    abstract = True
    lock_expire_seconds = 60 * 60

    locker_class = PeriodicTaskLocker

    @property
    def locker_config(self) -> dict:
        """Настройки для механизма блокировок."""
        return {
            'lock_params': {'task_name': self.name},
            'lock_message': f'Task [{self.__name__}] is running',
            'lock_expire': self.lock_expire_seconds,
        }
