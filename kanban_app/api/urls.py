from django.urls import path, include

from rest_framework.routers import DefaultRouter

from kanban_app.api.views import BoardViewSet, TaskViewSet, CommentViewSet, UserViewSet, AssignedToMeView, ReviewingTasksView

router = DefaultRouter()
router.register(r'boards', BoardViewSet, basename='board')
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('tasks/assigned-to-me/', AssignedToMeView.as_view(), name='assigned-to-me'),
    path('tasks/reviewing/', ReviewingTasksView.as_view(), name='reviewing-tasks'),
    path('', include(router.urls)),
]