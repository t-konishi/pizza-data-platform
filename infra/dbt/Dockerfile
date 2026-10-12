FROM python:3.12-slim-bookworm

ARG DBT_CORE_VERSION=1.12.5
ARG DBT_DUCKDB_VERSION=1.11.0

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       git \
       ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    "dbt-core==${DBT_CORE_VERSION}" \
    "dbt-duckdb==${DBT_DUCKDB_VERSION}"

RUN groupadd --gid 1000 dbt \
    && useradd --uid 1000 --gid 1000 --create-home dbt

USER dbt

WORKDIR /workspace/dbt

CMD ["dbt", "--version"]
