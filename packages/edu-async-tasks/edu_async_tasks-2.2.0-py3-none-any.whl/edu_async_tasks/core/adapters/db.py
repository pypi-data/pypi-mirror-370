from typing import (
    TYPE_CHECKING,
)

from django.core.exceptions import (
    ValidationError,
)

from ..models import (
    RunningTask,
)


if TYPE_CHECKING:
    from django.db.models.query import (
        QuerySet,
    )


class RunningTasksRepository:
    def get_by_id(self, id_: str) -> RunningTask:
        return RunningTask.objects.get(pk=id_)

    def get_by_ids(self, *ids: str) -> 'QuerySet[RunningTask]':
        """Возвращает кверисет асинхронных задач."""
        try:
            result = RunningTask.objects.filter(id__in=ids)
        except ValidationError:
            result = RunningTask.objects.none()

        return result


running_tasks_repository = RunningTasksRepository()
