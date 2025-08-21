import uuid

from django.db import (
    migrations,
    models,
)


class Migration(migrations.Migration):
    dependencies = [
        ('persons', '0002_auto_20240927_0651'),
    ]

    operations = [
        migrations.CreateModel(
            name='UUIDPerson',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('surname', models.TextField(db_index=True, verbose_name='Фамилия')),
                ('firstname', models.TextField(db_index=True, verbose_name='Имя')),
                ('patronymic', models.TextField(blank=True, db_index=True, null=True, verbose_name='Отчество')),
            ],
            options={
                'verbose_name': 'Физлицо с UUID',
                'verbose_name_plural': 'Физлица с UUID',
            },
        ),
    ]
