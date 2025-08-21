from django.core.management import (
    call_command,
)
from django.db import (
    migrations,
)


def load_fixture(apps, _):
    call_command('loaddata', 'persons', app_label='persons')


class Migration(migrations.Migration):
    dependencies = [
        ('persons', '0001_initial'),
    ]

    operations = [migrations.RunPython(load_fixture)]
