from pydantic.class_validators import (
    validator,
)
from pydantic.dataclasses import (
    dataclass,
)
from pydantic.fields import (
    Field,
)


@dataclass
class Config:
    task_start_time_format: str = Field(title='Формат времени', default='%H:%M %d.%m.%Y')
    task_default_user_name: str = Field(title='Имя пользователя по-умолчанию', default='Система')
    default_lock_expire: int = Field(  # noqa
        title='Задача считается уникальной в течение', default=30 * 60
    )
    filter_days_after_start: int = Field(  # noqa
        title='Фильтр реестра - количество дней, в течение которых были запущены задачи', default=7
    )

    @validator('task_start_time_format')
    @classmethod
    def validate_task_start_time_format(cls, value):
        if not isinstance(value, str) or not value:
            raise ValueError(f'Неверное значение поля "{cls.task_start_time_format.title}"')
        return value

    @validator('task_default_user_name')
    @classmethod
    def validate_task_default_user_name(cls, value):
        if not isinstance(value, str) or not value:
            raise ValueError(f'Неверное значение поля "{cls.task_default_user_name.title}"')
        return value

    @validator('default_lock_expire')
    @classmethod
    def validate_default_lock_expire(cls, value):
        if not isinstance(value, int) or value <= 0:
            raise ValueError(f'Неверное значение поля "{cls.default_lock_expire.title}"')
        return value

    @validator('filter_days_after_start')
    @classmethod
    def validate_filter_days_after_start(cls, value):
        if not isinstance(value, int) or value <= 0:
            raise ValueError(f'Неверное значение поля "{cls.filter_days_after_start.title}"')
        return value
