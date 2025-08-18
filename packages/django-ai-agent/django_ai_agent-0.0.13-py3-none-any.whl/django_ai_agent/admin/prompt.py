from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from django_ai_agent.models import Prompt

from .mixins import SoftValidationAdminMixin


@admin.register(Prompt)
class PromptAdmin(SoftValidationAdminMixin, SimpleHistoryAdmin):
    list_display = ('name', 'template')
    search_fields = ('name', 'template')
    history_list_display = ['name']
