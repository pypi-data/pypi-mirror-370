from django.urls import (
    include,
    path,
)
from rest_framework.routers import (
    DefaultRouter,
)

from .utils.bootstrap import (
    import_submodules,
)


router = DefaultRouter()


for module in import_submodules(__package__, '.urls'):
    router.registry.extend(module.router.registry)


urlpatterns = [
    path('', include(router.urls)),
]
