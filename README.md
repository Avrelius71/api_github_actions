# API-тесты Restful Booker

## Подготовка

1. Python 3.11+ (локально рекомендуется совпадать с `target-version` в `pyproject.toml` для Ruff).
2. Виртуальное окружение и зависимости:

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

3. Скопируйте `.env.example` в `.env` и при необходимости задайте `BOOKER_USERNAME` / `BOOKER_PASSWORD` (см. `config/environments.py`).

## Запуск тестов по окружениям

Окружение задаётся флагом `--env` (см. `conftest.py`): `dev` или `stage`.

**Локально (по умолчанию `dev`):**

```bash
pytest
```

**Явно dev:**

```bash
pytest --env=dev
```

**Stage:**

```bash
pytest --env=stage
```

Убедитесь, что для stage в `config/environments.py` задан корректный URL, если он отличается от dev.

## Параллельный прогон (pytest-xdist)

```bash
pytest -n auto
```

Можно комбинировать с окружением, например: `pytest --env=stage -n auto`.

## Линтинг (Ruff)

```bash
ruff check .
ruff format --check .
```

Автоисправления: `ruff check . --fix` и `ruff format .`.

Подробный вывод pytest локально: `pytest -v` (в `pyproject.toml` по умолчанию без `-v`, чтобы не засорять CI).

## Allure

После прогона в каталоге `allure-results` появятся сырые данные отчёта (путь задан в `pyproject.toml` через `--alluredir`).

1. Установите [Allure Commandline](https://github.com/allure-framework/allure2/releases) и убедитесь, что команда `allure` доступна в `PATH` (нужна Java).
2. Откройте отчёт в браузере:

```bash
allure serve allure-results
```

Либо сгенерируйте статический отчёт и откройте `index.html`:

```bash
allure generate allure-results -o allure-report --clean
allure open allure-report
```

## Поведение pytest из конфига

В `pyproject.toml` заданы: таймаут теста 60 с (`pytest-timeout`), до двух повторов упавших тестов с паузой 1 с (`pytest-rerunfailures`), строгие маркеры, логи в CLI на уровне INFO.
