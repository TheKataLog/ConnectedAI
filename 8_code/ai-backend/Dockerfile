FROM python:3.12.6-slim AS base

# Setup env
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1
ENV POETRY__VERSION 1.8.4


FROM base AS python-deps

RUN apt-get update && apt-get install -y --no-install-recommends apt-utils curl libgomp1 g++

# Install poetry and compilation dependencies
RUN pip install "poetry==$POETRY__VERSION"

COPY . .
RUN poetry config virtualenvs.create false
RUN poetry install


