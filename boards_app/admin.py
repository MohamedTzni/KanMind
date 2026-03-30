from django.contrib import admin

from boards_app.models import Board


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    """Admin configuration for Board model."""
    list_display = ['title', 'owner', 'get_member_count', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['title', 'description', 'owner__username', 'owner__email']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['members']

    def get_member_count(self, obj):
        return obj.members.count()
    get_member_count.short_description = 'Members'
