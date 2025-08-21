from django_filters import (
    rest_framework as filters,
)

from edu_async_tasks.core.models import (
    RunningTask,
)


class RunningTasksFilter(filters.FilterSet):
    queued_at = filters.IsoDateTimeFromToRangeFilter(label='Дата и время постановки в очередь')
    description = filters.CharFilter(lookup_expr='icontains', label='Описание')
    status = filters.CharFilter(label='Ключ статуса')

    ordering = filters.OrderingFilter(
        fields=(
            ('queued_at', 'queued_at'),
            ('description', 'description'),
            ('status__title', 'status'),
            ('execution_time', 'execution_time'),
        )
    )

    class Meta:
        model = RunningTask
        fields = (
            'queued_at',
            'status',
        )
