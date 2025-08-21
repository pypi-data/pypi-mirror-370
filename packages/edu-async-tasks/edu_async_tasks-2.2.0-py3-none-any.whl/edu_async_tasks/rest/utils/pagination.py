from rest_framework.pagination import (
    LimitOffsetPagination as BaseLimitOffsetPagination,
)


class LimitOffsetPagination(BaseLimitOffsetPagination):
    """Пагинатор с поддержкой лимита и смещения."""

    offset_query_param = 'start'
    default_limit = 25
