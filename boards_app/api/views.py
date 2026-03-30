from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from auth_app.api.serializers import UserSerializer
from boards_app.api.permissions import IsOwnerOrMember
from boards_app.api.serializers import BoardListSerializer, BoardDetailSerializer
from boards_app.models import Board


class BoardListCreateView(generics.ListCreateAPIView):
    """List boards of the authenticated user or create a new board."""
    serializer_class = BoardListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return Board.objects.all()

        owned_boards = Board.objects.filter(owner=user)
        member_boards = Board.objects.filter(members=user)
        return (owned_boards | member_boards).distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a single board."""
    serializer_class = BoardDetailSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrMember]

    def get_queryset(self):
        return Board.objects.all()

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

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        instance.refresh_from_db()

        return Response(
            self._build_patch_response(instance),
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.owner != request.user:
            raise PermissionDenied("Only the board owner can delete this board.")

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)