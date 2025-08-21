from django.apps import (
    AppConfig as AppConfigBase,
)


class AppConfig(AppConfigBase):
    name = __package__

    def ready(self):
        import edu_async_tasks

        edu_async_tasks.set_config(edu_async_tasks.Config())
