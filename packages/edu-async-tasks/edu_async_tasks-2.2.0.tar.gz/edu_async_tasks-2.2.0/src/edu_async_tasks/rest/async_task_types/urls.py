from django.urls import (
    include,
    path,
)
from rest_framework.routers import (
    SimpleRouter,
)

from .views import (
    AsyncTaskTypeViewSet,
)


router = SimpleRouter()

router.register('async-task-types', AsyncTaskTypeViewSet, basename='async-task-types')

urlpatterns = [
    path('', include(router.urls)),
]
