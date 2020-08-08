# from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.views.generic import View, CreateView
from django.urls import reverse_lazy, reverse
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Sith, Recruit, Planet, Test, Order, Answer, RecruitAnswer
from .forms import RecruitForm, SithForm, RecruitQuestionsForm
from django.shortcuts import redirect
from .utils import ObjectDetailMixin, ObjectCreateMixin, ObjectUpdateMixin
from django.forms import modelformset_factory
from django.core.mail import send_mail
import random
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.core.mail import EmailMessage
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin


def index(request):
    return render(request, 'si/index.html')


# @login_required(login_url='/si/sith_authorization/')
@login_required(login_url='sith_authorization_url')
def recruits_list(request):
    recruits = Recruit.objects.all()

    # paginator = Paginator(recruits, 3)
    #
    # page_number = request.GET.get('page', 1)
    # page = paginator.get_page(page_number)
    #
    # is_paginated = page.has_other_pages()
    #
    # if page.has_previous():
    #     prev_url = '?page={}'.format(page.previous_page_number())
    # else:
    #     prev_url = ''
    #
    # if page.has_next():
    #     next_url = '?page={}'.format(page.next_page_number())
    # else:
    #     next_url = ''
    #
    # context = {
    #     'page_object': page,
    #     'is_paginated': is_paginated,
    #     'prev_url': prev_url,
    #     'next_url': next_url,
    #     'recruits': recruits
    # }
    #
    # # return render(request, 'bitr24/index.html', context=context)
    # return render(request, 'si/recruits_list.html', context=context)

    return render(request, 'si/recruits_list.html', context={'recruits': recruits})


@login_required(login_url='sith_authorization_url')
def siths_list(request):
    siths = Sith.objects.all()
    return render(request, 'si/siths_list.html', context={'siths': siths})


@login_required(login_url='sith_authorization_url')
def siths_count_hands(request, count_hands):
    queryset = []
    for si in Sith.objects.all():
        if si.get_count_hands() >= count_hands:
            queryset.append(si)
    # print(queryset)
    # print(request.path)
    return render(request, 'si/siths_count_hands.html', context={'siths': queryset})


class RecruitDetail(ObjectDetailMixin, View):
    model = Recruit
    template = 'si/recruit_detail.html'
    answers = True


class SithDetail(LoginRequiredMixin, ObjectDetailMixin, View):
    login_url = 'sith_authorization_url'
    model = Sith
    template = 'si/sith_detail.html'


class RecruitCreate(CreateView):
    model = Recruit
    template_name = 'si/recruit_create.html'
    context_object_name = 'form'
    form_class = RecruitForm
    success_url = '../{slug}/questions/'


class SithCreate(LoginRequiredMixin, ObjectCreateMixin, View):
    login_url = 'sith_authorization_url'
    model_form = SithForm
    template = 'si/sith_create.html'


class RecruitUpdate(LoginRequiredMixin, ObjectUpdateMixin, View):
    login_url = 'sith_authorization_url'
    model = Recruit
    model_form = RecruitForm
    template = 'si/recruit_update.html'


class SithUpdate(LoginRequiredMixin, ObjectUpdateMixin, View):
    login_url = 'sith_authorization_url'
    model = Sith
    model_form = SithForm
    template = 'si/sith_update.html'


@login_required(login_url='sith_authorization_url')
def siths_planet(request, slug):
    planet_id = Planet.objects.get(slug__iexact=slug).pk
    planet_name = Planet.objects.get(slug__iexact=slug).name
    siths = Sith.objects.filter(planet=planet_id)
    # get_object_or_404(Chats, slug__iexact=
    return render(request, 'si/siths_planet.html', context={'siths': siths, 'planet': planet_name})


@login_required(login_url='sith_authorization_url')
def siths_order(request, slug):
    order_id = Order.objects.get(slug__iexact=slug).pk
    order_name = Order.objects.get(slug__iexact=slug).name
    siths = Sith.objects.filter(order=order_id)
    # get_object_or_404(Chats, slug__iexact=
    return render(request, 'si/siths_order.html', context={'siths': siths, 'order': order_name})


@login_required(login_url='sith_authorization_url')
def recruits_planet(request, slug):
    planet_id = Planet.objects.get(slug__iexact=slug).pk
    planet_name = Planet.objects.get(slug__iexact=slug).name
    recruits = Recruit.objects.filter(planet=planet_id)
    # get_object_or_404(Chats, slug__iexact=
    return render(request, 'si/recruits_planet.html', context={'recruits': recruits, 'planet': planet_name})


@login_required(login_url='sith_authorization_url')
def recruits_order(request, slug):
    recruits = []
    recruits_not_sith = []

    for recruit in Recruit.objects.all():
        if recruit.sith:
            if recruit.sith.order.slug == slug:
                recruits.append(recruit)
        else:
            recruits_not_sith.append(recruit)
    if slug != 'None':
        order_name = Order.objects.get(slug__iexact=slug).name
    else:
        order_name = 'None'
        recruits = recruits_not_sith

    return render(request, 'si/recruits_order.html', context={'recruits': recruits, 'order': order_name})


def sith_authorization(request):
    return render(request, 'si/sith_authorization.html')


@login_required(login_url='sith_authorization_url')
def task_view(request):
    return render(request, 'si/the_task.html')


def recruit_questions(request, slug):
    recruit = Recruit.objects.get(slug=slug)
    recruitanswer_formset = modelformset_factory(RecruitAnswer, form=RecruitQuestionsForm, extra=0)

    if request.method == 'POST':
        recruitanswer = RecruitAnswer.objects.filter(recruit=recruit)

        formset = recruitanswer_formset(request.POST, queryset=recruitanswer)
        if formset.is_valid():
            formset.save()
            # return render(request, 'si/recruit_detail.html', {'slug': slug, 'recruit': recruit})
            # return render(request, 'si/recruit_answer.html', {'slug': slug, 'recruit': recruit})
            return redirect('recruit_detail_url', slug=slug)

    else:
        recruitanswer = recruit.refresh_question()  # Обновление вопросов при каждом запросе

        formset = recruitanswer_formset(queryset=recruitanswer)
        for i, form in enumerate(formset):
            form.instance = recruitanswer[i]
            # form.label_suffix = questions[i]
    return render(request, 'si/recruit_questions.html', {'form': formset, 'slug': slug, 'recruit': recruit})


@login_required(login_url='sith_authorization_url')
def recruit_take(request, slug):
    limit_sith_number = 3  # Количество рекрутов, которое может взять ситх
    recruit = Recruit.objects.get(slug=slug)
    sith_visit = request.session.get('sith_visit', None)
    try:
        sith = Sith.objects.get(slug=sith_visit)
        print('======== Ситх: {}, кол-во рекрутов: {}'.format(sith.name, len(sith.recruits.all())))
        if len(sith.recruits.all()) >= limit_sith_number:
            return redirect('limit_sith_url')
        sith.recruits.add(recruit)
        sith.save()
    except Sith.DoesNotExist:
        print('===== Ситх не вошел: ', sith_visit)
        return redirect('not_sith_url')

    message_email = ' Наши поздравления {} с планеты {}!!!\n<br>'.format(recruit.name, recruit.planet)
    message_email += '\n Вы зачислены рукой тени к {}'.format(recruit.sith)
    html_message = '<h4>{}</h4>'.format(message_email)

    rezult_send = send_mail('Служба рекрутинга для ордена Ситхов', message_email, 'si.recruit@bk.ru',
              [recruit.email], fail_silently=True, html_message=html_message)
    rezult_send = 'Отправлено' if rezult_send == 1 else 'НЕ УШЛО!!!'
    print('===== Письмо отправлено: ', rezult_send)
    print('====ЗАЧИСЛЕН===Рекрут: {},  Кем: {}, Письмо: {} '.format(recruit, sith_visit, rezult_send))

    if request.method == 'GET':
        return redirect(recruit)


def not_sith(request):
    return render(request, 'si/not_sith.html')


def limit_sith(request):
    return render(request, 'si/limit_sith.html')


# --------------------------------------
#     self.model._meta.object_name
# si.models.Sith.DoesNotExist: Sith matching query does not exist.
# [07/Aug/2020 11:38:27] "GET /si/recruit/marat-1596747586/take/ HTTP/1.1" 500 81965
    # except Exception as e:
# print('-===========EEEEEEE: ', e)
# ------------------------------------
# raise ValidationError('ВЫ не вошли под ситхом!!! "{}"'.format(e))
# return redirect('siths_list_url')
# messages.success(request, 'Необходимо войти под ситхом!!!')
# messages.add_message(request, messages.INFO, 'Необходимо войти под ситхом')

# html_message += '<img src="/static/si/Yoda.png">'
    # em = EmailMessage(subject='Результаты отбора!', body=message_email, to=[recruit.email])
    # em.send()
    # em.send(fail_silently=True)
# ------------------------------------
    # num_visits = request.session.get('num_visits', 0)  # Подсчет заходов ситха
    # request.session['num_visits'] = num_visits + 1
# ---------------------------------------
# def recruit_answer(request, slug):
#     recruit = Recruit.objects.get(slug=slug)
#     # return redirect('recruit_answer_url')
#     return render(request, 'si/recruit_answer.html', {'slug': slug, 'recruit': recruit})

# ---------------------------
    # sith_visit = request.session.get('sith_visit', 'mini')
    # # session_info = request.session['ep10ts2w1s2odxtw50yt8ppbsuocekcc']
    # num_visits = request.session.get('num_visits', 0)
    # request.session['num_visits'] = num_visits + 1
    # print('===Session_info: {} --Second-: {} '.format(sith_visit, num_visits))


# # -----------------------------------------------------
# def recruit_questions_one(request, slug):  # Для одного вопроса без formset-а
#     recruit = Recruit.objects.get(slug=slug)
#
#     if request.method == 'POST':
#         recruitanswer = RecruitAnswer.objects.filter(recruit=recruit)[0]
#         form = RecruitQuestionsForm(request.POST, instance=recruitanswer)
#         if form.is_valid():
#             form.save()
#             print('==RECRUIT method POST', form.fields['answer'].label)
#             return redirect(recruit)
#     else:
#         recruitanswer = recruit.refresh_question()[0]
#         form = RecruitQuestionsForm(instance=recruitanswer)
#         print('==instance: ===Recr: {}, \t===Quest: {}, \t===ANSw: {}'.
#               format(recruitanswer.recruit, recruitanswer.question,
#                      Test.objects.get(question=recruitanswer.question).answers.all()))
#     return render(request, 'si/recruit_questions.html', {'form': form, 'slug': slug, 'recruit': recruit})
# # -----------------------------------------------------




# def recruit_questions2(request, slug):
#     recruit = Recruit.objects.get(slug=slug)
#     if request.method == 'POST':
#         form = RecruitQuestionsForm2
#     else:
#         #         formset = question_form_set(QuestionForm)
#         #         formset = formset_factory(QForm, extra=count)()
#         #         count = 3
#         #         questions = random.sample(list(Test.objects.all()), count)
#         #         formset = formset_factory(QForm, extra=count)()
#         #         for i, form in enumerate(formset):
#         #             form.label_suffix = questions[i]        #
#         #         return render(request, 'si/recruit_questions.html', context={'form': formset})
#
#         questions = random.sample(list(Test.objects.all()), 3)
#         # form = RecruitQuestionsForm2
#         formset = formset_factory(RecruitQuestionsForm2, extra=3)
#         for i, form in enumerate(formset):
#             form.label = questions[i]
#     # return render(request, 'si/recruit_questions.html', {'form': form, 'slug': ''})
#     # return render(request, 'si/recruit_questions.html', {'form': form, 'slug': slug, 'recruit': recruit})
#     return render(request, 'si/recruit_questions.html', {'form': formset, 'slug': slug, 'recruit': recruit})







# -----------------------------------------------------
# ------------------------------------------------------
# questions = Test.objects.filter(pk__in=(i.question.pk for i in recruitanswer))
# print('==Questions from recruitanswer: ', questions)

# form = RecruitQuestionsForm(instance=recruitanswer)
# recruit_questions_formset = modelformset_factory(RecruitQuestionsForm1())
# recruit_questions_formset = formset_factory(RecruitQuestionsForm1(instance=recruitanswer))
# formset_ra = modelformset_factory(RecruitAnswer, fields=('answer',), labels={'answer': Test.question})

# RecruitQuestionsFormSet = modelformset_factory(RecruitAnswer, form=RecruitQuestionsForm1(instance=recruitanswer), fields=('answer',))
# formset_ra = inlineformset_factory(Test, RecruitAnswer, form=RecruitQuestionsForm1, extra=1)

# labels={'answer': recruitanswer.first().question})
# recruit_questions_formset = modelformset_factory(RecruitAnswer, form=RecruitQuestionsForm1(instance=recruitanswer[0]))
# recruit_questions_formset = modelformset_factory(RecruitAnswer, fields=('answer',),
#                                                  form=RecruitQuestionsForm1(),
#                                                  labels={'answer': recruitanswer.first().question})

# recruit_questions_formset = modelformset_factory(RecruitAnswer, fields=('answer',), extra=0
#                         , labels={'answer-0': 'WWWWWWWW-11111', 'id_form-1-answer': 'WWWWWWWW-11111'})
#                         # , labels={'answer': [i.question.question for i in recruitanswer]})
#                                                  # form=RecruitQuestionsForm1(),

# print('==FormSET', formset_ra())
# print('==instance: ===Recr: {}, \t===Quest: {}, \t===ANSw: {}'.
#       format(recruitanswer[0].recruit, recruitanswer[0].question,
#              Test.objects.get(question=recruitanswer[0].question).answers.all()))

# formset = formset_ra(instance=recruitanswer[0].question)

# formset = formset_ra(queryset=questions)
# ----------------------------------------------------
# form.instance.answer = form.cleaned_data['answer']
# form.instance.question = form.fields['answer'].label
# -------------------------------------------
# form = modelform_factory(RecruitAnswer, fields=('answer',),
#                          labels={'answer': recruitanswer.question})

# RecruitAnswerFormSet = modelformset_factory(RecruitAnswer, form=form, max_num=3)

# form = RecruitQuestionsForm(instance=recruitanswer, label_suffix=recruitanswer.question)
# queryset = Test.objects.get(question=recruitanswer.question).answers.all()}
# form = RecruitQuestionsForm(instance=recruitanswer, label_suffix=recruitanswer.question)

# old_questions = RecruitAnswer.objects.filter(recruit=recruit)
# old_questions.delete()
#
# # questions = random.sample(list(Test.objects.all()), 1)[0]
# questions = random.sample(list(Test.objects.all()), number_questions)
# recruitanswer = RecruitAnswer.objects.none()
# for question in questions:
#     recruitanswer = RecruitAnswer.objects.create(question=question, recruit=recruit)

# ------------------------------------------
# -----------------------------
# instance = form.save(commit=False)
# form.instance.recruit = recruit
# form.instance.question = form.questions
# new_obj = form.save()
# return redirect('index')
# return redirect('recruit_detail_url', {'slug': slug})
# return reverse_lazy('recruit_detail_url')

# --------------------------------------------------------------------
# class RecruitAnswers(ObjectDetailMixin, View):  # Ненужен (Перенос в RecruitDetail)
#     model = Recruit
#     template = 'si/recruit_detail.html'
#     answers = True
#     # answers = 'asasas---------'
#     # recruit = get_object_or_404(Recruit, slug__iexact=slug)

# def recruit_answer(request, slug):
#     pass
#     # recruit = Recruit.objects.get(slug=slug)
#     # return render(request, 'si/recruit_answers.html', {'form': form, 'slug': slug,
#     #                                                      'recruit': recruit})
# ------------------------------------------
# form = RecruitQuestionsForm(question='1111111111111qqqqqqqqqqqq')
# question = Test.objects.get(pk=1)
# form = RecruitQuestionsForm(initial={label: question})
# form = RecruitQuestionsForm({'question': question})

# print('==form.clean: ', form.Meta.labels)
# print('==form.xxxx: ', form.Meta.questions, type(form.Meta.questions))

# class RecruitQuestions(View):
#     def get(self, request, slug):
#         recruit = get_object_or_404(Recruit, slug__iexact=slug)
#         question = random.sample(list(Question.objects.all()), 1)[0].question
#         # question = random.sample(list(Test.objects.all()), 2)
#         print('====question: ', question)
#
#         # form = RecruitQuestionsForm(question)
#         # form = RecruitQuestionsForm(label_suffix=question)
#         form = RecruitQuestionsForm(label_suffix=question)
#
#         # form.label_suffix = question
#         # form.label = question
#         return render(request, 'si/recruit_questions.html', context={'form': form, 'recruit': recruit})
#         # return render(request, 'si/recruit_questions.html', context={'form': form})
#
#     def post(self, request, slug):
#         pass
#     #     recruit = get_object_or_404(Recruit, slug__iexact=slug)
#     #     bound_form = RecruitQuestionsForm('', request.POST)
#     #     print('===2=bound_form:', bound_form.fields['q'].label, '==data:', bound_form.data['q'])
#     #     bound_form.save()
#     #     # print('===BOUND_FOR: ', bound_form)
#     #     return render(request, 'si/recruit_questions.html', context={'form': bound_form, 'recruit': recruit})
#
#
#
#     # class RecruitCreate2(ObjectCreateMixin, View):
#     #     model_form = RecruitForm
#     #     template = 'si/recruit_create.html'
#     #     # success_url = Recruit.get_questions_url
#     #     # success_url = reverse_lazy('recruit_questions_url', kwargs={'slug': Recruit.get_questions_url})
#
#     # success_url = reverse_lazy('recruit_questions_url', kwargs={'slug': '{slug}'})
#     # print('--Success URL: ', success_url())
#     # success_url = redirect('recruit_detail_url')
#     # success_url = reverse_lazy('get_absolute_url')
#
#     # def form_valid(self, form):
#     #     obj = form.save(commit=False)
#     #     obj.profile_id = self.request.user.id
#     #     # obj.slug = self.get_success_url()
#     #     print('====slug: ', obj.slug)
#     #     obj.save()
#     #     self.success_url = self.model.get_absolute_url(obj)
#
#     # def get_success_url(self):
#     #     if 'slug' in self.kwargs:
#     #         slug = self.kwargs['slug']
#     #     else:
#     #         slug = 'demo'
#     #     return reverse_lazy('recruit_questions_url', kwargs={'slug': slug})


# def recruit_create(request):
#     if request.method == 'POST':
#         form = RecruitForm(request.POST)
#         if form.is_valid():
#             recruit = form.save()
#             return redirect(recruit.get_questions_url())
#     else:
#         form = RecruitForm()
#     return render(request, 'si/recruit_create.html', {'form': form})

# # class RecruitQuestionsView(CreateView):
# class RecruitQuestionsView(View):
#     # def get(self, request):
#     @staticmethod
#     def get(request):
#         count = 3
#         questions = random.sample(list(Test.objects.all()), count)
#         formset = formset_factory(QForm, extra=count)()
#         for i, form in enumerate(formset):
#             form.label_suffix = questions[i]
#
#         return render(request, 'si/recruit_questions.html', context={'form': formset})

# -----------------------------------

# ---------------------------
    # def get(self, request):
    #     form = RecruitForm()
    #     return render(request, 'si/recruit_create.html', context={'form': form})
    #
    # def post(self, request):
    #     bound_form = RecruitForm(request.POST)
    #
    #     if bound_form.is_valid():
    #         new_recruit = bound_form.save()
    #         return redirect(new_recruit)
    #     return render(request, 'si/recruit_create.html', context={'form': bound_form})
# -------------------------------
    # def get(self, request):
    #     form = SithForm()
    #     return render(request, 'si/sith_create.html', context={'form': form})
    #
    # def post(self, request):
    #     bound_form = SithForm(request.POST)
    #
    #     if bound_form.is_valid():
    #         new_sith = bound_form.save()
    #         return redirect(new_sith)
    #     return render(request, 'si/sith_create.html', context={'form': bound_form})
# ---------------------------
# class RecruitCreateView(CreateView):
#     template_name = 'si/recruit_create.html'
#     # template_name = 'si/recruit_questions.html'
#     form_class = RecruitForm
#     success_url = reverse_lazy('index')
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['planet'] = Planet.objects.all()
#         return context
#         # return render(request, 'si/recruit_questions.html', context=context)
#
#     def post(self, request, *args, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['planet'] = Planet.objects.all()
#         return redirect(reverse('recruit_questions_url'))
#     # redirect_url = 'recruit_questions_url'
# -------------------------------
        # return render(request, 'si/recruit_questions.html', context={'form': form, 'context': questions})
        # form.label_suffix = random.choice(Test.objects.all())
        # QuestionsFormSet = formset_factory(QuestionsForm, extra=3)
        # formset = QuestionsFormSet()
        # label = random.choice(Test.objects.all())
        # form = form + QuestionsForm(label_suffix=questions)
        # questions = random.sample(list(Test.objects.all()), 3)
    # template_name = 'si/recruit_questions.html'
    # form_class = QuestionsForm
    # success_url = reverse_lazy('index')
    #
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['question'] = Test.objects.get(pk=4)
    #     # context['question'] = Test.objects.all()
    #     return context

# class RecruitQuestions_2(View):
#     @staticmethod
#     def get_count_question_form_set():  # Получение кол-ва вопросов и formset
#         # count = random.randint(2, 5)    # Указать свой диапазон кол-ва вопросов
#         count = random.randint(1, 1)    # Указать свой диапазон кол-ва вопросов
#         question_form_set = formset_factory(QuestionForm, extra=count)
#         # question_form_set = formset_factory(QuestionForm)
#         return (count, question_form_set)
#
#     # @staticmethod
#     # def get(request, slug):
#     def get(self, request, slug):
#         count, question_form_set = RecruitQuestions.get_count_question_form_set()
#         recruit = get_object_or_404(Recruit, slug__iexact=slug)
#         questions = random.sample(list(Test.objects.all()), count)  # Список вопросов
#         # formset = question_form_set()
#         formset = question_form_set(QuestionForm)
#         list_questions = []                         # Создаем список вопросов который выпал рекруту
#         list_questions_text = []
#         for i, form in enumerate(formset):
#             # form.label_suffix = questions[i].question  # Список вопросов для (в) "label"
#             # print('=== form.label_suffix: ', form.label_suffix)
#             # form_label_suffix.append(form.label_suffix)
#
#             # form.queryset = questions[i].answers.all()  # вытаскиваем все связанные(M2M) ответы
#             # form = QuestionForm(instance=questions[i].answers.all())
#             # form(queryset=Planet.objects.all())
#             form.answer = questions[i].answers.all()
#             print('== form.answer', form.answer)
#
#             list_questions.append(questions[i].id)  # Дополняем список (id) который выпал рекруту
#             list_questions_text.append(questions[i].question)  # Список вопросов (текст) для (в) "label"
#         print('===list_questions_text:', list_questions_text, '--Type: ', type(list_questions_text))
#         recruit.answers = list_questions         # Сохраняем список вопросов (id) который выпал рекруту
#         recruit.save()                           # в базу
#         list_questions_text.reverse()       # реверс, потому как в шаблоне вытаскиваем через ".pop" (с конца)
#         print('=== List_question', list_questions)
#         print('=== formset:', formset, '--Type: ', type(formset))
#         return render(request, 'si/recruit_questions.html',
#                       context={'formset': formset, 'recruit': recruit, 'questions': list_questions_text})
#
#     def post(self, request, slug):
#         count, question_form_set = RecruitQuestions.get_count_question_form_set()
#         print("=====Req POST: ", request.POST)
#         recruit = get_object_or_404(Recruit, slug__iexact=slug)
#         formset = question_form_set(request.POST)
#         # print('==== Foermset POST: ', formset.forms)
#         # print('====== formset in POST: ', formset)
#         new_obj = []
#         for form in formset:
#             if form.is_valid():
#                 print('==== Foermset POST: ', form.cleaned_data)
#                 new_obj.append(form.save())
#         print('====new_obj:', new_obj)
#         return render(request, 'si/recruit_questions.html', context={'formset': formset, 'recruit': recruit})


# ----------------------------------------
# uniq = [1,2,3,4,5]
# fifa = ['q1','q2','q3','q4','q5']
# uniq_and_fifa = dict(zip(uniq, fifa))  -> {1: 'q1', 2: 'q2', 3: 'q3', 4: 'q4'}
# -----------------------------------
# a = [1, 2, 3]
# >>> c = dict.fromkeys(a)      ->  # {1: None, 2: None, 3: None}
# >>> d = dict.fromkeys(a, 10)  ->  # {1: 10, 2: 10, 3: 10}
# ----------------------
# # class RecruitQuestions(View):
# #     def get(self, request, slug):
# #         recruit = get_object_or_404(Recruit, slug__iexact=slug)
# #         bound_form = RecruitQuestionsForm(instance=recruit)
# #         return render(request, 'si/recruit_questions.html', context={'form': bound_form, 'recruit': recruit})


# bound_formset = formset_factory(QuestionForm)()
# print("==bound formset: ", bound_formset)
# ArticleFormSet = formset_factory(ArticleForm, extra=2)
# formset = ArticleFormSet(initial={'title': 'Django is now open source',
#                                   'pub_date': datetime.date.today(),}])
# formset = ArticleFormSet(request.POST, initial=[...])

# if bound_form.is_valid():
# new_recruit = bound_form.save()
# new_recruit = bound_form.cleaned_data
# return redirect(new_recruit)

# --------------------------
    # def get(self, request, slug):
    #     # recruit = Recruit.objects.get(slug__iexact=slug)
    #     recruit = get_object_or_404(Recruit, slug__iexact=slug)
    #     bound_form = RecruitForm(instance=recruit)
    #     return render(request, 'si/recruit_update.html', context={'form': bound_form, 'recruit': recruit})
    #
    # def post(self, request, slug):
    #     recruit = get_object_or_404(Recruit, slug__iexact=slug)
    #     bound_form = RecruitForm(request.POST, instance=recruit)
    #
    #     if bound_form.is_valid():
    #         new_recruit = bound_form.save()
    #         return redirect(new_recruit)
    #     return render(request, 'si/recruit_update.html', context={'form': bound_form, 'recruit': recruit})
# -----------------------------------
    # print(dir(request))
    # print()
    # print(request.POST)
    # print()

    # def get(self, request, slug):
    #     # recruit = Recruit.objects.get(slug__exact=slug)
    #     recruit = get_object_or_404(Recruit, slug__iexact=slug)
    #     return render(request, 'si/recruit_detail.html', context={'recruit': recruit})
    # def get(self, request, slug):
    #     # sith = Sith.objects.get(slug__iexact=slug)
    #     sith = get_object_or_404(Sith, slug__iexact=slug)
    #     return render(request, 'si/sith_detail.html', context={'sith': sith})

# def recruit_detail(request, slug):
#     recruit = Recruit.objects.get(slug__exact=slug)
#     return render(request, 'si/recruit_detail.html', context={'recruit': recruit})

# def sith_detail(request, slug):
#     sith = Sith.objects.get(slug__iexact=slug)
#     return render(request, 'si/sith_detail.html', context={'sith': sith})

# def siths_list(request):
#     search_query = request.GET.get('search', '')
#
#     if search_query:
#         siths = Sith.objects.filter(Q(name__contains=search_query) | Q(planet__name__contains=search_query))
#     else:
#         siths = Sith.objects.all()
#
#     paginator = Paginator(siths, 5)
#
#     page_number = request.GET.get('page', 1)
#     page = paginator.get_page(page_number)
#
#     is_paginated = page.has_other_pages()
#
#     if page.has_previous():
#         prev_url = '?page={}'.format(page.previous_page_number())
#     else:
#         prev_url = ''
#
#     if page.has_next():
#         next_url = '?page={}'.format(page.next_page_number())
#     else:
#         next_url = ''
#
#     context = {
#         'page_object': page,
#         'is_paginated': is_paginated,
#         'prev_url': prev_url,
#         'next_url': next_url
#     }
#
#     return render(request, 'si/siths_list.html', context=context)



