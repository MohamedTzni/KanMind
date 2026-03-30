from django.urls import path, include

from rest_framework.routers import DefaultRouter

from tasks_app.api.views import (
    TicketViewSet, CommentViewSet, SubticketViewSet,
    UserViewSet, AssignedToMeView, ReviewingTasksView,
)

router = DefaultRouter()
router.register(r'tasks', TicketViewSet, basename='ticket')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'subtickets', SubticketViewSet, basename='subticket')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path(
        'tasks/<int:ticket_id>/comments/<int:comment_id>/',
        TicketViewSet.as_view({'delete': 'delete_comment'}),
    ),
    path('tasks/assigned-to-me/', AssignedToMeView.as_view(), name='assigned-to-me'),
    path('tasks/reviewing/', ReviewingTasksView.as_view(), name='reviewing-tasks'),
    path('', include(router.urls)),
]
