from unittest.case import (
    TestCase,
)

from pydantic import (
    ValidationError,
)

import edu_async_tasks


class ConfigTestCase(TestCase):
    def test_min_config(self):
        config = edu_async_tasks.Config()

        self.assertIsNotNone(config.task_start_time_format)
        self.assertEqual(config.task_start_time_format, edu_async_tasks.Config.task_start_time_format.default)

        self.assertIsNotNone(config.task_default_user_name)
        self.assertEqual(config.task_default_user_name, edu_async_tasks.Config.task_default_user_name.default)

        self.assertIsNotNone(config.default_lock_expire)
        self.assertEqual(config.default_lock_expire, edu_async_tasks.Config.default_lock_expire.default)

    def test_max_config(self):
        values = {
            'task_start_time_format': '%Y-%m-%d %H:%M:%S',
            'task_default_user_name': 'Foo Bar',
            'default_lock_expire': 1 * 60,
            'filter_days_after_start': 1,
        }

        config = edu_async_tasks.Config(**values)

        self.assertEqual(config.task_start_time_format, values['task_start_time_format'])
        self.assertEqual(config.task_default_user_name, values['task_default_user_name'])
        self.assertEqual(config.default_lock_expire, values['default_lock_expire'])

    def test_config_validation(self):
        for value in ['', None, set()]:
            with self.subTest(f'{value} ({type(value)})'), self.assertRaises(ValidationError):
                edu_async_tasks.Config(task_start_time_format=value)

        for value in ['', None, set()]:
            with self.subTest(f'{value} ({type(value)})'), self.assertRaises(ValidationError):
                edu_async_tasks.Config(task_default_user_name=value)

        for value in [0, '', None, set()]:
            with self.subTest(f'{value} ({type(value)})'), self.assertRaises(ValidationError):
                edu_async_tasks.Config(default_lock_expire=value)

        for value in [0, '', None, set()]:
            with self.subTest(f'{value} ({type(value)})'), self.assertRaises(ValidationError):
                edu_async_tasks.Config(filter_days_after_start=value)

    def test_config_set(self):
        config = edu_async_tasks.Config(
            task_start_time_format='%H', task_default_user_name='Foo', default_lock_expire=1, filter_days_after_start=1
        )

        edu_async_tasks.reset_config()

        with self.assertRaises(ValueError):
            edu_async_tasks.get_config()

        edu_async_tasks.set_config(config)

        self.assertIs(edu_async_tasks.get_config(), config)
