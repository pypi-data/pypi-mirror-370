from rest_framework.serializers import (
    ModelSerializer,
)

from edu_async_tasks.core.models import (
    AsyncTaskStatus,
)


class AsyncTaskStatusSerializer(ModelSerializer):
    class Meta:
        model = AsyncTaskStatus
        fields = ('key', 'title')
