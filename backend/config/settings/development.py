from .base import *  # noqa: F403

DEBUG = True

INSTALLED_APPS += ["django_extensions"] if False else []  # noqa: F405

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
