from django.db import (
    migrations,
    models,
)


class Migration(migrations.Migration):
    dependencies = [
        ('edu_async_tasks_core', '0002_task_type_and_status_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='runningtask',
            name='profile_id',
            field=models.CharField(blank=True, max_length=36, null=True),
        ),
    ]
