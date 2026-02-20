import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from kanban_app.models import Board, Ticket, Subticket, Comment
from django.utils import timezone

class Command(BaseCommand):
    help = 'Populates the database with dummy data for testing'

    def handle(self, *args, **kwargs):
        self.stdout.write('Deleting old data...')
        Comment.objects.all().delete()
        Subticket.objects.all().delete()
        Ticket.objects.all().delete()
        Board.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

        self.stdout.write('Creating dummy users...')
        users = []
        user_data = [
            ('marcel', 'marcel@example.com', 'Marcel', 'S.'),
            ('sofia', 'sofia@example.com', 'Sofia', 'A.'),
            ('lukas', 'lukas@example.com', 'Lukas', 'K.'),
            ('elena', 'elena@example.com', 'Elena', 'M.'),
        ]
        for username, email, first, last in user_data:
            user = User.objects.create_user(
                username=username,
                email=email,
                password='password123',
                first_name=first,
                last_name=last
            )
            users.append(user)

        self.stdout.write('Creating boards...')
        boards = []
        
        # Ensure every user owns at least one board
        for user in users:
            board = Board.objects.create(
                title=f"{user.first_name}'s Project",
                description=f"Personal project board for {user.get_full_name()}.",
                owner=user
            )
            # Add other users as members
            other_users = [u for u in users if u != user]
            members = random.sample(other_users, k=random.randint(1, len(other_users)))
            board.members.set(members)
            boards.append(board)

        # Add some extra collaborative boards
        extra_boards = [
            ('Company Roadmap', 'High-level planning for the whole team'),
            ('Team Building', 'Events and internal activities'),
        ]
        for title, desc in extra_boards:
            owner = random.choice(users)
            board = Board.objects.create(
                title=title,
                description=desc,
                owner=owner
            )
            board.members.set(users) # Everyone is a member
            boards.append(board)

        statuses = ['todo', 'in_progress', 'await_feedback', 'done']
        priorities = ['low', 'medium', 'urgent']

        self.stdout.write('Creating tickets and subtickets...')
        for board in boards:
            for i in range(random.randint(5, 8)):
                creator = random.choice(list(board.members.all()) + [board.owner])
                ticket = Ticket.objects.create(
                    board=board,
                    title=f'Sample Ticket {i+1} for {board.title}',
                    description=f'Full description for ticket {i+1}. This includes details about the implementation and requirements.',
                    status=random.choice(statuses),
                    priority=random.choice(priorities),
                    created_by=creator,
                    due_date=timezone.now() + timezone.timedelta(days=random.randint(1, 30))
                )
                
                # Assign users
                assignees = random.sample(list(board.members.all()) + [board.owner], k=random.randint(1, 2))
                ticket.assigned_to.set(assignees)

                # Create Subtickets
                for s in range(random.randint(2, 4)):
                    Subticket.objects.create(
                        ticket=ticket,
                        title=f'Subtask {s+1} for {ticket.title}',
                        done=random.choice([True, False])
                    )

                # Create Comments
                for c in range(random.randint(1, 3)):
                    author = random.choice(list(board.members.all()) + [board.owner])
                    Comment.objects.create(
                        ticket=ticket,
                        author=author,
                        text=f"This is a comment number {c+1} on ticket {ticket.id}. It provides some feedback."
                    )

        self.stdout.write(self.style.SUCCESS('Successfully populated the database with dummy data.'))
        self.stdout.write(self.style.SUCCESS('User passwords are all "password123"'))
