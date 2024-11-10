"""Apps.py"""
from django.apps import AppConfig

class ExpensesConfig(AppConfig):
    """apps config"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'expenses'
