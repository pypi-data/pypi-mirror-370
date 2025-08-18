from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from django_ai_agent.models import ModelSettings


@admin.register(ModelSettings)
class ModelSettingsAdmin(SimpleHistoryAdmin):
    list_display = (
        'provider',
        'model_name',
        'temperature',
        'max_tokens',
    )
    search_fields = ('provider__provider', 'model_name')
    history_list_display = ['provider', 'model_name', 'temperature', 'max_tokens']
    autocomplete_fields = ['provider']
