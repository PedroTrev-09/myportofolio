"""Settings for disposable browser QA; never use this module for deployment."""
import os
from portofolio.settings import *  # noqa: F403

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": os.environ["PORTFOLIO_QA_DATABASE"]}}
PRODUCTION = False
