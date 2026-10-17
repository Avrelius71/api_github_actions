# API-тесты Restful Booker

Фреймворк для тестирования REST API [Restful Booker](https://restful-booker.herokuapp.com/): pytest, Pydantic, Faker, Allure, Docker и GitHub Actions.

## Подготовка

1. Python 3.11+ (локально рекомендуется совпадать с `target-version` в `pyproject.toml` для Ruff).
2. Виртуальное окружение и зависимости:

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

3. Скопируйте `.env.example` в `.env` и задайте `BOOKER_USERNAME` / `BOOKER_PASSWORD` (см. `config/environments.py`). Файл `.env` подхватывается Docker Compose автоматически.

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

Маркеры:

```bash
pytest -m smoke
pytest -m regression
```

## Запуск в Docker

Одной командой: прогон тестов и сборка Allure-отчёта внутри контейнера. Папки `allure-results` и `allure-report` очищаются и монтируются на хост:

```bash
docker compose run --rm tests
```

После прогона откройте `allure-report/index.html` в браузере (или `allure open allure-report`, если CLI установлен локально).

Смена окружения:

```bash
TEST_ENV=stage docker compose run --rm tests
```

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

## Allure (локально без Docker)

После `pytest` в каталоге `allure-results` появятся сырые данные (путь задан в `pyproject.toml` через `--alluredir`).

1. Установите [Allure Commandline](https://github.com/allure-framework/allure2/releases) и убедитесь, что команда `allure` доступна в `PATH` (нужна Java).
2. Откройте отчёт:

```bash
allure serve allure-results
```

Либо статический отчёт:

```bash
allure generate allure-results -o allure-report --clean
allure open allure-report
```

В отчёте шаги описаны человекочитаемо: HTTP-запросы, проверки (assert) и валидация ответов по Pydantic-схемам.

Через Docker Allure CLI на хосте не нужен — отчёт уже лежит в `allure-report/` после `docker compose run --rm tests`.

## CI/CD (GitHub Actions)

Пайплайн описан в `.github/workflows/api_tests.yml`.

**Когда запускается:** на каждый `pull_request` в ветку `main`.

**Секреты репозитория** (Settings → Secrets and variables → Actions):

- `BOOKER_USERNAME`
- `BOOKER_PASSWORD`

Без них шаг с тестами получит пустые креды.

**Что делает:**

1. Собирает образ и одной командой гоняет тесты + Allure в Docker (`docker compose run --rm tests`).
2. Сохраняет готовый `allure-report` как artifact (хранение 14 дней).

**Как посмотреть отчёт из CI:**

1. Откройте вкладку Actions у pull request / репозитория.
2. Выберите успешный (или завершённый) workflow run.
3. Внизу страницы скачайте artifact `allure-report`.
4. Распакуйте архив и откройте `index.html` локально (удобнее через `allure open` или любой статический сервер).

## Поведение pytest из конфига

В `pyproject.toml` заданы: таймаут теста 60 с (`pytest-timeout`), до двух повторов упавших тестов с паузой 1 с (`pytest-rerunfailures`), строгие маркеры, логи в CLI на уровне INFO.
