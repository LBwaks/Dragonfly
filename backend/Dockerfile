FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app
RUN addgroup --system dragonfly && adduser --system --ingroup dragonfly dragonfly
COPY pyproject.toml ./
RUN python -m pip install --no-cache-dir \
    "Django>=5.1,<5.3" \
    "djangorestframework>=3.15,<3.17" \
    "django-filter>=24.3,<26" \
    "drf-spectacular>=0.28,<0.29" \
    "psycopg[binary]>=3.2,<3.3" \
    "django-environ>=0.12,<0.13" \
    "django-cors-headers>=4.7,<5" \
    "gunicorn>=23,<24" \
    "whitenoise>=6.8,<7" \
    "httpx>=0.28,<0.29" \
    "numpy>=2.1,<3" \
    "polars>=1.20,<2" \
    "sentry-sdk[django]>=2.20,<3"
COPY config ./config
COPY apps ./apps
COPY analytics ./analytics
COPY providers ./providers
COPY manage.py ./
RUN python -m pip install --no-cache-dir --no-deps . \
    && python manage.py collectstatic --noinput \
    && chown -R dragonfly:dragonfly /app
USER dragonfly
EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
