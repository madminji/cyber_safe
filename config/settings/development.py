from .base import *  # noqa: F403

DEBUG = config("DJANGO_DEBUG", default=True, cast=bool)  # noqa: F405

