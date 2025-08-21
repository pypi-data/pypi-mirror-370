from rest_framework import (
    serializers,
)
from rest_framework.fields import (
    DurationField,
)

from edu_async_tasks.core.models import (
    RunningTask,
)
from edu_async_tasks.core.services import (
    get_running_task_result,
)
from edu_async_tasks.rest.async_task_statuses.serializers import (
    AsyncTaskStatusSerializer,
)


class TaskResultFileSerializer(serializers.Serializer):
    """Сериализатор данных о файле в результатах выполнения задачи."""

    description = serializers.CharField(allow_null=True, label='Описание файла')
    url = serializers.CharField(label='Ссылка на файл')


class TaskResultSerializer(serializers.Serializer):
    """Сериализатор результата задачи."""

    values = serializers.DictField(
        label='Результаты выполнения', help_text='Набор пар ключ-значение с результатами выполнения задачи'
    )
    error_text = serializers.CharField(source='error', label='Текст ошибки (если возникла)')
    files = TaskResultFileSerializer(many=True, label='Набор файлов, сгенерированных задачей')


class RunningTaskSerializer(serializers.ModelSerializer):
    status = AsyncTaskStatusSerializer()
    task_result = TaskResultSerializer()
    execution_time = DurationField(read_only=True)
    organization_id = serializers.CharField(read_only=True, allow_null=True)

    def to_representation(self, instance):
        instance.task_result = get_running_task_result(instance)

        return super().to_representation(instance)

    class Meta:
        model = RunningTask
        fields = (
            'id',
            'queued_at',
            'started_at',
            'name',
            'description',
            'status',
            'task_result',
            'finished_at',
            'execution_time',
            'organization_id',
        )


class RevokeTasksActionSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.CharField(), allow_empty=False)
