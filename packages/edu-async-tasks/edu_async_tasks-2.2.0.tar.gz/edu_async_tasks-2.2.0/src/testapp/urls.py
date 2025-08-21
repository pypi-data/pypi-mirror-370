from django.urls import (
    include,
    path,
)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)
from rest_framework.routers import (
    SimpleRouter,
)

from edu_async_tasks.rest.async_task_statuses.views import (
    AsyncTaskStatusViewSet,
)
from edu_async_tasks.rest.async_task_types.views import (
    AsyncTaskTypeViewSet,
)
from edu_async_tasks.rest.running_tasks.views import (
    RunningTasksViewSet,
)


router = SimpleRouter()
router.register('async-tasks', RunningTasksViewSet, basename='async-tasks')
router.register('async-task-statuses', AsyncTaskStatusViewSet, basename='async-task-statuses')
router.register('async-task-types', AsyncTaskTypeViewSet, basename='async-task-types')

urlpatterns = [
    path('', include('edu_async_tasks.rest.urls')),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'schema/swagger-ui/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui',
    ),
]
