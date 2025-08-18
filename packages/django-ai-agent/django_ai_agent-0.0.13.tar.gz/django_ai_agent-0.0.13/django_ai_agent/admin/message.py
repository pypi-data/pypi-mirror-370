from django.contrib import admin

from django_ai_agent.models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('conversation', 'message_history')
    search_fields = ('message_history',)
