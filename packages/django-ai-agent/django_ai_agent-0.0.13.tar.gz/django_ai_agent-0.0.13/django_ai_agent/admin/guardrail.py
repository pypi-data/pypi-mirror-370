from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from django_ai_agent.models import Guardrail


@admin.register(Guardrail)
class GuardrailAdmin(SimpleHistoryAdmin):
    list_display = ('name', 'description', 'is_input_enabled', 'is_output_enabled')
    search_fields = ('name', 'description')
    history_list_display = ['name', 'description', 'is_input_enabled', 'is_output_enabled']
