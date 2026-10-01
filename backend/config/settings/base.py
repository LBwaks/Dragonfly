from datetime import date
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parents[2]
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(BASE_DIR.parent / ".env")
SECRET_KEY = env("DJANGO_SECRET_KEY", default="unsafe-local-development-key")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=["http://localhost:3000"])
CORS_ALLOW_CREDENTIALS = True

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "django_filters",
    "corsheaders",
    "drf_spectacular",
    "apps.accounts",
    "apps.instruments",
    "apps.market_data",
    "apps.jobs",
    "apps.technicals",
    "apps.screeners",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "config.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"
DATABASES = {
    "default": env.db("DATABASE_URL", default=f"sqlite:///{(BASE_DIR / 'db.sqlite3').as_posix()}")
}
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 50,
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticatedOrReadOnly"],
}
SPECTACULAR_SETTINGS = {
    "TITLE": "Dragonfly API",
    "DESCRIPTION": "Provider-agnostic market intelligence and stock screening API.",
    "VERSION": "1.0.0",
}
NASDAQ_VERIFY_SSL = env.bool("NASDAQ_VERIFY_SSL", default=True)
MARKET_DATA_PROVIDERS = {
    "instrument_overview": env.list("OVERVIEW_PROVIDERS", default=["nasdaq"]),
    "symbol_universe": env.list(
        "UNIVERSE_PROVIDERS",
        default=[env("PRIMARY_UNIVERSE_PROVIDER", default="alpaca")],
    ),
    "quote": env.list(
        "QUOTE_PROVIDERS",
        default=[env("PRIMARY_QUOTE_PROVIDER", default="finnhub")],
    ),
    "company_profile": env.list(
        "PROFILE_PROVIDERS",
        default=[env("PRIMARY_QUOTE_PROVIDER", default="finnhub")],
    ),
    "historical_ohlcv": env.list(
        "OHLCV_PROVIDERS",
        default=[env("PRIMARY_OHLCV_PROVIDER", default="alpaca")],
    ),
    "intraday_ohlcv": env.list(
        "INTRADAY_PROVIDERS",
        default=[env("PRIMARY_OHLCV_PROVIDER", default="alpaca")],
    ),
    "fundamentals": env.list(
        "FUNDAMENTAL_PROVIDERS",
        default=[env("PRIMARY_FUNDAMENTALS_PROVIDER", default="finnhub")],
    ),
    "company_news": env.list(
        "NEWS_PROVIDERS",
        default=[env("PRIMARY_NEWS_PROVIDER", default="finnhub")],
    ),
}
FINNHUB_API_KEY = env("FINNHUB_API_KEY", default="")
ALPACA_API_KEY_ID = env("ALPACA_API_KEY_ID", default="")
ALPACA_API_SECRET_KEY = env("ALPACA_API_SECRET_KEY", default="")
ALPACA_DATA_FEED = env("ALPACA_DATA_FEED", default="iex")
ALPACA_ADJUSTMENT = env("ALPACA_ADJUSTMENT", default="all")
ALPACA_ASSETS_BASE_URL = env("ALPACA_ASSETS_BASE_URL", default="https://paper-api.alpaca.markets")
ALPACA_ASSET_EXCHANGES = env.list(
    "ALPACA_ASSET_EXCHANGES", default=["NASDAQ", "NYSE", "AMEX", "ARCA", "BATS"]
)
MARKET_DATA_HISTORY_START = date.fromisoformat(
    env("MARKET_DATA_HISTORY_START", default="1900-01-01")
)
SENTRY_DSN = env("SENTRY_DSN", default="")
SENTRY_ENVIRONMENT = env("SENTRY_ENVIRONMENT", default="local")
SENTRY_RELEASE = env("SENTRY_RELEASE", default="")
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"json": {"()": "config.logging.JsonFormatter"}},
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "json"}},
    # Provider clients can include credentials or signed URLs in request metadata.
    "loggers": {
        "httpx": {"handlers": ["console"], "level": "WARNING", "propagate": False},
        "httpcore": {"handlers": ["console"], "level": "WARNING", "propagate": False},
    },
    "root": {"handlers": ["console"], "level": env("LOG_LEVEL", default="INFO")},
}
