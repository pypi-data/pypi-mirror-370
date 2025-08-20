FROM rockylinux:9.3

RUN dnf install -y \
      gcc \
    && dnf clean all

ENV UV_COMPILE_BYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

COPY --from=ghcr.io/astral-sh/uv:0.8.7 /uv /uvx /bin/

ARG AIRFLOW_VERSION=2.7.1
ARG PYTHON_VERSION=3.10

RUN uv venv /opt/venv --python=${PYTHON_VERSION}

ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN uv pip install  \
    "apache-airflow==${AIRFLOW_VERSION}" --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"
