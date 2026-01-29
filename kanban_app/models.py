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