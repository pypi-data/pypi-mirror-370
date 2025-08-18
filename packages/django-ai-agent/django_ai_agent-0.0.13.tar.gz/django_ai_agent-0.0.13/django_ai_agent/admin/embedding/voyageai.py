from django.contrib import admin

from django_ai_agent.models import VoyageAIEmbedding


@admin.register(VoyageAIEmbedding)
class VoyageAIEmbeddingAdmin(admin.ModelAdmin):
    list_display = ('chunk', 'model', 'embedding')
    search_fields = ('model',)
