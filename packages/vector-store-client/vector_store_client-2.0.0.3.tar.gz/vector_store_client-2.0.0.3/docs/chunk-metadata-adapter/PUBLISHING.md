# Публикация пакета chunk_metadata_adapter в PyPI

Этот документ описывает процесс публикации пакета chunk_metadata_adapter в Python Package Index (PyPI).

## Предварительные требования

1. Учетная запись на PyPI (https://pypi.org/account/register/)
2. Учетная запись на TestPyPI (https://test.pypi.org/account/register/) для тестирования публикации
3. Установленные инструменты для публикации:
   ```bash
   pip install build twine
   ```

## Подготовка к публикации

1. Убедитесь, что версия пакета обновлена в следующих файлах:
   - `pyproject.toml` в поле `version`
   - `chunk_metadata_adapter/__init__.py` в переменной `__version__`

2. Соберите пакет для проверки:
   ```bash
   python -m build
   ```

3. Проверьте установку пакета в отдельном окружении с помощью скрипта:
   ```bash
   python scripts/test_package_install.py
   ```

## Публикация в TestPyPI

Перед публикацией в основной индекс PyPI, рекомендуется сначала опубликовать пакет в TestPyPI.

Для публикации в TestPyPI используйте скрипт:

```bash
python scripts/publish_to_pypi.py --username YOUR_USERNAME --password YOUR_PASSWORD
```

Или укажите учетные данные через переменные окружения:

```bash
export PYPI_USERNAME=YOUR_USERNAME
export PYPI_PASSWORD=YOUR_PASSWORD
python scripts/publish_to_pypi.py
```

После публикации проверьте, что пакет доступен на TestPyPI: https://test.pypi.org/project/chunk-metadata-adapter/

Чтобы установить пакет из TestPyPI для проверки:

```bash
pip install --index-url https://test.pypi.org/simple/ chunk-metadata-adapter
```

## Публикация в основной PyPI

После успешного тестирования на TestPyPI, опубликуйте пакет в основном PyPI:

```bash
python scripts/publish_to_pypi.py --repository pypi --username YOUR_USERNAME --password YOUR_PASSWORD
```

Или с использованием переменных окружения:

```bash
export PYPI_USERNAME=YOUR_USERNAME
export PYPI_PASSWORD=YOUR_PASSWORD
python scripts/publish_to_pypi.py --repository pypi
```

После публикации проверьте, что пакет доступен на PyPI: https://pypi.org/project/chunk-metadata-adapter/

## Проверка установки из PyPI

Установите пакет из PyPI для проверки:

```bash
pip install chunk-metadata-adapter==1.1.0
```

Проверьте, что установка прошла успешно:

```python
import chunk_metadata_adapter
print(chunk_metadata_adapter.__version__)  # Должно быть "1.1.0"
```

## Использование API токенов вместо пароля

Для более безопасной публикации рекомендуется использовать API токены вместо пароля.

1. Создайте токен на PyPI: https://pypi.org/manage/account/token/
2. Используйте токен вместо пароля при публикации:
   ```bash
   python scripts/publish_to_pypi.py --repository pypi --username __token__ --password pypi-YOUR_TOKEN
   ```

## Автоматизация с GitHub Actions

Для автоматизации публикации при создании нового релиза рекомендуется использовать GitHub Actions.

Пример конфигурации в `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [created]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.x'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    - name: Build and publish
      env:
        PYPI_USERNAME: ${{ secrets.PYPI_USERNAME }}
        PYPI_PASSWORD: ${{ secrets.PYPI_PASSWORD }}
      run: |
        python -m build
        python scripts/publish_to_pypi.py --repository pypi
```

## Решение проблем

### Конфликт имен пакетов

Если имя пакета уже занято в PyPI, вам нужно изменить имя в `pyproject.toml` или связаться с владельцем пакета.

### Ошибка при загрузке

Если вы получаете ошибку при загрузке, проверьте:
1. Правильность учетных данных
2. Уникальность версии (нельзя загрузить ту же версию дважды)
3. Корректность файлов пакета

### Проблемы с зависимостями

Если есть проблемы с зависимостями, проверьте:
1. Все ли зависимости указаны в `pyproject.toml`
2. Нет ли конфликтующих версий
3. Доступны ли все зависимости на PyPI 