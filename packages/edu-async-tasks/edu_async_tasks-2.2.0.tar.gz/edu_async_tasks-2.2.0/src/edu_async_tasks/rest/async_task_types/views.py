from rest_framework.viewsets import (
    ReadOnlyModelViewSet,
)

from edu_async_tasks.core.models import (
    AsyncTaskType,
)
from edu_async_tasks.rest.async_task_types.serializers import (
    AsyncTaskTypeSerializer,
)
from edu_async_tasks.rest.utils.pagination import (
    LimitOffsetPagination,
)


class AsyncTaskTypeViewSet(ReadOnlyModelViewSet):
    queryset = AsyncTaskType.objects.all()
    serializer_class = AsyncTaskTypeSerializer
    pagination_class = LimitOffsetPagination
