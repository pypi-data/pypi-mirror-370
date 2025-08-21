from django.db import (
    migrations,
)


def init_task_types(apps, schema_editor):
    """Заполнение первоначальными данными AsyncTaskType."""
    AsyncTaskType = apps.get_model('edu_async_tasks_core', 'AsyncTaskType')  # noqa: N806

    AsyncTaskType.objects.bulk_create(
        [
            AsyncTaskType(
                key='UNKNOWN',
                title='Неизвестно',
            ),
            AsyncTaskType(
                key='SYSTEM',
                title='Системная',
            ),
            AsyncTaskType(
                key='REPORT',
                title='Отчет',
            ),
            AsyncTaskType(
                key='IMPORT',
                title='Импорт данных',
            ),
            AsyncTaskType(
                key='SCHEDULE_FORMING',
                title='Формирование расписания',
            ),
            AsyncTaskType(
                key='SCHEDULE_CLEANER',
                title='Очищение расписания',
            ),
            AsyncTaskType(
                key='SCHEDULE_PATTERN_COPY',
                title='Копирование шаблона расписания',
            ),
            AsyncTaskType(
                key='ST_PRINTING',
                title='Печать учебных планов',
            ),
            AsyncTaskType(
                key='ASYNC_REQUEST',
                title='Отправка асинхронных запросов',
            ),
            AsyncTaskType(
                key='MASS_EXPULSION',
                title='Массовый выпуск',
            ),
            AsyncTaskType(
                key='AIO_CLIENT',
                title='AIO клиент',
            ),
        ],
        ignore_conflicts=True,
    )


def init_task_statuses(apps, schema_editor):
    """Заполнение первоначальными данными AsyncTaskStatus."""
    AsyncTaskStatus = apps.get_model('edu_async_tasks_core', 'AsyncTaskStatus')  # noqa: N806

    AsyncTaskStatus.objects.bulk_create(
        [
            AsyncTaskStatus(
                key='PENDING',
                title='В ожидании',
            ),
            AsyncTaskStatus(
                key='RECEIVED',
                title='В очереди',
            ),
            AsyncTaskStatus(
                key='STARTED',
                title='Выполняется',
            ),
            AsyncTaskStatus(
                key='SUCCESS',
                title='Успешно выполнена',
            ),
            AsyncTaskStatus(
                key='REVOKED',
                title='Остановлена',
            ),
            AsyncTaskStatus(
                key='FAILURE',
                title='Ошибка',
            ),
            AsyncTaskStatus(
                key='RETRY',
                title='Перезапуск',
            ),
            AsyncTaskStatus(
                key='IGNORED',
                title='Игнорирована',
            ),
            AsyncTaskStatus(
                key='REJECTED',
                title='Отменена',
            ),
            AsyncTaskStatus(
                key='UNKNOWN',
                title='Неизвестно',
            ),
        ],
        ignore_conflicts=True,
    )


class Migration(migrations.Migration):
    dependencies = [
        ('edu_async_tasks_core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(init_task_types, reverse_code=migrations.RunPython.noop),
        migrations.RunPython(init_task_statuses, reverse_code=migrations.RunPython.noop),
    ]
