from rest_framework.routers import (
    SimpleRouter,
)

from .views import (
    RunningTasksViewSet,
)


router = SimpleRouter()

router.register('async-tasks', RunningTasksViewSet, basename='async-tasks')
