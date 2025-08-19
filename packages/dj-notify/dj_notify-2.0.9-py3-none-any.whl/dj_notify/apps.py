from django.apps import AppConfig

class DjNotifyConfig(AppConfig):
    name = 'dj_notify'

    def ready(self):
        import dj_notify.signals  # connect the signals
