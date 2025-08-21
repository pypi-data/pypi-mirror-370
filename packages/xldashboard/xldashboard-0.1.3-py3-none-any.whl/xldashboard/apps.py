from django.apps import AppConfig
from django.conf import settings

from .jazzmin_default import JAZZMIN_SETTINGS as _JAZZMIN_SETTINGS
from .jazzmin_default import JAZZMIN_UI_TWEAKS as _JAZZMIN_UI_TWEAKS


class XLDashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'xldashboard'

    def ready(self) -> None:  # pragma: no cover - simple settings assignment
        base = getattr(settings, 'JAZZMIN_SETTINGS', {})
        settings.JAZZMIN_SETTINGS = _JAZZMIN_SETTINGS | base

        links = settings.JAZZMIN_SETTINGS.get('usermenu_links', [])
        ctx = {
            'DOMAIN_URL': getattr(settings, 'DOMAIN_URL', ''),
            'LOGUI_URL_PREFIX': getattr(settings, 'LOGUI_URL_PREFIX', ''),
            'REDISUI_URL_PREFIX': getattr(settings, 'REDISUI_URL_PREFIX', ''),
        }
        for link in links:
            link['url'] = link['url'].format_map(ctx)

        base_ui = getattr(settings, 'JAZZMIN_UI_TWEAKS', {})
        settings.JAZZMIN_UI_TWEAKS = _JAZZMIN_UI_TWEAKS | base_ui
