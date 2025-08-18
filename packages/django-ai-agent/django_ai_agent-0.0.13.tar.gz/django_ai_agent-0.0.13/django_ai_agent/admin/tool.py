from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from django_ai_agent.models import Tool


@admin.register(Tool)
class ToolAdmin(SimpleHistoryAdmin):
    list_display = ('name', 'description', 'is_active', 'max_retries', 'max_calls', 'max_identical_calls')
    list_filter = ('is_active', 'strict')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Parameters', {
            'fields': ('parameters_schema', 'strict')
        }),
        ('Retry Configuration', {
            'fields': ('max_retries',)
        }),
        ('Circuit Breaker', {
            'fields': ('max_calls', 'max_identical_calls'),
            'description': 'Circuit breaker settings to prevent tool calling loops'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    history_list_display = ['name', 'description', 'is_active', 'max_retries', 'max_calls', 'max_identical_calls']
