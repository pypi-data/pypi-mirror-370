from django.contrib import admin

from django_ai_agent.models import TranscriptionModel

from .mixins import SoftValidationAdminMixin


@admin.register(TranscriptionModel)
class TranscriptionModelAdmin(SoftValidationAdminMixin, admin.ModelAdmin):
    list_display = ('provider', 'model_name')
    search_fields = ('provider', 'model_name')
