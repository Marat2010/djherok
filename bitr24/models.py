from django.db import models
# from django.urls import reverse
from django.shortcuts import reverse
from django.utils.text import slugify
from time import time
from django.utils import timezone


def gen_slug(s):
    new_slug = slugify(s, allow_unicode=True)
    return new_slug + '-' + str(int(time()))


class Chat(models.Model):
    chat_id = models.IntegerField(default=0, verbose_name='Чат ID', unique=True)
    first_name = models.CharField(max_length=100, verbose_name='Имя', db_index=True)
    last_name = models.CharField(max_length=100, verbose_name='Фамилия', db_index=True)
    slug = models.SlugField(max_length=100, blank=True, unique=True, verbose_name='Слаг(Slug)')
    username = models.CharField(max_length=100, null=True, blank=True, verbose_name='Username')
    lang_code = models.CharField(max_length=2, verbose_name='Язык')
    bitrs = models.ManyToManyField('Bitr', blank=True, related_name='chats', verbose_name='Имя в Битрикс24')
    date_chat = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата подкл.к боту')

    def get_bitrs(self):
        return ', '.join(['{}-{}'.format(str(bi.bx24_id), bi.bx24_name) for bi in self.bitrs.all()])

    def __unicode__(self):
        return "{0}".format(self.first_name)

    def get_absolute_url(self):
        return reverse('chat_detail_url', kwargs={'slug': self.slug})

    def get_update_url(self):
        return reverse('chat_update_url', kwargs={'slug': self.slug})

    def get_delete_url(self):
        return reverse('chat_delete_url', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        # if not self.id:
        if not self.id or not self.slug:
            self.slug = gen_slug(self.first_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return '{}, {}'.format(self.chat_id, self.first_name)

    class Meta:
        verbose_name_plural = 'Чаты телеграм бота'
        verbose_name = 'Чат'
        # ordering = ['chat_id']
        ordering = ['-date_chat']


class Bitr(models.Model):
    bx24_id = models.IntegerField(default=0, verbose_name='ID поль. Б24', unique=True)
    bx24_name = models.CharField(default='', max_length=100, verbose_name='Имя в Б24', db_index=True)
    slug = models.SlugField(max_length=100, blank=True, unique=True, verbose_name='Слаг(Slug)')
    # expires = models.IntegerField(default=0, blank=True, null=True, verbose_name='Время acc токена', unique=True)
    # expires = models.IntegerField(default=0, blank=True, null=True, verbose_name='Время Acc токена')
    # expires = models.CharField(default='', max_length=30, blank=True, null=True, verbose_name='Время Acc токена',
    #                            db_index=True)
    expires = models.DateTimeField(blank=True, null=True, db_index=True, verbose_name='Время Acc токена')

    access_token = models.CharField(max_length=150, null=True, blank=True, verbose_name='Токен доступа Б24')
    refresh_token = models.CharField(max_length=150, null=True, blank=True, verbose_name='Токен обновления Б24')
    date_bx24 = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата подкл. к Б24')

    def get_chats(self):
        return ', \n'.join(['{}-{}'.format(str(ch.chat_id), ch.first_name) for ch in self.chats.all()])

    def get_absolute_url(self):
        return reverse('bitr_detail_url', kwargs={'slug': self.slug})

    def get_update_url(self):
        return reverse('bitr_update_url', kwargs={'slug': self.slug})

    def get_delete_url(self):
        return reverse('bitr_delete_url', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        # if not self.id:
        if not self.id or not self.slug:
            self.slug = gen_slug(self.bx24_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return '{:>3}:{}'.format(self.bx24_id, self.bx24_name)
        # return self.bx24_id

    class Meta:
        verbose_name_plural = 'Данные Б24'
        verbose_name = 'Данные Б24'
        ordering = ['-expires']


class Messages(models.Model):
    message = models.TextField(null=True, blank=True, verbose_name='Сообщение')
    date_msg = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата сообщения')
    chat = models.ForeignKey('Chat', on_delete=models.CASCADE, related_name='messages', verbose_name='Chat: ID, Имя')
    # bitrs = models.ManyToManyField('Bitr', blank=True, related_name='chats')

    def __str__(self):
        return self.message

    class Meta:
        verbose_name_plural = 'Сообщения'
        verbose_name = 'Сообщение'
        # ordering = ['pk']
        ordering = ['-date_msg']

    # class Bind(models.Model):
    #     chat_id = models.IntegerField(default=0, verbose_name='Чат ID', unique=True)
    #     bx24_id = models.IntegerField(default=0, verbose_name='ID поль. Б24', db_index=True)
    #     message = models.TextField(null=True, blank=True, verbose_name='Посл.сообщение')
    #     date_bind = models.DateTimeField(auto_now=True, db_index=True, verbose_name='Дата привязки')
    #
    #     def __str__(self):
    #         return 'Чат:{}, Б24:{}'.format(self.chat_id, self.bx24_id)
    #
    #     class Meta:
    #         verbose_name_plural = 'Привязки'
    #         verbose_name = 'Привязка'
    #         ordering = ['-date_bind']

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


