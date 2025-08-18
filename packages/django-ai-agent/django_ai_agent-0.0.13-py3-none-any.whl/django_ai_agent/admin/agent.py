from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from django_ai_agent.models import Agent


@admin.register(Agent)
class AgentAdmin(SimpleHistoryAdmin):
    list_display = ('name', 'description', 'is_active')
    search_fields = ('name', 'description')
    filter_horizontal = ('tools', 'documents')
    history_list_display = ['name', 'description', 'is_active']
    autocomplete_fields = ['system_prompt', 'model_settings', 'transcription_model']
