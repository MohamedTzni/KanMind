from django.urls import path, include

from rest_framework.routers import DefaultRouter

from kanban_app.api.views import (
    BoardListCreateView, BoardDetailView,
    TicketViewSet, CommentViewSet, SubticketViewSet,
    UserViewSet, AssignedToMeView, ReviewingTasksView,
)

router = DefaultRouter()
router.register(r'tasks', TicketViewSet, basename='ticket')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'subtickets', SubticketViewSet, basename='subticket')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('boards/', BoardListCreateView.as_view(), name='board-list'),
    path('boards/<int:pk>/', BoardDetailView.as_view(), name='board-detail'),

    # Nested URL for deleting comments on a specific ticket
    path(
        'tasks/<int:ticket_id>/comments/<int:comment_id>/',
        TicketViewSet.as_view({'delete': 'delete_comment'}),
    ),
    path(
        'tasks/assigned-to-me/',
        AssignedToMeView.as_view(),
        name='assigned-to-me',
    ),
    path(
        'tasks/reviewing/',
        ReviewingTasksView.as_view(),
        name='reviewing-tasks',
    ),
    path('', include(router.urls)),
]
