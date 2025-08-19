from django.conf import settings

TEMPLATE_TIME_FORMAT = getattr(settings, "DJADMIN_TEMPLATE_TIME_FORMAT", "d M Y, P O")
EXCLUDE_BOOTSTRAP_TAGS = getattr(settings, "DJADMIN_EXCLUDE_BOOTSTRAP_TAGS", False)
