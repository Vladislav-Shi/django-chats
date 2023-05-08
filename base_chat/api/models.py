from django.conf import settings
from django.db import models


class ChatRoom(models.Model):
    """
    Модель существующих чатов
    """
    name = models.CharField(max_length=40, unique=True)
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='autor'
    )
    create_at = models.DateTimeField(auto_now_add=True)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, )

    def _get_count_users(self):
        """Возвращает кол-во пользователей"""
        return self.users.all().count()

    chat_size = property(_get_count_users)

    class Meta:
        ordering = ['create_at']


class ChatMessage(models.Model):
    text = models.CharField(max_length=256)
    chat = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    is_event = models.BooleanField(verbose_name='техническое сообщение', default=0)
    create_at = models.DateTimeField(auto_now_add=True)
