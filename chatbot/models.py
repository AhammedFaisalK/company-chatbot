from django.conf import settings
from django.db import models


class Conversation(models.Model):
    """
    Groups a sequence of messages together as one chat session.
    `user` is optional (nullable) so anonymous/testing chats work too.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="conversations",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Conversation #{self.pk}"

    class Meta:
        ordering = ["-updated_at"]


class Message(models.Model):
    """
    A single message in a conversation — either from the user or the bot.
    """
    class Role(models.TextChoices):
        USER = "user", "User"
        ASSISTANT = "assistant", "Assistant"
        SYSTEM = "system", "System"

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    role = models.CharField(max_length=10, choices=Role.choices)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        preview = self.content[:40]
        return f"[{self.role}] {preview}"

    class Meta:
        ordering = ["created_at"]