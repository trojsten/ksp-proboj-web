FROM node:lts-alpine AS cssbuild

WORKDIR /app

COPY package.json pnpm-lock.yaml ./
RUN npm install -g pnpm && \
 pnpm install

COPY proboj ./proboj
COPY tailwind.config.js ./
RUN pnpm run build
CMD ["pnpm", "run", "dev"]

FROM ghcr.io/trojsten/django-docker:v6

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-cache

COPY ./Caddyfile /base/Caddyfile
COPY --chown=appuser:appuser ./ /app
COPY --chown=appuser:appuser --from=cssbuild /app/proboj/theme/static /app/proboj/theme/static

RUN PYTHONDONTWRITEBYTECODE=1 uv run --no-cache pygmentize -S monokai -f html -a .codehilite > /app/proboj/theme/static/code.css
RUN DATABASE_URL=sqlite://:memory: BASE_URL=:unset: CELERY_BROKER_URL=:unset: python -B manage.py collectstatic --no-input

ENV BASE_START=/app/start.sh
