FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-17-jre-headless \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

ENV ALLURE_VERSION=2.32.0
RUN curl -fsSL "https://github.com/allure-framework/allure2/releases/download/${ALLURE_VERSION}/allure-${ALLURE_VERSION}.tgz" \
    | tar -xz -C /opt/ \
    && ln -sf "/opt/allure-${ALLURE_VERSION}/bin/allure" /usr/local/bin/allure \
    && allure --version

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

# alluredir задаётся в pyproject.toml → allure-results
CMD ["pytest", "--env=dev"]
