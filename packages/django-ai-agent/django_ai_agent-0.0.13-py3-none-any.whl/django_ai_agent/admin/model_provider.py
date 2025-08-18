from django.contrib import admin

from django_ai_agent.models import ModelProvider


@admin.register(ModelProvider)
class ModelProviderAdmin(admin.ModelAdmin):
    list_display = ('provider', 'base_url', 'api_key_variable')
    search_fields = ('provider', 'base_url', 'api_key_variable')
