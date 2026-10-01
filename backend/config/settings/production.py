from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403

DEBUG = False
if SECRET_KEY == "unsafe-local-development-key":  # noqa: F405
    raise ImproperlyConfigured("DJANGO_SECRET_KEY must be set in production")
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

if SENTRY_DSN:  # noqa: F405
    import sentry_sdk

    sentry_sdk.init(
        dsn=SENTRY_DSN,  # noqa: F405
        environment=SENTRY_ENVIRONMENT,  # noqa: F405
        release=SENTRY_RELEASE or None,  # noqa: F405
        send_default_pii=False,
        traces_sample_rate=0.05,
    )
