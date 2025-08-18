from django.contrib import admin

from django_ai_agent.models import OpenAIEmbedding


@admin.register(OpenAIEmbedding)
class OpenAIEmbeddingAdmin(admin.ModelAdmin):
    list_display = ('chunk', 'model', 'embedding')
    search_fields = ('model',)
