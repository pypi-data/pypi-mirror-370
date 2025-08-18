from django.contrib import admin

from django_ai_agent.models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'content', 'source', 'url')
    search_fields = ('name', 'content', 'source', 'url')

    @admin.display(description='Content')
    def content(self, obj):
        return f'{obj.content[:100]}...'
