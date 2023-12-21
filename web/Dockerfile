FROM node:20.8.0-alpine AS cssbuild

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY proboj ./proboj
COPY tailwind.config.js ./
RUN npm run build
CMD ["npm", "run", "dev"]

FROM python:3.11-slim-bullseye
WORKDIR /app
RUN useradd --create-home appuser

ENV PYTHONUNBUFFERED 1
ENV PYTHONFAULTHANDLER 1
ENV POETRY_VIRTUALENVS_CREATE 0

RUN export DEBIAN_FRONTEND=noninteractive \
    && apt update \
    && apt -y upgrade \
#    && apt -y install nodejs npm \
    && apt -y clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root

USER appuser

COPY --chown=appuser:appuser . /app/
COPY --chown=appuser:appuser --from=cssbuild /app/proboj/theme/static /app/proboj/theme/static
CMD ["/app/start.sh"]
