from django.contrib import admin

from django_ai_agent.models import Conversation, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ('created_at', 'updated_at')
    fields = ('message_history', 'created_at', 'updated_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('created_at')


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('agent', 'user', 'title', 'is_active', 'created_at')
    search_fields = ('title', 'agent__name', 'user__first_name', 'user__last_name')
    autocomplete_fields = ('agent',)
    inlines = [MessageInline]
    readonly_fields = ('created_at', 'updated_at')
