from django.db import models


class Planets(models.Model):
    name = models.CharField(max_length=50, db_index=True, verbose_name='Планета')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Планеты'
        verbose_name = 'Планета'
        ordering = ['name']


class Recruits(models.Model):
    name = models.CharField(max_length=50, verbose_name='Имя рекрута')
    planet = models.ForeignKey(Planets, null=True, on_delete=models.PROTECT, verbose_name='Планета')
    age = models.IntegerField(default=1, verbose_name='Возраст')
    email = models.EmailField(max_length=50, unique=True, verbose_name='Емаил')

    class Meta:
        verbose_name_plural = 'Рекруты'
        verbose_name = 'Рекрут'
        ordering = ['name']


class Sith(models.Model):
    name = models.CharField(max_length=50, verbose_name='Имя ситха')
    planet = models.ForeignKey(Planets, on_delete=models.PROTECT, verbose_name='Планета')

    class Meta:
        verbose_name_plural = 'Ситхи'
        verbose_name = 'Ситх'
        ordering = ['name']


class Tests(models.Model):
    order_code = models.IntegerField(unique=True, verbose_name='Код ордена')
    list_questions = models.CharField(max_length=200, verbose_name='Список вопросов')

    class Meta:
        verbose_name_plural = 'Тесты'
        verbose_name = 'Тест'
        ordering = ['order_code']

