from rest_framework.viewsets import (
    ReadOnlyModelViewSet,
)

from edu_async_tasks.core.models import (
    AsyncTaskStatus,
)
from edu_async_tasks.rest.async_task_statuses.serializers import (
    AsyncTaskStatusSerializer,
)
from edu_async_tasks.rest.utils.pagination import (
    LimitOffsetPagination,
)


class AsyncTaskStatusViewSet(ReadOnlyModelViewSet):
    queryset = AsyncTaskStatus.objects.all()
    serializer_class = AsyncTaskStatusSerializer
    pagination_class = LimitOffsetPagination
