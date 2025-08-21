"""Модели для асинхронных задач Celery."""

from typing import (
    Optional,
)

from celery import (
    states,
)
from django.contrib.contenttypes.models import (
    ContentType,
)
from django.db.models import (
    PROTECT,
    SET_NULL,
    BigIntegerField,
    CharField,
    DateTimeField,
    F,
    ForeignKey,
    Index,
    JSONField,
    UUIDField,
)
from django.db.models.base import (
    Model,
)
from django.db.models.manager import (
    Manager,
)

from m3_db_utils.models import (
    ModelEnumValue,
    TitledModelEnum,
)
from m3_django_compat.models import (
    GenericForeignKey,
)

import edu_async_tasks


class AsyncTaskType(TitledModelEnum):
    """Модель-перечисление типа асинхронной задачи."""

    UNKNOWN = ModelEnumValue(title='Неизвестно')
    SYSTEM = ModelEnumValue(title='Системная')
    REPORT = ModelEnumValue(title='Отчет')
    IMPORT = ModelEnumValue(title='Импорт данных')
    SCHEDULE_FORMING = ModelEnumValue(title='Формирование расписания')
    SCHEDULE_CLEANER = ModelEnumValue(title='Очищение расписания')
    SCHEDULE_PATTERN_COPY = ModelEnumValue(title='Копирование шаблона расписания')
    ST_PRINTING = ModelEnumValue(title='Печать учебных планов')
    ASYNC_REQUEST = ModelEnumValue(title='Отправка асинхронных запросов')
    MASS_EXPULSION = ModelEnumValue(title='Массовый выпуск')
    AIO_CLIENT = ModelEnumValue(title='AIO клиент')

    class Meta:
        extensible = True
        verbose_name = 'Тип асинхронных задач'
        verbose_name_plural = 'Типы асинхронных задач'


class AsyncTaskStatus(TitledModelEnum):
    """Модель-перечисления статуса асинхронной задачи."""

    PENDING = ModelEnumValue(title='В ожидании')
    RECEIVED = ModelEnumValue(title='В очереди')
    STARTED = ModelEnumValue(title='Выполняется')
    SUCCESS = ModelEnumValue(title='Успешно выполнена')
    REVOKED = ModelEnumValue(title='Остановлена')
    FAILURE = ModelEnumValue(title='Ошибка')
    RETRY = ModelEnumValue(title='Перезапуск')
    IGNORED = ModelEnumValue(title='Игнорирована')
    REJECTED = ModelEnumValue(title='Отменена')
    UNKNOWN = ModelEnumValue(title='Неизвестно')

    _status_to_task_state = {
        PENDING: states.PENDING,
        RECEIVED: states.RECEIVED,
        STARTED: states.STARTED,
        SUCCESS: states.SUCCESS,
        REVOKED: states.REVOKED,
        FAILURE: states.FAILURE,
        RETRY: states.RETRY,
        IGNORED: states.IGNORED,
        REJECTED: states.REJECTED,
    }

    _task_state_to_status = {state: status for status, state in _status_to_task_state.items()}

    @classmethod
    def from_state(cls, task_state: str) -> ModelEnumValue:
        """Возвращает статус задачи RunningTask по состоянию задачи Celery."""
        return cls._task_state_to_status.get(task_state, cls.UNKNOWN)

    @classmethod
    def to_state(cls, status: ModelEnumValue) -> Optional[str]:
        """Возвращает состояние задачи Celery по статусу задачи RunningTask."""
        return cls._status_to_task_state.get(status)

    @classmethod
    def is_finished(cls, status: ModelEnumValue) -> bool:
        """Является ли статус RunningTask завершенной задачи."""
        return status.key in {
            cls.SUCCESS.key,
            cls.FAILURE.key,
            cls.REVOKED.key,
        }

    @classmethod
    def is_cancellable(cls, status: ModelEnumValue) -> bool:
        """Возможно ли отменить выполнение задачи RunningTask для указанного статуса."""
        return status.key in {
            cls.PENDING.key,
            cls.RECEIVED.key,
            cls.STARTED.key,
            cls.RETRY.key,
        }


class AnnotatedRunningTaskManager(Manager):
    """Менеджер кверисета задач RunningTask с добавлением аннотирования.

    В аннотации добавляются текстовое значение типа задачи.
    """

    def get_queryset(self):
        """Возвращает кварисет с аннотированием."""
        return (
            super()
            .get_queryset()
            .annotate(
                task_type_str=F('task_type__title'),
                status_str=F('status__title'),
            )
        )


class RunningTask(Model):
    """Модель асинхронной задачи для отображения в соответствующем реестре."""

    objects = AnnotatedRunningTaskManager()

    id = UUIDField(
        'ID задачи',
        primary_key=True,
    )

    name = CharField(
        'Наименование задачи',
        max_length=512,
        blank=True,
    )

    task_type = ForeignKey(
        AsyncTaskType,
        verbose_name='Тип задачи',
        default=AsyncTaskType.UNKNOWN.key,
        on_delete=PROTECT,
    )

    profile_type = ForeignKey(
        ContentType,
        null=True,
        blank=True,
        on_delete=SET_NULL,
    )
    profile_id = CharField(
        max_length=36,
        null=True,
        blank=True,
    )
    user_profile = GenericForeignKey('profile_type', 'profile_id')

    description = CharField(
        'Описание задачи',
        max_length=512,
        blank=True,
    )

    options = JSONField(
        'Дополнительные опции задачи',
        null=True,
        blank=True,
    )

    status = ForeignKey(
        AsyncTaskStatus,
        verbose_name='Состояние задачи',
        default=AsyncTaskStatus.PENDING.key,
        on_delete=PROTECT,
    )

    queued_at = DateTimeField(
        'Дата и время помещения в очередь',
        db_index=True,
        null=True,
        blank=True,
    )

    started_at = DateTimeField(
        'Дата и время запуска задачи',
        null=True,
        blank=True,
    )

    finished_at = DateTimeField(
        'Дата и время завершения задачи',
        null=True,
        blank=True,
    )

    organization_id = CharField(
        'Идентификатор организации',
        max_length=40,
        null=True,
        blank=True,
    )

    def get_queued_at_display(self) -> str:
        """Отображение времени старта задачи."""
        return self.queued_at.strftime(edu_async_tasks.get_config().task_start_time_format) if self.queued_at else '-'

    def get_user_profile_display(self) -> str:
        """Отображение пользователя запустившего задачу."""
        if not self.user_profile:
            return edu_async_tasks.get_config().task_default_user_name

        return getattr(self.user_profile, 'fullname', str(self.user_profile))

    class Meta:
        indexes = (Index(fields=['profile_type', 'profile_id']),)
        verbose_name = 'Асинхронная задача'
        verbose_name_plural = 'Асинхронные задачи'
