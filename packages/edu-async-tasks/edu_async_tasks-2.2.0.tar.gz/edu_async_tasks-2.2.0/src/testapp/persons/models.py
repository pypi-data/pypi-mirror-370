import uuid

from django.db import (
    models,
)


class Person(models.Model):
    surname = models.TextField('Фамилия', db_index=True)
    firstname = models.TextField('Имя', db_index=True)
    patronymic = models.TextField('Отчество', db_index=True, null=True, blank=True)

    class Meta:
        verbose_name = 'Физлицо'
        verbose_name_plural = 'Физлица'


class UUIDPerson(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    surname = models.TextField('Фамилия', db_index=True)
    firstname = models.TextField('Имя', db_index=True)
    patronymic = models.TextField('Отчество', db_index=True, null=True, blank=True)

    class Meta:
        verbose_name = 'Физлицо с UUID'
        verbose_name_plural = 'Физлица с UUID'
