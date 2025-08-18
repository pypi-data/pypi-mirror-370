from django.contrib import admin

from django_ai_agent.models import DocumentChunk


@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    list_display = ('document', 'content')
    search_fields = ('document__name', 'content')
