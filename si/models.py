# from pytils.translit import slugify
from django.db import models
from django.utils.text import slugify
from time import time
from django.shortcuts import reverse


def gen_slug(s):
    new_slug = slugify(s, allow_unicode=True)
    return new_slug + '-' + str(int(time()))


class Planet(models.Model):
    name = models.CharField(max_length=50, db_index=True, verbose_name='Планета')
    slug = models.SlugField(max_length=100, blank=True, null=True, unique=True, verbose_name='Слаг(Slug)')

    def get_siths(self):
        return ';  '.join(['{}'.format(str(si.name)) for si in self.siths.all()])

    def get_recruits(self):
        return ';  '.join(['{}: {}'.format(str(recr.name), recr.email) for recr in self.recruits.all()])

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.id or not self.slug:
            self.slug = gen_slug(self.name)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Планеты'
        verbose_name = 'Планета'
        ordering = ['name']


class Order(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название ордена')
    code = models.SlugField(max_length=100, unique=True, verbose_name='Код ордена')

    def get_siths(self):
        return ';  '.join(['{} (планета: {})'.format(str(si.name), si.planet) for si in self.siths.all()])

    def __str__(self):
        return self.code

    class Meta:
        verbose_name_plural = 'Ордена'
        verbose_name = 'Орден'
        ordering = ['name']


class Sith(models.Model):
    name = models.CharField(max_length=50, verbose_name='Имя ситха')
    planet = models.ForeignKey(Planet, related_name='siths', on_delete=models.PROTECT, verbose_name='Планета')
    order = models.ForeignKey(Order, blank=True, null=True, related_name='siths', on_delete=models.PROTECT, verbose_name='Код ордена')
    slug = models.SlugField(max_length=100, blank=True, null=True, unique=True, verbose_name='Слаг(Slug)')

    def get_recruits(self):
        return ';  '.join(['{} ({})'.format(str(recr.name), recr.email) for recr in self.recruits.all()])

    def get_count_hands(self):   # siths_count_hands
        return len(self.recruits.all())
        # return self.recruits.all().count()

    def get_absolute_url(self):
        return reverse('sith_detail_url', kwargs={'slug': self.slug})

    def get_update_url(self):
        return reverse('sith_update_url', kwargs={'slug': self.slug})

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.id or not self.slug:
            self.slug = gen_slug(self.name)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Ситхи'
        verbose_name = 'Ситх'
        ordering = ['name']


class Recruit(models.Model):
    name = models.CharField(max_length=50, verbose_name='Имя рекрута')
    planet = models.ForeignKey(Planet, related_name='recruits', on_delete=models.PROTECT, verbose_name='Планета')
    age = models.IntegerField(default=1, verbose_name='Возраст')
    email = models.EmailField(max_length=50, unique=True, verbose_name='Емаил')
    slug = models.SlugField(max_length=100, blank=True, null=True, unique=True, verbose_name='Слаг(Slug)')
    answers = models.CharField(max_length=200, blank=True, null=True, verbose_name='Ответы')
    sith = models.ForeignKey(Sith, blank=True, null=True, related_name='recruits', on_delete=models.PROTECT,
                             verbose_name='Рука Тени')

    def get_sith(self):
        return '{} (планета: {})'.format(self.sith.name, self.sith.planet) if self.sith else ' -'

    def get_absolute_url(self):
        return reverse('recruit_detail_url', kwargs={'slug': self.slug})

    def get_update_url(self):
        return reverse('recruit_update_url', kwargs={'slug': self.slug})

    def get_questions_url(self):
        return reverse('recruit_questions_url', kwargs={'slug': self.slug})

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.id or not self.slug:
            self.slug = gen_slug(self.name)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Рекруты'
        verbose_name = 'Рекрут'
        ordering = ['name']


class Test(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT, verbose_name='Код ордена')
    question = models.TextField(blank=True, null=True, verbose_name='Вопрос')
    slug = models.SlugField(max_length=100, blank=True, null=True, unique=True, verbose_name='Слаг(Slug)')

    def get_answers(self):
        # return ';  '.join(['{} ({})'.format(str(recr.name), recr.email) for recr in self.recruits.all()])
        return ';  '.join(['{} '.format(str(answ.answer)) for answ in self.answers.all()])

    def __str__(self):
        return self.question

    def save(self, *args, **kwargs):
        if not self.id or not self.slug:
            self.slug = gen_slug(self.order)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Тесты'
        verbose_name = 'Тест'
        ordering = ['order']


class Answer(models.Model):
    answer = models.CharField(max_length=100, blank=True, null=True, verbose_name='Ответ', unique=True)
    tests = models.ManyToManyField('Test', blank=True, related_name='answers', verbose_name='Вопрос')

    def __str__(self):
        return self.answer

    class Meta:
        verbose_name_plural = 'Ответы'
        verbose_name = 'Ответ'
        ordering = ['id']






