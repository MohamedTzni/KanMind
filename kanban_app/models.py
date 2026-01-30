from django.db import models
from django.contrib.auth.models import User


class Board(models.Model):
    """
    Represents a Kanban board that contains tasks.
    Each board has an owner and can have multiple members.
    """
    title = models.CharField(
        max_length=100,
        verbose_name="Board Title"
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owned_boards',
        verbose_name="Board Owner"
    )
    members = models.ManyToManyField(
        User,
        related_name='boards',
        blank=True,
        verbose_name="Board Members"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At"
    )

    class Meta:
        verbose_name = "Board"
        verbose_name_plural = "Boards"
        ordering = ['-created_at']

    def __str__(self):
        return self.title
    
class Task(models.Model):
    """
    Represents a task within a Kanban board.
    Tasks can be assigned to multiple users and have different statuses and priorities.
    """
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('reviewing', 'Reviewing'),
        ('done', 'Done'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name="Board"
    )
    title = models.CharField(
        max_length=200,
        verbose_name="Task Title"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='todo',
        verbose_name="Status"
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name="Priority"
    )
    assigned_to = models.ManyToManyField(
        User,
        related_name='assigned_tasks',
        blank=True,
        verbose_name="Assigned To"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_tasks',
        verbose_name="Created By"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At"
    )
    due_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Due Date"
    )

    class Meta:
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"