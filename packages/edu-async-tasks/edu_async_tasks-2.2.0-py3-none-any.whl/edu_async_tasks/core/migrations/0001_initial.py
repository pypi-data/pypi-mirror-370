import django.db.models.deletion
from django.db import (
    migrations,
    models,
)


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='AsyncTaskStatus',
            fields=[
                ('title', models.TextField(verbose_name='расшифровка значения')),
                (
                    'key',
                    models.CharField(
                        db_index=True, max_length=512, primary_key=True, serialize=False, verbose_name='ключ'
                    ),
                ),
                ('order_number', models.PositiveIntegerField(default=100000, verbose_name='Порядковый номер')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AsyncTaskType',
            fields=[
                ('title', models.TextField(verbose_name='расшифровка значения')),
                (
                    'key',
                    models.CharField(
                        db_index=True, max_length=512, primary_key=True, serialize=False, verbose_name='ключ'
                    ),
                ),
                ('order_number', models.PositiveIntegerField(default=100000, verbose_name='Порядковый номер')),
            ],
            options={
                'verbose_name': 'Тип асинхронных задач',
                'verbose_name_plural': 'Типы асинхронных задач',
            },
        ),
        migrations.CreateModel(
            name='RunningTask',
            fields=[
                ('id', models.UUIDField(primary_key=True, serialize=False, verbose_name='ID задачи')),
                ('name', models.CharField(blank=True, max_length=512, verbose_name='Наименование задачи')),
                ('profile_id', models.PositiveIntegerField(blank=True, null=True)),
                ('description', models.CharField(blank=True, max_length=512, verbose_name='Описание задачи')),
                ('options', models.JSONField(blank=True, null=True, verbose_name='Дополнительные опции задачи')),
                (
                    'queued_at',
                    models.DateTimeField(
                        blank=True, db_index=True, null=True, verbose_name='Дата и время помещения в очередь'
                    ),
                ),
                ('started_at', models.DateTimeField(blank=True, null=True, verbose_name='Дата и время запуска задачи')),
                (
                    'finished_at',
                    models.DateTimeField(blank=True, null=True, verbose_name='Дата и время завершения задачи'),
                ),
                (
                    'profile_type',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to='contenttypes.contenttype',
                    ),
                ),
                (
                    'status',
                    models.ForeignKey(
                        default='PENDING',
                        on_delete=django.db.models.deletion.PROTECT,
                        to='edu_async_tasks_core.asynctaskstatus',
                        verbose_name='Состояние задачи',
                    ),
                ),
                (
                    'task_type',
                    models.ForeignKey(
                        default='UNKNOWN',
                        on_delete=django.db.models.deletion.PROTECT,
                        to='edu_async_tasks_core.asynctasktype',
                        verbose_name='Тип задачи',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Асинхронная задача',
                'verbose_name_plural': 'Асинхронные задачи',
                'indexes': [models.Index(fields=['profile_type', 'profile_id'], name='edu_async_t_profile_70c100_idx')],
            },
        ),
    ]
