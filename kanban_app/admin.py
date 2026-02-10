from django.contrib import admin
from kanban_app.models import Board, Task, Comment


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    """Admin configuration for Board model."""
    list_display = [
        'title', 'owner', 'get_member_count', 'created_at',
    ]
    list_filter = ['created_at', 'updated_at']
    search_fields = [
        'title', 'owner__username', 'owner__email',
    ]
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['members']

    def get_member_count(self, obj):
        """Return the number of board members."""
        return obj.members.count()

    get_member_count.short_description = 'Members'


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Admin configuration for Task model."""
    list_display = [
        'title', 'board', 'status',
        'priority', 'created_by', 'created_at',
    ]
    list_filter = ['status', 'priority', 'created_at', 'board']
    search_fields = [
        'title', 'description', 'created_by__username',
    ]
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['assigned_to']

    fieldsets = (
        ('Basic Information', {
            'fields': ('board', 'title', 'description')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority')
        }),
        ('Assignment', {
            'fields': ('created_by', 'assigned_to')
        }),
        ('Dates', {
            'fields': (
                'due_date', 'created_at', 'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin configuration for Comment model."""
    list_display = [
        'get_short_text', 'task', 'author', 'created_at',
    ]
    list_filter = ['created_at', 'task__board']
    search_fields = [
        'text', 'author__username', 'task__title',
    ]
    readonly_fields = ['created_at']

    def get_short_text(self, obj):
        """Return a truncated version of the comment text."""
        if len(obj.text) > 50:
            return obj.text[:50] + '...'
        return obj.text

    get_short_text.short_description = 'Comment'
