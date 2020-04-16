from django.forms import ModelForm
from django import forms
from .models import Recruit, Test
import random
from django.forms import formset_factory


class RecruitForm(ModelForm):
    class Meta:
        model = Recruit
        fields = ('name', 'planet', 'age', 'email')


class NullBooleanRadioSelect(forms.RadioSelect):
    def __init__(self, *args, **kwargs):
        choices = ((True, 'Да'), (False, 'Нет'))
        super(NullBooleanRadioSelect, self).__init__(choices=choices, *args, **kwargs)
    _empty_value = None


class QForm(forms.Form):
    q = forms.NullBooleanField(widget=NullBooleanRadioSelect)
    q.label = ' '    # q.label = 'Вопрос: '


# class QuestionsForm(forms.formset_factory(QForm)):
#     QuestionsFormSet = formset_factory(QForm, extra=3)
#     questions = random.sample(list(Test.objects.all()), 3)
#     print(questions)
#     print('===rkffff===', type(questions))
#     # form = QuestionsForm()
#     formset = QuestionsFormSet()
#     # QuestionsFormSet = formset_factory(QuestionsForm, extra=3)
#     # formset = QuestionsFormSet()
#     for form in formset:
#         form.label_suffix = random.choice(Test.objects.all())
#         print(form)

    # answer0 = forms.ChoiceField(label=questions[0], widget=forms.RadioSelect(), choices=CHOICES)
    # answer1 = forms.NullBooleanField(label=questions[1])
    # answer2 = forms.NullBooleanField(label=questions[2])


    # ans = []
    # for i in range(3):
    #     ques = 'answer_'+str(i)
    #     ans.append(ques)
    # print(ans)
    # i = 0
    # for q in questions:
    #     f = str(q) + str(i)
    #     ans[i] = forms.NullBooleanField(label=q)
    #     i += 1
    # CHOICES = (('0', 'Нет',), ('1', 'Да',))
    # answer0 = forms.NullBooleanField(label=questions[0], widget=forms.RadioSelect)

    # length = Test.objects.all().count()
    # random_pk = random.randint(0, length)
    # label = random.sample(list(Test.objects.all()), 1)
    # label = str(Test.objects.get(pk=random_pk))
    # question = forms.CharField(label=label)
    # question = forms.BooleanField(label=label)

    # label = random.choice(Test.objects.all())

    # for q in questions:
    # answer = []

    # ans = []
   # for i in range(3):
   #     ques = 'answer'+str(i)
   #     ans.append(ques)
   #  # print(ans)
   # for a in ans:
   #     a = forms.NullBooleanField()





