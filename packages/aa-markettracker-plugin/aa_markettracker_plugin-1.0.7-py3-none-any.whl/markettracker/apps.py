from django.apps import AppConfig
from django.conf import settings
from django.db.models import ForeignKey, SET_NULL
from django.utils.module_loading import import_string
import uuid, logging

logger = logging.getLogger(__name__)

class MarkettrackerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'markettracker'
    label = 'markettracker'
    verbose_name = "Market Tracker"

    def ready(self):
        return


