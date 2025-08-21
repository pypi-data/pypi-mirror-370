from rest_framework.serializers import (
    ModelSerializer,
)

from edu_async_tasks.core.models import (
    AsyncTaskType,
)


class AsyncTaskTypeSerializer(ModelSerializer):
    class Meta:
        model = AsyncTaskType
        fields = ('key', 'title')
