from django.urls import (
    include,
    path,
)
from rest_framework.routers import (
    SimpleRouter,
)

from .views import (
    AsyncTaskStatusViewSet,
)


router = SimpleRouter()

router.register('async-task-statuses', AsyncTaskStatusViewSet, basename='async-task-statuses')

urlpatterns = [
    path('', include(router.urls)),
]
