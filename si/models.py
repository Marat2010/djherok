# from pytils.translit import slugify
from django.db import models
from django.utils.text import slugify
from time import time
from django.shortcuts import reverse
from django.core.exceptions import ValidationError
from django.dispatch import receiver
import random


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
    slug = models.SlugField(max_length=100, blank=True, null=True, unique=True, verbose_name='Слаг(Slug)')

    def get_siths(self):
        return ';  '.join(['{} (планета: {})'.format(str(si.name), si.planet) for si in self.siths.all()])

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        if not self.id or not self.slug:
            self.slug = gen_slug(self.name)
        super().save(*args, **kwargs)

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

    def get_planet_url(self):
        return reverse('siths_planet_url', kwargs={'slug': self.planet.slug})

    def get_order_url(self):
        return reverse('siths_order_url', kwargs={'slug': self.order.slug})

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
    sith = models.ForeignKey(Sith, blank=True, null=True, related_name='recruits', on_delete=models.PROTECT,
                             verbose_name='Рука Тени')

    def get_sith(self):
        return '{} (планета: {})'.format(self.sith.name, self.sith.planet) if self.sith else ' -'

    def get_planet_url(self):
        return reverse('recruits_planet_url', kwargs={'slug': self.planet.slug})

    def get_order_url(self):
        if self.sith:
            return reverse('recruits_order_url', kwargs={'slug': self.sith.order.slug})
        return reverse('recruits_order_url', kwargs={'slug': 'None'})
        # return reverse('recruits_list_url')

    def get_absolute_url(self):
        return reverse('recruit_detail_url', kwargs={'slug': self.slug})

    def get_update_url(self):
        return reverse('recruit_update_url', kwargs={'slug': self.slug})

    def get_questions_url(self):
        return reverse('recruit_questions_url', kwargs={'slug': self.slug})

    def refresh_question(self):  # Возвращает queryset вопросов RecruitAnswer (без ответов - новый)
        # number_questions = 3    # Кол-во вопросов для рекрута, можно сформировать случайное в диапазоне, например так:
        number_questions = random.randint(2, 5)
        old_questions = RecruitAnswer.objects.filter(recruit=self)
        old_questions.delete()
        # questions = random.sample(list(Test.objects.all()), 1)[0]
        questions = random.sample(list(Test.objects.all()), number_questions)
        for question in questions:
            RecruitAnswer.objects.create(question=question, recruit=self)
        return RecruitAnswer.objects.filter(recruit=self)

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


class Answer(models.Model):
    answer = models.CharField(max_length=100, blank=True, null=True, verbose_name='Ответ', unique=True)
    # tests = models.ManyToManyField('Test', blank=True, related_name='answers', verbose_name='Вопрос')

    def __str__(self):
        return self.answer

    class Meta:
        verbose_name_plural = 'Ответы'
        verbose_name = 'Ответ'
        ordering = ['id']


class Test(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT, verbose_name='Код ордена')
    question = models.TextField(blank=True, null=True, verbose_name='Вопрос')
    slug = models.SlugField(max_length=100, blank=True, null=True, unique=True, verbose_name='Слаг(Slug)')
    right_answ = models.ForeignKey(Answer, blank=True, null=True, on_delete=models.PROTECT, related_name='right_answ',
                                   verbose_name='Правильный ответ')
    answers = models.ManyToManyField(Answer, blank=True, related_name='tests', verbose_name='Ответ')

    def get_absolute_url(self):
        return reverse('recruit_detail_url', kwargs={'pk': self.pk})

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
        ordering = ['-pk']


class RecruitAnswer(models.Model):
    recruit = models.ForeignKey(Recruit, related_name='recruitanswers', on_delete=models.CASCADE, verbose_name='Рекрут')
    question = models.ForeignKey(Test, related_name='recruitanswers', on_delete=models.PROTECT, verbose_name='Вопрос')
    answer = models.ForeignKey(Answer, related_name='recruitanswers', on_delete=models.PROTECT, verbose_name='Ответ',
                               blank=True, null=True)

    # def _get_answer_display(self, answer):
    # def _get_answer(self):
        # answer = self.question.answers.all()
    # def __getattr__(self, name):
    #     if name == 'answer':
    #         answer = self.question.answers
    #         print('____GETATTR', answer)
    #         return answer
    #     return super(RecruitAnswer, self).__getattribute__(name)
    #     # return super(RecruitAnswer, self).__getattr__(name)

    # answer = property(_get_answer)
    @classmethod  # Возвращает queryset вопросов RecruitAnswer (без ответов - новый), перенесен в модель Recruit.
    def refresh_question(cls, recruit):  # надо чтобы возвращал queryset
        number_questions = 2

        old_questions = cls.objects.filter(recruit=recruit)
        old_questions.delete()
        # questions = random.sample(list(Test.objects.all()), 1)[0]
        questions = random.sample(list(Test.objects.all()), number_questions)
        for question in questions:
            cls.objects.create(question=question, recruit=recruit)
        recruitanswer = cls.objects.filter(recruit=recruit)

        return recruitanswer
        # return reverse('recruits_order_url', kwargs={'slug': 'None'})
        # return reverse('recruits_list_url')

    def __str__(self):
        return '{}: {}'.format(self.recruit, self.question)

    class Meta:
        verbose_name_plural = 'Ответы Рекрутов'
        verbose_name = 'Ответы Рекрута'
        ordering = ['recruit']


# ----------------
    # def get_questions(self):
    #     # recruit = get_object_or_404(Recruit, slug__iexact=slug)
    #     # question = random.sample(list(Test.objects.all()), 1)[0].question
    #     # # question = random.sample(list(Test.objects.all()), 2)
    #     # print('====question: ', question)
    #     pass

# ---------------
        # recruit = models.ForeignKey(Recruit, related_name='recruitanswers', on_delete=models.PROTECT, verbose_name='Рекрут')

        # else:
            # new_test = Answer.objects.update_or_create(self)
            # new_test = super(Test, self).save(*args, **kwargs)

            # super(Test, self).save(*args, **kwargs)
            # right_answ = self.right_answ

            # self.right_answ.save()
            # ans = self.answers.all()
            # Answer.objects.update_or_create(self)
            # self.answers.update_or_create()
            # yes_no = right_answ.save() in list(self.answers.all())
            # self.right_answ
            # ans = Answer.objects.update_or_create(answer=new_test)
            # self.answers.set()
            # self.answers.update()
            # print('----new-test: ', type(new_test))
            # Использовать "m2m_changed" или "TabularInline"
            # print('----кшпре-test: ', self.right_answ, self.answers.all())
    # answers = models.CharField(max_length=200, blank=True, null=True, verbose_name='Ответы')

    # @receiver
    # def pre_save(self, instance, **kwargs):
    #     # instance.answers.update = instance.period_duration()
    #     instance.answers.update()

    # def create(self, *args, **kwargs):
    #     if
    #     validated_data['slug'] = slugify(validated_data['name'])
    #     return budgets.models.BudgetCategory.objects.create(**validated_data)

    # self.answers = Answer.objects.none()
    # self.answers = ''
    # if not commit:
    #     raise NotImplementedError("Can't create User and Userextended without database save")

    # right = models.ForeignObject(answers)
    # right_answ = models.ForeignKey(Answer, blank=True, related_name='tests_right', on_delete=models.PROTECT, verbose_name='Правильный ответ')

