from dataclasses import (
    asdict,
)
from datetime import (
    datetime,
    timedelta,
)
from itertools import (
    chain,
)
from operator import (
    attrgetter,
)
from unittest import (
    mock,
)
from uuid import (
    uuid4,
)

import freezegun
import pytz
from django.urls.base import (
    reverse,
)
from django.utils import (
    timezone,
)
from django.utils.duration import (
    duration_string,
)
from rest_framework import (
    status,
)
from rest_framework.test import (
    APITestCase,
)

from edu_async_tasks.core import (
    domain,
)
from edu_async_tasks.core.models import (
    AsyncTaskStatus,
    AsyncTaskType,
    RunningTask,
)


# 3 марта, 18:00 по UTC
_frozen_time = datetime(2025, 3, 3, 18, tzinfo=pytz.utc)


@freezegun.freeze_time(_frozen_time)
class RunningTaskViewSetTestCase(APITestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.list_url = reverse('async-tasks-list')

        self.task_types = AsyncTaskType.get_model_enum_values()
        self.task_statuses = sorted(AsyncTaskStatus.get_model_enum_values(), key=attrgetter('title'))

        base_time_utc = self.base_time_utc = timezone.now()

        # Первые три задачи первого дня по UTC (3 марта), по Москве они тоже 3 марта
        self.task_1 = RunningTask(
            id=uuid4(),
            name=f'edu_async_tasks.core.tasks.Foo00',
            task_type_id=self.task_types[0].key,
            queued_at=base_time_utc - timedelta(hours=2),  # попадает в 3 марта по UTC
            started_at=base_time_utc - timedelta(hours=1),
            finished_at=base_time_utc,
            status_id=AsyncTaskStatus.PENDING.key,
            description='АААААААААааааааааааААААААААААааааа',
        )

        self.task_2 = RunningTask(
            id=uuid4(),
            name=f'edu_async_tasks.core.tasks.Foo01',
            queued_at=base_time_utc - timedelta(hours=3),  # тоже 3 марта по UTC
            started_at=base_time_utc - timedelta(hours=2),
            finished_at=base_time_utc - timedelta(hours=1, minutes=1),
            task_type_id=self.task_types[1].key,
            status_id=AsyncTaskStatus.RECEIVED.key,
            description='В',
        )

        self.task_3 = RunningTask(
            id=uuid4(),
            name=f'edu_async_tasks.core.tasks.Foo02',
            task_type_id=self.task_types[2].key,
            queued_at=base_time_utc - timedelta(minutes=30),  # ближе к концу 3 марта UTC
            started_at=base_time_utc - timedelta(minutes=20),
            finished_at=base_time_utc - timedelta(minutes=10),
            status_id=AsyncTaskStatus.STARTED.key,
            description='Б',
        )

        self.tasks = [
            self.task_1,
            self.task_2,
            self.task_3,
        ]

        # задачи второго дня с точки зрения клиента (по Москве уже 4 марта, по UTC еще 3 марта)
        self.other_day_tasks = []
        for idx, task_status in enumerate(self.task_statuses[3:], start=3):
            queued_at_utc = base_time_utc + timedelta(hours=idx)
            started_at_utc = queued_at_utc + timedelta(minutes=3 + idx)
            finished_at_utc = started_at_utc + timedelta(minutes=5 + idx)

            task = RunningTask(
                id=uuid4(),
                name=f'edu_async_tasks.core.tasks.Foo{idx:02d}',
                task_type_id=self.task_types[idx].key,
                description=f'Задача номер {idx:02d}',
                status_id=task_status.key,
                queued_at=queued_at_utc,
                started_at=started_at_utc,
                finished_at=finished_at_utc,
                options=None,
            )
            setattr(self, f'task_{idx + 1}', task)
            self.other_day_tasks.append(task)

        self.tasks = RunningTask.objects.bulk_create(chain(self.tasks, self.other_day_tasks))

    def _get_expected_task_data(self, task: RunningTask) -> dict:
        return {
            'id': str(task.id),
            'name': task.name,
            'status': {'key': 'PENDING', 'title': 'В ожидании'},
            'description': task.description,
            'execution_time': duration_string(task.finished_at - task.started_at),
            'queued_at': task.queued_at.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'started_at': task.started_at.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'finished_at': task.finished_at.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'organization_id': task.organization_id,
        }

    def test_list(self) -> None:
        response = self.client.get(self.list_url)
        task = self.tasks[0]

        expected_result = self.client.get(reverse('async-tasks-detail', args=[task.id])).json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for field in ('count', 'next', 'previous', 'results'):
            with self.subTest(field=field):
                self.assertIn(field, response.data)

        results = response.json()['results']

        self.assertEqual(len(results), len(self.tasks))

        # проверяем сортировку по-умолчанию
        self.assertEqual(
            tuple(str(i.id) for i in (*reversed(self.other_day_tasks), self.task_3, self.task_1, self.task_2)),
            tuple(t['id'] for t in results),
        )

        # Проверяем, что expected_result содержится в результатах
        self.assertIn(expected_result, results)

    @mock.patch('edu_async_tasks.rest.running_tasks.serializers.get_running_task_result')
    def test_retrieve(self, mock_get_result):
        file = domain.TaskResultFile(url='/reports/report_foo.xls', description='Отчёт FOO')
        expected_task_result = domain.TaskResult(values={'Ключ': 'значение'}, files=[file], error='не ошибка')
        mock_get_result.return_value = expected_task_result

        url = reverse('async-tasks-detail', args=[self.task_1.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_data = self._get_expected_task_data(self.task_1) | {
            'task_result': {
                'error_text': expected_task_result.error,
                'values': expected_task_result.values,
                'files': [asdict(file)],
            },
        }

        self.assertEqual(response.json(), expected_data)

    def test_list_ordering(self):
        sub_tests = (
            ('queued_at', (self.task_2, self.task_1, self.task_3, *self.other_day_tasks)),
            ('status', (self.task_1, self.task_2, self.task_3, *self.other_day_tasks)),
            ('description', (self.task_1, self.task_3, self.task_2, *self.other_day_tasks)),
            ('status', (self.task_1, self.task_2, self.task_3, *self.other_day_tasks)),
            (
                'execution_time',
                (
                    self.task_4,
                    self.task_5,
                    self.task_3,
                    self.task_6,
                    self.task_7,
                    self.task_8,
                    self.task_9,
                    self.task_10,
                    self.task_2,
                    self.task_1,
                ),
            ),
        )
        for ordering_field, expected_asc_order in sub_tests:
            with self.subTest(ordering_field):
                response_asc = self.client.get(self.list_url, {'ordering': ordering_field})
                response_desc = self.client.get(self.list_url, {'ordering': f'-{ordering_field}'})

                self.assertEqual(response_asc.status_code, status.HTTP_200_OK)
                self.assertEqual(response_desc.status_code, status.HTTP_200_OK)

                results_asc = response_asc.json()['results']
                results_desc = response_desc.json()['results']

                # проверяем правильность сортировки
                self.assertEqual(
                    tuple(str(i.id) for i in expected_asc_order),
                    tuple(t['id'] for t in results_asc),
                )
                # проверяем что набор записей не отличается, отличается только порядок
                self.assertListEqual(results_asc, list(reversed(results_desc)))

    def test_list_filtering(self):
        client_tz = pytz.timezone('Europe/Moscow')

        # первый день по Москве
        today_local = self.base_time_utc.astimezone(client_tz).date()

        # границы для первого дня по Москве
        today_start_local = client_tz.localize(datetime.combine(today_local, datetime.min.time()))
        today_end_local = client_tz.localize(datetime.combine(today_local, datetime.max.time()))

        # границы для второго дня по Москве
        tomorrow_local = today_local + timedelta(days=1)
        tomorrow_start_local = client_tz.localize(datetime.combine(tomorrow_local, datetime.min.time()))
        tomorrow_end_local = client_tz.localize(datetime.combine(tomorrow_local, datetime.max.time()))

        subtests = (
            (
                'queued_at: интервал (все задачи за первый день по Москве)',
                {'queued_at_after': today_start_local, 'queued_at_before': today_end_local},
                (self.task_3, self.task_1, self.task_2),
            ),
            (
                'queued_at: интервал (все задачи за второй день по Москве)',
                {'queued_at_after': tomorrow_start_local, 'queued_at_before': tomorrow_end_local},
                tuple(reversed(self.other_day_tasks)),
            ),
            (
                'queued_at: интервал (все задачи за первый и второй день по Москве)',
                {'queued_at_after': today_start_local, 'queued_at_before': tomorrow_end_local},
                tuple(chain(reversed(self.other_day_tasks), (self.task_3, self.task_1, self.task_2))),
            ),
            (
                'queued_at_after: интервал с границей слева (все задачи, начиная со второго дня по Москве)',
                {'queued_at_after': tomorrow_start_local},
                reversed(self.other_day_tasks),
            ),
            (
                'queued_at_before: интервал с границей справа (все задачи до конца первого дня по Москве)',
                {'queued_at_before': today_end_local},
                (self.task_3, self.task_1, self.task_2),
            ),
            ('status', {'status': self.task_1.status.key}, (self.task_1,)),
            ('description', {'description': 'ааааааа'}, (self.task_1,)),
            ('status', {'status': AsyncTaskStatus.PENDING.key}, (self.task_1,)),
        )

        for name, filter_params, expected_tasks in subtests:
            with self.subTest(name=name):
                response = self.client.get(self.list_url, filter_params)
                self.assertEqual(response.status_code, status.HTTP_200_OK)

                results = response.json()['results']

                # проверяем правильность фильтрации
                self.assertEqual(
                    tuple(str(i.id) for i in expected_tasks),
                    tuple(t['id'] for t in results),
                )
