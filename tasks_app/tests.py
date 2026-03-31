from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from boards_app.models import Board
from tasks_app.models import Ticket


class TaskEndpointDocumentationTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username='owner@example.com',
            email='owner@example.com',
            password='testpass123',
            first_name='Owner',
            last_name='User',
        )
        self.member = User.objects.create_user(
            username='member@example.com',
            email='member@example.com',
            password='testpass123',
            first_name='Member',
            last_name='User',
        )
        self.reviewer = User.objects.create_user(
            username='reviewer@example.com',
            email='reviewer@example.com',
            password='testpass123',
            first_name='Reviewer',
            last_name='User',
        )
        self.other_owner = User.objects.create_user(
            username='other@example.com',
            email='other@example.com',
            password='testpass123',
            first_name='Other',
            last_name='Owner',
        )

        self.board = Board.objects.create(title='Main Board', owner=self.owner)
        self.board.members.add(self.member, self.reviewer)
        self.other_board = Board.objects.create(title='Other Board', owner=self.other_owner)

        self.client.force_authenticate(user=self.member)

    def test_assigned_to_me_only_returns_tasks_where_user_is_assignee(self):
        assigned_ticket = Ticket.objects.create(
            board=self.board,
            title='Assigned ticket',
            status='to-do',
            priority='medium',
            assignee=self.member,
            reviewer=self.reviewer,
            created_by=self.owner,
        )
        Ticket.objects.create(
            board=self.board,
            title='Reviewer only ticket',
            status='review',
            priority='high',
            reviewer=self.member,
            created_by=self.owner,
        )

        response = self.client.get('/api/tasks/assigned-to-me/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], assigned_ticket.id)

    def test_patch_task_rejects_board_changes_with_bad_request(self):
        ticket = Ticket.objects.create(
            board=self.board,
            title='Existing task',
            status='to-do',
            priority='medium',
            assignee=self.member,
            created_by=self.owner,
        )

        response = self.client.patch(
            f'/api/tasks/{ticket.id}/',
            {'board': self.other_board.id},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        ticket.refresh_from_db()
        self.assertEqual(ticket.board_id, self.board.id)

    def test_task_creator_can_delete_task_even_if_removed_from_board_members(self):
        former_member = User.objects.create_user(
            username='former@example.com',
            email='former@example.com',
            password='testpass123',
            first_name='Former',
            last_name='Member',
        )
        self.board.members.add(former_member)
        ticket = Ticket.objects.create(
            board=self.board,
            title='Creator task',
            status='to-do',
            priority='medium',
            created_by=former_member,
        )
        self.board.members.remove(former_member)

        self.client.force_authenticate(user=former_member)
        response = self.client.delete(f'/api/tasks/{ticket.id}/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Ticket.objects.filter(id=ticket.id).exists())
