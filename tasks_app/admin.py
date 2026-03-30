from django.contrib import admin

from tasks_app.models import Ticket, Comment, Subticket


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    """Admin configuration for Ticket model."""
    list_display = ['title', 'board', 'status', 'priority', 'created_by', 'created_at']
    list_filter = ['status', 'priority', 'created_at', 'board']
    search_fields = ['title', 'description', 'created_by__username']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['assigned_to']

    fieldsets = (
        ('Basic Information', {'fields': ('board', 'title', 'description')}),
        ('Status & Priority', {'fields': ('status', 'priority')}),
        ('Assignment', {'fields': ('created_by', 'assigned_to')}),
        ('Dates', {'fields': ('due_date', 'created_at', 'updated_at'), 'classes': ('collapse',)}),
    )


@admin.register(Subticket)
class SubticketAdmin(admin.ModelAdmin):
    """Admin configuration for Subticket model."""
    list_display = ['title', 'ticket', 'done']
    list_filter = ['done', 'ticket__board']
    search_fields = ['title', 'ticket__title']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin configuration for Comment model."""
    list_display = ['get_short_text', 'ticket', 'author', 'created_at']
    list_filter = ['created_at', 'ticket__board']
    search_fields = ['text', 'author__username', 'ticket__title']
    readonly_fields = ['created_at']

    def get_short_text(self, obj):
        if len(obj.text) > 50:
            return obj.text[:50] + '...'
        return obj.text
    get_short_text.short_description = 'Comment'
