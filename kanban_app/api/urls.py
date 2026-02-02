from django.urls import path, include
from rest_framework.routers import DefaultRouter
from kanban_app.api.views import BoardViewSet, TaskViewSet, CommentViewSet, UserViewSet

# Router für ViewSets
router = DefaultRouter()
router.register(r'boards', BoardViewSet, basename='board')
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
]