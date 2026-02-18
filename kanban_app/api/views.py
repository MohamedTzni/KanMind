from django.contrib.auth.models import User

from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from kanban_app.api.permissions import IsBoardMember, IsOwner, IsOwnerOrMember
from kanban_app.api.serializers import (
    BoardListSerializer, BoardDetailSerializer,
    TicketSerializer, CommentSerializer, UserSerializer,
    SubticketSerializer,
)
from kanban_app.models import Board, Ticket, Comment, Subticket


class BoardListCreateView(generics.ListCreateAPIView):
    """
    View for listing and creating boards.
    Supports GET for a filtered list and POST for creation.
    """
    serializer_class = BoardListSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrMember]

    def get_queryset(self):
        """
        Return all boards if superuser, otherwise only those where the user
        is an owner or member.
        """
        user = self.request.user
        if user.is_superuser:
            return Board.objects.all()
            
        owned = Board.objects.filter(owner=user)
        member = Board.objects.filter(members=user)
        return (owned | member).distinct()

    def perform_create(self, serializer):
        """
        Custom save logic for new boards.
        Automatically assigns the requesting user as the board owner.
        """
        serializer.save(owner=self.request.user)


class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    View for individual board operations.
    Supports GET (retrieve), PUT/PATCH (update), and DELETE.
    """
    serializer_class = BoardDetailSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrMember]

    def get_queryset(self):
        """
        Filters boards to only those the user can access.
        Returns 404 if the board exists but the user is not a member/owner.
        """
        user = self.request.user
        owned = Board.objects.filter(owner=user)
        member = Board.objects.filter(members=user)
        return (owned | member).distinct()

    def update(self, request, *args, **kwargs):
        """Return owner_data and members_data (without tickets) for PATCH/PUT."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        owner = instance.owner
        user_serializer = UserSerializer()
        return Response({
            "id": instance.id,
            "title": instance.title,
            "owner_data": {
                "id": owner.id,
                "email": owner.email,
                "fullname": user_serializer.get_fullname(owner),
            },
            "members_data": UserSerializer(instance.members.all(), many=True).data,
        })


class TicketViewSet(viewsets.ModelViewSet):
    """CRUD for tickets."""
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated, IsBoardMember]

    def get_queryset(self):
        """Return filtered tickets for list, all tickets for detail actions."""
        if self.action == 'list':
            user = self.request.user
            owned_boards = Board.objects.filter(owner=user)
            member_boards = Board.objects.filter(members=user)
            all_boards = owned_boards | member_boards
            return Ticket.objects.filter(board__in=all_boards)
        return Ticket.objects.all()

    def create(self, request, *args, **kwargs):
        """Check board membership before creating a ticket."""
        board_id = request.data.get('board')
        if not board_id:
            return Response(
                {"board": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            board = Board.objects.get(pk=board_id)
        except Board.DoesNotExist:
            return Response(
                {"detail": "Board not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        user = request.user
        if board.owner != user and user not in board.members.all():
            return Response(
                {"detail": "You must be a member of the board."},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        instance = serializer.instance
        return Response(
            self._ticket_response(instance),
            status=status.HTTP_201_CREATED,
        )

    def _ticket_response(self, instance):
        """Build a response with only the fields required by the API spec."""
        user_serializer = UserSerializer()
        assignee_data = None
        if instance.assignee:
            assignee_data = {
                "id": instance.assignee.id,
                "email": instance.assignee.email,
                "fullname": user_serializer.get_fullname(instance.assignee),
            }
        reviewer_data = None
        if instance.reviewer:
            reviewer_data = {
                "id": instance.reviewer.id,
                "email": instance.reviewer.email,
                "fullname": user_serializer.get_fullname(instance.reviewer),
            }
        return {
            "id": instance.id,
            "board": instance.board_id,
            "title": instance.title,
            "description": instance.description,
            "status": instance.status,
            "priority": instance.priority,
            "assignee": assignee_data,
            "reviewer": reviewer_data,
            "due_date": str(instance.due_date) if instance.due_date else None,
        }

    def update(self, request, *args, **kwargs):
        """Update a ticket and return only spec-required fields."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(self._ticket_response(instance))

    def perform_create(self, serializer):
        """Set the current user as ticket creator."""
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['get', 'post'])
    def comments(self, request, pk=None):
        """Route to list or create comments for a ticket."""
        ticket = self.get_object()
        if request.method == 'GET':
            return self.list_comments(ticket)
        return self.create_comment(request, ticket)

    def list_comments(self, ticket):
        """Return all comments for a ticket."""
        comments = ticket.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def create_comment(self, request, ticket):
        """Create a new comment for a ticket."""
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(ticket=ticket, author=request.user)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete_comment(self, request, ticket_id=None, comment_id=None):
        """Delete a specific comment of a ticket."""
        try:
            ticket = Ticket.objects.get(pk=ticket_id)
            comment = ticket.comments.get(pk=comment_id)
        except (Ticket.DoesNotExist, Comment.DoesNotExist):
            return Response(
                {"detail": "Not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        board = ticket.board
        if board.owner != request.user and request.user not in board.members.all():
            return Response(
                {"detail": "You must be a member of the board."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if comment.author != request.user:
            return Response(
                {"detail": "You can only delete your own comments."},
                status=status.HTTP_403_FORBIDDEN,
            )

        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubticketViewSet(viewsets.ModelViewSet):
    """CRUD for subtickets."""
    queryset = Subticket.objects.all()
    serializer_class = SubticketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return subtickets for accessible tickets."""
        user = self.request.user
        owned_boards = Board.objects.filter(owner=user)
        member_boards = Board.objects.filter(members=user)
        all_boards = owned_boards | member_boards
        return Subticket.objects.filter(ticket__board__in=all_boards)


class AssignedToMeView(APIView):
    """Return tickets assigned to the current user as assignee."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return tickets where the user is the assignee."""
        user = request.user
        owned_boards = Board.objects.filter(owner=user)
        member_boards = Board.objects.filter(members=user)
        all_boards = owned_boards | member_boards
        tickets = Ticket.objects.filter(
            board__in=all_boards,
            assignee=user,
        )
        serializer = TicketSerializer(tickets, many=True)
        return Response(serializer.data)


class ReviewingTasksView(APIView):
    """Return tickets where the current user is the reviewer."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return tickets where the user is assigned as reviewer."""
        user = request.user
        owned_boards = Board.objects.filter(owner=user)
        member_boards = Board.objects.filter(members=user)
        all_boards = owned_boards | member_boards
        tickets = Ticket.objects.filter(
            board__in=all_boards,
            reviewer=user,
        )
        serializer = TicketSerializer(tickets, many=True)
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    """CRUD for comments."""
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        """Return comments from tickets on accessible boards."""
        user = self.request.user
        owned_boards = Board.objects.filter(owner=user)
        member_boards = Board.objects.filter(members=user)
        all_boards = owned_boards | member_boards
        user_tickets = Ticket.objects.filter(board__in=all_boards)
        return Comment.objects.filter(ticket__in=user_tickets)

    def create(self, request, *args, **kwargs):
        """Validate that ticket is provided for standalone comment creation."""
        if 'ticket' not in request.data:
            return Response(
                {"ticket": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        """Set the current user as comment author."""
        serializer.save(author=self.request.user)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only list of users."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
