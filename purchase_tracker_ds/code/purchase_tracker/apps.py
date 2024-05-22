from django.apps import AppConfig


class PurchaseTrackerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = "purchase_tracker"
    
    def ready(self):
        import purchase_tracker.signals
