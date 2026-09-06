from decouple import config

environment = config("DJANGO_SETTINGS_MODULE", default="config.settings.development")

if "production" in environment:
    from .production import *  # noqa: F403
else:
    from .development import *  # noqa: F403
