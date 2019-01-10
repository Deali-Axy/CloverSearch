import os, django
import profile

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Config.settings")
django.setup()

from Search.config import ConfigManager
from Search.query import SearchQuery

print(ConfigManager.__dict__)
result = profile.run("SearchQuery.query('想的念')", "search_profile")
