from django.apps import AppConfig


class CscCenterConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'csc_center'

    def ready(self):     
        import csc_center.signals   
        import csc.celery