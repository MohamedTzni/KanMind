from django.contrib.auth.models import User

from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from auth_app.api.serializers import UserSerializer, UserListSerializer
from boards_app.api.permissions import IsOwnerOrMember
from boards_app.api.serializers import BoardListSerializer, BoardDetailSerializer
from boards_app.models import Board


class BoardListCreateView(generics.ListCreateAPIView):
    """View for listing and creating boards."""
    serializer_class = BoardListSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrMember]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Board.objects.all()
        owned = Board.objects.filter(owner=user)
        member = Board.objects.filter(members=user)
        return (owned | member).distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    """View for retrieve, update and delete of a single board."""
    serializer_class = BoardDetailSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrMember]

    def get_queryset(self):
        return Board.objects.all()

    def get_object(self):
        obj = super().get_object()
        if obj.owner != self.request.user and not obj.members.filter(id=self.request.user.id).exists():
            raise PermissionDenied()
        return obj

    def _build_owner_data(self, owner):
        return {
            "id": owner.id,
            "email": owner.email,
            "fullname": UserSerializer().get_fullname(owner),
        }

    def _build_patch_response(self, instance):
        return {
            "id": instance.id,
            "title": instance.title,
            "owner_data": self._build_owner_data(instance.owner),
            "members_data": UserSerializer(instance.members.all(), many=True).data,
        }

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.owner != request.user:
            return Response(
                {"detail": "Only the board owner can delete this board."},
                status=status.HTTP_403_FORBIDDEN,
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(self._build_patch_response(instance))


class UserViewSet:
    pass
