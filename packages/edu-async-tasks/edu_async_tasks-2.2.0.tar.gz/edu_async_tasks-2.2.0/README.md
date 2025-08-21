# Реестр асинхронных задач

## Сборка и распространение
$ python -m build && \
  twine check ./dist/* && \
  twine upload ./dist/* --repository-url=http://... -u user.name -p userpassword

## Запуск тестов
$ source deactivate
$ pip install tox tox-docker==5.0.0
$ tox
