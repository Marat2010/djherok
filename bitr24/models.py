from django.db import models
# from django.urls import reverse
from django.shortcuts import reverse


class Chat(models.Model):
    chat_id = models.IntegerField(default=1, verbose_name='Чат ID', unique=True)
    first_name = models.CharField(max_length=100, verbose_name='Имя пользователя', db_index=True)
    slug = models.SlugField(max_length=100, unique=True, verbose_name='Slug')
    username = models.CharField(max_length=100, null=True, blank=True, verbose_name='Пользователь')
    lang_code = models.CharField(max_length=2, verbose_name='Язык')
    bitrs = models.ManyToManyField('Bitr', blank=True, related_name='chats')

    def get_absolute_url(self):
        return reverse('chat_detail_url', kwargs={'slug': self.slug})

    def __str__(self):
        return '{}, {}'.format(self.chat_id, self.first_name)

    class Meta:
        verbose_name_plural = 'Чаты телеграм бота'
        verbose_name = 'Чат'
        ordering = ['chat_id']


class Bitr(models.Model):
    bx24_id = models.IntegerField(default=0, verbose_name='ID пользователя Б24', unique=True)
    bx24_name = models.CharField(default='', max_length=100, verbose_name='Имя в Битрикс24', db_index=True)
    slug = models.SlugField(max_length=100, unique=True, verbose_name='Slug')
    access_token = models.CharField(max_length=150, null=True, blank=True, verbose_name='Токен доступа Б24')
    refresh_token = models.CharField(max_length=150, null=True, blank=True, verbose_name='Токен обновления Б24')

    def get_absolute_url(self):
        return reverse('bitr_detail_url', kwargs={'slug': self.slug})

    def __str__(self):
        return '{}'.format(self.bx24_id)

    class Meta:
        verbose_name_plural = 'Данные Б24'
        verbose_name = 'Данные Б24'
        ordering = ['bx24_id']


class Messages(models.Model):
    message = models.TextField(null=True, blank=True, verbose_name='Сообщение')
    date_msg = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата сообщения')
    # chatM = models.ForeignKey(Chats, on_delete=models.CASCADE, verbose_name='Чат ID, Пользователь')

    def __str__(self):
        return self.message

    class Meta:
        verbose_name_plural = 'Сообщения'
        verbose_name = 'Сообщение'
        ordering = ['pk']


    # chatB = models.ForeignKey(Chats, on_delete=models.CASCADE, verbose_name='Чат ID, Пользователь')
    # chats = models.ManyToManyField('Chats', blank=True, related_name='bitrs')
# def upload_tbx_images_folder(instance, filename):
#     filename = instance.slug + '.' + filename.split('.')[-1]    #.png .ipg
#     return "{}/{}".format(instance.slug, filename)


# class Tbx(models.Model):
#     messages = models.ForeignKey(Messages, on_delete=models.PROTECT, verbose_name='Сообщение')
#     chat_id = models.IntegerField(default=1, verbose_name='Чат ID', unique=True)
#     # chat_id = models.ForeignKey(Chats, on_delete=models.CASCADE, verbose_name='Чат ID')
#     first_name = models.CharField(max_length=50, verbose_name='Имя пользователя')
#     slug = models.SlugField(unique=True)
#     image = models.ImageField(upload_to=upload_tbx_images_folder)
#     username = models.CharField(max_length=50, null=True, blank=True, verbose_name='Пользователь')
#     lang_code = models.CharField(max_length=2, verbose_name='Язык')
#     bx24_id = models.IntegerField(default=0, verbose_name='ID пользователя Б24', unique=True)
#
#     def __str__(self):
#         return "Пользователь {} и его сообщения: {}".format(self.first_name, self.messages.message)
#
#     def get_absolute_url(self):
#         return reverse('tbx_detail', kwargs={'tbx_slug': self.slug})


