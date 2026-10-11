FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

# alluredir задаётся в pyproject.toml → allure-results
CMD ["pytest", "--env=dev"]
