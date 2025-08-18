from django.apps import AppConfig


class UIElementsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    # Define the app label explicitly, matching the models
    name = 'shared_models.ui_elements' 
    label = 'ui_elements' # This label must match the app_label in models.py
    verbose_name = "UI Elements (Shared)" # Optional: human-readable name 