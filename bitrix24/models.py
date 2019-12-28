from django.db import models


class Messages(models.Model):
    message = models.TextField(null=True, blank=True, verbose_name='Сообщение')
    date_msg = models.DateTimeField(auto_now=True, db_index=True,
                                    verbose_name='Дата сообщения')

    def __str__(self):
        return self.message

    class Meta:
        verbose_name_plural = 'Сообщения'
        verbose_name = 'Сообщение'
        ordering = ['pk']


class Chats(models.Model):
    chat_id = models.IntegerField(default=1, verbose_name='Чат ID', unique=True)
    first_name = models.CharField(max_length=50, verbose_name='Имя пользователя')
    username = models.CharField(max_length=50, verbose_name='Пользователь')
    message = models.ForeignKey(Messages, null=True, on_delete=models.PROTECT, verbose_name='Сообщение')
    lang_code = models.CharField(max_length=2, verbose_name='Язык')

    class Meta:
        verbose_name_plural = 'Чаты'
        verbose_name = 'Чат'
        ordering = ['chat_id']


