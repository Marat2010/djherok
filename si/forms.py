from django.forms import ModelForm
from django import forms
import random
from django.forms import formset_factory
from django.core.exceptions import ValidationError
from .models import Recruit, Sith, Planet, Test, Answer, RecruitAnswer
# from dal import autocomplete


class RecruitForm(forms.ModelForm):
    class Meta:
        model = Recruit
        fields = ['name', 'planet', 'age', 'email']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'planet': forms.Select(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    # autocomplete_fields = ('planet', )

    def clean_email(self):
        new_email = self.cleaned_data['email']
        if Recruit.objects.filter(email=new_email) and not self.instance.slug:  # Если новый и не Update, тогда отказ.
            raise ValidationError('Е-маил: "{}", уже используется'.format(new_email))
        return new_email


class TestForm(forms.ModelForm):  # Для выбора прав.ответа из сущестующих в 'admin'
    class Meta:
        model = Test
        fields = ['right_answ', 'question', 'answers', 'order']
        widgets = {'question': forms.Textarea(attrs={"rows": 5, "class": "vLargeTextField"})}
        labels = {'answers': 'Ответы'}

    # right_answ = forms.ModelChoiceField(queryset=Answer.objects.all(),
    #                                     # empty_label='Выберите',
    #                                     empty_label=None,
    #                                     # initial=Answer.objects.get(pk=1),
    #                                     to_field_name='answer',
    #                                     label='Правильный ответ'
    #                                     )

    def clean(self):
        if self.cleaned_data["right_answ"] not in self.cleaned_data["answers"]:
            raise forms.ValidationError('Правильный ответ должен быть одним из в "Ответах"!')
        super(TestForm, self).clean()  # ? important- let admin do its work on data!
        print('--self.cleaned_data: ', self.cleaned_data)
        return self.cleaned_data


class SithForm(forms.ModelForm):
    class Meta:
        model = Sith
        fields = ['name', 'planet', 'order']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'planet': forms.Select(attrs={'class': 'form-control'}),
            'order': forms.Select(attrs={'class': 'form-control'}),
        }


class RecruitQuestionsForm(forms.ModelForm):
    class Meta:
        model = RecruitAnswer
        fields = ['answer']
        widgets = {'answer': forms.RadioSelect()}

        # labels = {'answer': ' '}    # Первый способ используем 'label_suffix' для самого
        # вопроса из View (Как альтернатива)
        # Второй (правильный) способ использователь переопределение "label" здесь:

    def __init__(self, *args, **kwargs):
        super(RecruitQuestionsForm, self).__init__(*args, **kwargs)
        self.fields['answer'].label = self.instance.question  # change required label ... and answers
        self.fields['answer'].queryset = Test.objects.get(question=self.instance.question).answers.all()
        self.fields['answer'].empty_label = None


class RecruitQuestionsForm2(forms.Form):
    # pass
    questions = random.sample(list(Test.objects.all()), 3)
    # print('---question:   ', questions)

    for question in questions:
        queryset = question.answers.all()
        label = question.question
        # answers = forms.ModelChoiceField(queryset=queryset, label=label, empty_label=)


class ChoiceRadioSelect(forms.RadioSelect):
    def __init__(self, *args, **kwargs):
        choices = ((True, 'Да'), (False, 'Нет'), (3, 'ответ 3'), (3, 'ответ 4'))
        # choices = ((True, 'Да'), (False, 'Нет'))
        super(ChoiceRadioSelect, self).__init__(choices=choices, *args, **kwargs)
    _empty_value = None



# -------------------------------
# -------------------------------
# ------------------------------
# print('---Form Instans1: {} \t =={} '.format(self.instance.question, self.instance.answer))
# answer = forms.ModelChoiceField(queryset=queryset, empty_label='выберите')
# ----------------------------------------
# # -----------------------------------------------------
# class RecruitQuestionsForm_one(forms.ModelForm):  # Для одного вопроса без formset-а
#     class Meta:
#         model = RecruitAnswer
#         fields = ['answer']
#         # labels = {'answer': ' '}    # Используем 'label_suffix' для самого вопроса из View
#
#     # Второй способ использователь переопределение "label" здесь:
#     def __init__(self, *args, **kwargs):
#         super(RecruitQuestionsForm_one, self).__init__(*args, **kwargs)
#         self.fields['answer'].label = self.instance.question  # change required label ... and answers
#         self.fields['answer'].queryset = Test.objects.get(question=self.instance.question).answers.all()
#         print('---Form Instans: {} \t =={} '.format(self.instance.question, self.instance.answer))
# # -----------------------------------------------------


# class RecruitQuestionsForm11(forms.ModelForm):
#     pass
    # class Meta:
    #     model = Test
    #     # model = Answer
    #     fields = ['answers']
    #
    # widgets = {
    # #     'answer': forms.TextInput(attrs={'class': 'form-control'}),
    # #     'answers': forms.Select(attrs={'class': 'form-control', 'label': ' '}),
    # #     # 'answer': forms.TextInput(attrs={'class': 'form-control'}),
    # }
    #
    # # queryset = Answer.objects.all()
    # queryset = Test.objects.get(pk=1).answers
    #
    # # answer = forms.ModelChoiceField(queryset=queryset, widget=ChoiceRadioSelect, label=' ')
    #
    # # answers = forms.ModelChoiceField(queryset=queryset, widget=forms.RadioSelect, label=' ')
    # answers = forms.ModelChoiceField(queryset=queryset, label=' ')
    # # answers = forms.RadioSelect()
    #
    #
    # # answer = forms.ModelChoiceField(queryset=queryset, widget=ChoiceRadioSelect, label=' ')
    # # answer = forms.ModelChoiceField(widget=ChoiceRadioSelect, label=' ')
    #
    # # answer = forms.ModelChoiceField(queryset=queryset, label='')
    # # answer = forms.ModelChoiceField(widget=ChoiceRadioSelect, label='')
    #
    #
    #
    # # def clean_q(self):
    # #     new_q = self.cleaned_data['q']
    # #     print('===new_q: ', new_q)
    # #     if new_q is None:
    # #         raise ValidationError('Поле: {}, надо заполнить'.format(new_q))
    # #     return new_q
    #
    # # def save(self):
    # #     self.clean()
    # #     new_obj = {'quest': self.label_suffix, 'answ': self.cleaned_data}
    # #     return new_obj



# ----------------------------------------
# class NullBooleanRadioSelect(forms.RadioSelect):
# -----------------------------------------------------


# ---------------------------------------------------
# -----------------------------------------------------
    # # questions = random.sample(list(Test.objects.all()), 1)[0]
    # questions = RecruitAnswer.objects.get(question=s)
    #
    #
    # answer = forms.ModelChoiceField(queryset=Answer.objects.filter(tests=questions), label=questions)
    # print('dsdfd---------', answer, Answer.objects.filter(tests=questions))
# ---------------------------------------------------
# print('------Instans ', self.instance.question)
# print('------answLABEL ', self.fields['answer'].__dict__)
# ------Instans  Кайло Рен тренировался как джедай у своего дяди Люка Скайуокера?
# ------answLABEL  {'empty_label': '---------', 'required': False,
#  'label': <Test: Кайло Рен тренировался как джедай у своего дяди Люка Скайуокера?>,
#  'initial': None, 'show_hidden_initial': False, 'help_text': '', 'disabled': False,
#  'label_suffix': None, 'localize': False,
#  'widget': <django.forms.widgets.Select object at 0x7ff861bd5390>,
#  'error_messages': {'required': 'Обязательное поле.',
#  'invalid_choice': 'Выберите корректный вариант. Вашего варианта нет среди допустимых значений.'},
#  'validators': [], '_queryset': <QuerySet [<Answer: Да>, <Answer: Нет>, <Answer: Робот-дровосек>, <Answer: Хорошие парни>, <Answer: Камино>, <Answer: Альдераан>, <Answer: Мемит Надилл>, <Answer: Аэроспидер>, <Answer: Не знаю>]>, 'limit_choices_to': {}, 'to_field_name': 'id'}
# ==instance: Recr: Andrey, Quest: Кайло Рен тренировался как джедай у своего дяди Люка Скайуокера? - Answ: None
# -----------------------------------------------------
# if self.instance:
#     if self.instance.answer:
#     # if self.instance.answer == 'value':
#         # del self.fields['my_field']  # remove 'my_field'
        # fields = ['answer', 'question']
        # labels = {'answer': ''}

        # widgets = {'question': HiddenInput()}
        # question = forms.widgets.HiddenInput()
        # question = forms.widgets.MultipleHiddenInput()
    # label = 'fdfdfdf==========='
        # widgets = forms.ModelChoiceField(**kwargs)

# ------------------
    # labels = {'answer': questions.question}
        # labels = {'answer': question}
    # label = 'zzzzzzzz'
        # fields = ['answer']
        # labels = 'question'
    # print('== quest: ', self.instance.question)
    #     print('== quest: ', question)

    # def __init__(self, *args, **kwargs):
    #     print('=======KWARG', kwargs)
    #     labels = kwargs['question']
    #     super(RecruitQuestionsForm, self).__init__(*args, **kwargs)
    #     self.label_suffix = labels

# ------------------------------------------------------
    # question = forms.CharField(label='fdfdf', widget=forms.Textarea(attrs={"rows": 5, "class": "vLargeTextField"}))

    # question.labels = 'sdfd'
    # question = forms.CharField(widget=forms.Textarea(attrs={"rows": 5, "cols": 50,
    # "class": "vLargeTextField"}))

    # def clean_answers(self):
    #     print('--claen:::: ', self.cleaned_data)
    #     if self.cleaned_data["right_answ"] not in self.cleaned_data["answers"]:
    #         # raise forms.ValidationError('Выберите правильный ответ из предоставленных ответов!!!')
    #         raise forms.ValidationError('Правильный ответ должен быть одним из в ответах!')
    #     super(FormTest, self).clean()  # important- let admin do its work on data!
    #     print('--slef', self.cleaned_data)
    #     return self.cleaned_data

    # def clean_right_answ(self):
# ------------------------------------------------------
# class MyTestAdminForm(forms.ModelForm):
#     def clean_right_answ(self):
#         # do something that validates your data
#         # object_id = request.resolver_match.kwargs['object_id']
#         if self.right_answ not in self.answers.all():
#             raise ValidationError('Выберите правильный ответ из предоставленных ответов!!!')
#         return self.cleaned_data["right_answ"]

# class RecruitForm2(forms.ModelForm):
#     class Meta:
#         model = Recruit
#         fields = ['name', 'planet', 'age', 'email']

# -------------
# class QuestionForm_2(forms.ModelForm):
#     class Meta:
#         # model = Answer
#         model = Test
#         fields = ['answer']
#
#     queryset = Answer.objects.all()
#     # queryset = answer.all()
#     # answer = forms.ModelChoiceField(queryset=queryset, widget=ChoiceRadioSelect, label=' ')
#     answer = forms.NullBooleanField(widget=ChoiceRadioSelect, label=' ')
#
# class RecruitQuestionsForm(forms.Form):
#     # q = forms.NullBooleanField(widget=NullBooleanRadioSelect)
#     def __init__(self, label, *args, **kwargs):
#         global qq
#         super(RecruitQuestionsForm, self).__init__(*args, **kwargs)
#         self.fields['q'] = forms.NullBooleanField(widget=ChoiceRadioSelect, label=label)
#         # self.fields['q'] = forms.NullBooleanField(widget=NullBooleanRadioSelect)
#         # self.label_suffix = label
#         # self.fields['q'].label = label
#         # print('===== self.label_sufix:', self.label)
#         print('===1== self.label_sufix:', self.fields['q'].label)
#
#     def save(self):
#         # q_a = self.cleaned_data['q']
#         q_a = self.data
#         print('=====3=== Save:', q_a, '===qq ')
# #         new_recruit = Recruit.objects.create(
# #             name=self.cleaned_data['name'],
# #         )
#         return q_a
#
#
#     # def __init__(self, documents, *args, **kwargs):
#     #     row = [(row.id, row.first_name + ' ' + row.first_name) for row in documents]
#     #     super(RecruitQuestionsForm, self).__init__(*args, **kwargs)
#     #     self.fields['friends'] = forms.MultipleChoiceField(choices=row)
#     #     self.fields['msg'] = forms.CharField(min_length=10, widget=forms.Textarea(
#     #         attrs={'width': "100%", 'cols': "70", 'rows': "20", }),
#     #                                          label="Ваше сообщение")
#
#     # q.label_suffix = ' 22dsdsd'
#
#     # print('==q.label: ', q.label, '\n==q.label_suffix :', q.label_suffix)

# -------------
# class QuestionForm_2(forms.Form):
#     choices = [(1, 'Да'), (2, 'Нет'), (3, 'ответ 3'), (3, 'ответ 4')]
#     # widgets = {'rate': forms.RadioSelect(attrs={'name': 'rating'}, choices=choices)}
#     # q = forms.RadioSelect(widget=ChoiceRadioSelect, choices=choices)
#     # q.widget.attrs.update({'rate': forms.RadioSelect(attrs={'name': 'rating'}, choices=choices)})
#     # q = forms.NullBooleanField()
#     # q = forms.Select(choices=choices)
#
#     # q = forms.NullBooleanField(widget=ChoiceRadioSelect, label='')
#     # q = forms.NullBooleanField(widget=ChoiceRadioSelect)
#     # print('==== Q.LABEL: ', q.label)
#
#     # queryset = Planet.objects.all()
#
#     queryset = Answer.objects.all()
#     q = forms.ModelChoiceField(queryset=queryset, widget=ChoiceRadioSelect, label='')
#
#
#     # q = forms.NullBooleanField(widget=ChoiceRadioSelect, label=' * ')
#
#     def clean_q(self):
#         new_q = self.cleaned_data['q']
#         print('===new_q: ', new_q)
#         if new_q is None:
#             raise ValidationError('Поле: {}, надо заполнить'.format(new_q))
#         return new_q
#
#     def save(self):
#         self.clean()
#         new_obj = {'quest': self.label_suffix, 'answ': self.cleaned_data}
#         return new_obj
#
#
# # class QForm(forms.Form):
# #     # q = forms.NullBooleanField(widget=NullBooleanRadioSelect)
# #     q = forms.NullBooleanField()
# #     # q.label = ' '
# #     q.label = 'Вопрос: '
# #
# #     def save(self):
# #         new_recruit = Recruit.objects.update(answers=self.cleaned_data['q.label'])
# #         return new_recruit
# #
#
# # class QuestionFormSet(forms.Form):
# #     QuestionFormSet = formset_factory(QuestionForm)
#
#
# # ----------------------------------
#     # questions = random.sample(list(Test.objects.all()), 1)[0].question
#     # q.label = questions
#
#     # ques = forms.ModelChoiceField(queryset=questions, empty_label='assss asass')
#                                   # , widget=forms.Textarea(attrs={'class': 'alert alert-secondary'}))
#     # ques = forms.Textarea(attrs={'class': 'alert alert-secondary'})
#     # comment = forms.CharField(widget=forms.Textarea)
#
#     # def save(self):
#     #     new_answer = {self.q.label_suffix: self.q}
#     # #         name=self.cleaned_data['name'],
#     # #         planet=self.cleaned_data['planet'],
#     # #         age=self.cleaned_data['age'],
#     # #         email=self.cleaned_data['email']
#     # #     )
#     #     print('===new_answeeer: ', new_answer)
#     #     return new_answer
# # ----------------------------
#     # q.label = ' '
#     # # q.label = 'Вопрос: '
#     # print('==q.label_suffix===: ', q.label)
# # -----------------------
# #     Recruit.objects.create(
# #     name=self.cleaned_data['name'],
# #     planet=self.cleaned_data['planet'],
# #     age=self.cleaned_data['age'],
# #     email=self.cleaned_data['email']
# # )
# # -----------------------------
#     #         name=self.cleaned_data['name'],
#     #         planet=self.cleaned_data['planet'],
#     #         age=self.cleaned_data['age'],
#     #         email=self.cleaned_data['email']
#     #     )
#
# # ----------------------
#     # def get_count_question_form_set():
#     #     count = random.randint(2, 5)
#     #     # count = 2
#     #     question_form_set = formset_factory(QuestionForm, extra=count)
#     #     return (count, question_form_set)
#
# # --------------------------------------------
# # class RecruitForm(forms.Form):
# #     name = forms.CharField(max_length=50)
# #     # planet = forms.ChoiceField(Recruit.planet.objects.name)
# #     planet = forms.ModelChoiceField(Planet.objects.all())
# #     age = forms.IntegerField()
# #     email = forms.EmailField(max_length=50)
# #     # slug = forms.SlugField(max_length=100)
# #
# #     name.widget.attrs.update({'class': 'form-control'})
# #     planet.widget.attrs.update({'class': 'form-control'})
# #     age.widget.attrs.update({'class': 'form-control'})
# #     email.widget.attrs.update({'class': 'form-control'})
# #
# #     def clean_slug(self):       # не нужен , слаг не вводим, автоматом формируеться
# #         new_slug = self.cleaned_data['slug'].lower()   # self.cleaned_data.get('slug')
# #
# #         if new_slug == 'create':
# #             raise ValidationError('Slug may not be "Create"')
# #         if Recruit.objects.filter(slug__exact=new_slug).count():
# #             raise ValidationError('Слаг должен быть уникальным')
# #         return new_slug
# #
# #     def clean_email(self):
# #         new_email = self.cleaned_data['email']
# #         if Recruit.objects.filter(email=new_email):
# #             raise ValidationError('Е-маил: {}, уже используется'.format(new_email))
# #         return new_email
# #
# #     def save(self):
# #         new_recruit = Recruit.objects.create(
# #             name=self.cleaned_data['name'],
# #             planet=self.cleaned_data['planet'],
# #             age=self.cleaned_data['age'],
# #             email=self.cleaned_data['email']
# #         )
# #         return new_recruit
# # ----------------------------------------------------------
#     # for i in range(3):
#     # q = forms.NullBooleanField(null=True)
#     # q = forms.BooleanField()
#     # q = forms.ModelChoiceField(Planet.objects.filter(name__contains='Ко'))
#     # ques = forms.Textarea(attrs={'class': 'alert alert-secondary'})
#     # ques = forms.CharField(widget=forms.Textarea(attrs={"rows":5, "cols":20}))
#     # questions = Test.objects.all()
#
#     # def __init__(self, questions, *args, **kwargs):
#     #     # label = random.sample(list(Test.objects.all()), 1)[0].question
#     #     super(forms.Form, self).__init__(label_suffix=questions, *args, **kwargs)
#     # q.label = ' '
#
# # -------------------------------------------
#     # >> > from django import forms
#     # >> >
#     #
#     # class ArticleForm(forms.Form):
#     #     ...
#     #     title = forms.CharField()
#     #
#     # ...
#     # pub_date = forms.DateField()
# # -------------
# # from django.forms.formsets import formset_factory
# # >>> ArticleFormSet = formset_factory(ArticleForm)
# # ----------------
# # formset = ArticleFormSet()
# # >>> for form in formset:
# # ...     print(form.as_table())
#
# # ----------------------------------------------------
# # class RecruitQuestionsForm(forms.ModelForm):
# #     class Meta:
# #         model = Recruit
# #         fields = ['name', 'question', '']
# # -------------------------------------------
# # print('=======Объект новый или Update: ', self.instance)
# # print('=======Объект новый или Update: ', self.instance, self.instance.slug)
# # if Recruit.objects.filter(email=new_email) and not self.instance.slug:  # Если новый и не Update, тогда отказ.
#
# # --------------------------------
#     # name = forms.CharField(max_length=50)
#     # # planet = forms.ChoiceField(Recruit.planet.objects.name)
#     # planet = forms.ModelChoiceField(Planet.objects.all())
#     # age = forms.IntegerField()
#     # email = forms.EmailField(max_length=50)
#     # # slug = forms.SlugField(max_length=100)
#     #
#     # name.widget.attrs.update({'class': 'form-control'})
#     # planet.widget.attrs.update({'class': 'form-control'})
#     # age.widget.attrs.update({'class': 'form-control'})
#     # email.widget.attrs.update({'class': 'form-control'})
# # --------------------------------
#     # def clean_slug(self):       # не нужен , слаг не вводим, автоматом формируеться
#     #     new_slug = self.cleaned_data['slug'].lower()   # self.cleaned_data.get('slug')
#     #
#     #     if new_slug == 'create':
#     #         raise ValidationError('Slug may not be "Create"')
#     #     if Recruit.objects.filter(slug__exact=new_slug).count():
#     #         raise ValidationError('Слаг должен быть уникальным')
#     #     return new_slug
# # --------------------------------
#     # def save(self):
#     #     new_recruit = Recruit.objects.create(
#     #         name=self.cleaned_data['name'],
#     #         planet=self.cleaned_data['planet'],
#     #         age=self.cleaned_data['age'],
#     #         email=self.cleaned_data['email']
#     #     )
#     #     return new_recruit
# # --------------------------------
# # class RecruitForm(ModelForm):
# #     class Meta:
# #         model = Recruit
# #         fields = ('name', 'planet', 'age', 'email')
# # --------------------------------
#
# # class QuestionsForm(forms.formset_factory(QForm)):
# #     QuestionsFormSet = formset_factory(QForm, extra=3)
# #     questions = random.sample(list(Test.objects.all()), 3)
# #     print(questions)
# #     print('===rkffff===', type(questions))
# #     # form = QuestionsForm()
# #     formset = QuestionsFormSet()
# #     # QuestionsFormSet = formset_factory(QuestionsForm, extra=3)
# #     # formset = QuestionsFormSet()
# #     for form in formset:
# #         form.label_suffix = random.choice(Test.objects.all())
# #         print(form)
#
#     # answer0 = forms.ChoiceField(label=questions[0], widget=forms.RadioSelect(), choices=CHOICES)
#     # answer1 = forms.NullBooleanField(label=questions[1])
#     # answer2 = forms.NullBooleanField(label=questions[2])
#
#
#     # ans = []
#     # for i in range(3):
#     #     ques = 'answer_'+str(i)
#     #     ans.append(ques)
#     # print(ans)
#     # i = 0
#     # for q in questions:
#     #     f = str(q) + str(i)
#     #     ans[i] = forms.NullBooleanField(label=q)
#     #     i += 1
#     # CHOICES = (('0', 'Нет',), ('1', 'Да',))
#     # answer0 = forms.NullBooleanField(label=questions[0], widget=forms.RadioSelect)
#
#     # length = Test.objects.all().count()
#     # random_pk = random.randint(0, length)
#     # label = random.sample(list(Test.objects.all()), 1)
#     # label = str(Test.objects.get(pk=random_pk))
#     # question = forms.CharField(label=label)
#     # question = forms.BooleanField(label=label)
#
#     # label = random.choice(Test.objects.all())
#
#     # for q in questions:
#     # answer = []
#
#     # ans = []
#    # for i in range(3):
#    #     ques = 'answer'+str(i)
#    #     ans.append(ques)
#    #  # print(ans)
#    # for a in ans:
#    #     a = forms.NullBooleanField()





