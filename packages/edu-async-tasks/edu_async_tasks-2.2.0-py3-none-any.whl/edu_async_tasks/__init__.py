"""Реестр "Асинхронные задачи"."""

from typing import (
    Union,
)

from .config import (
    Config,
)


__config: Union[Config, None] = None


def set_config(config: Config) -> None:
    assert isinstance(config, Config)

    global __config

    __config = config


def get_config() -> Config:
    global __config

    if __config is None:
        raise ValueError('Конфигурация не установлена')

    return __config


def reset_config() -> None:
    global __config

    __config = None
