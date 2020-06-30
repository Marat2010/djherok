# from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.views.generic import View, CreateView
from django.urls import reverse_lazy, reverse
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Sith, Recruit, Planet, Test, Order
from .forms import RecruitForm, SithForm, RecruitQuestionsForm
import random
from django.forms import formset_factory
from django.shortcuts import redirect
from .utils import ObjectDetailMixin, ObjectCreateMixin, ObjectUpdateMixin


def index(request):
    return render(request, 'si/index.html')


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


def siths_list(request):
    siths = Sith.objects.all()
    return render(request, 'si/siths_list.html', context={'siths': siths})


def siths_count_hands(request, count_hands):
    queryset = []
    for si in Sith.objects.all():
        if si.get_count_hands() >= count_hands:
            queryset.append(si)
    print(queryset)
    print(request.path)
    return render(request, 'si/siths_count_hands.html', context={'siths': queryset})


class RecruitDetail(ObjectDetailMixin, View):
    model = Recruit
    template = 'si/recruit_detail.html'


class SithDetail(ObjectDetailMixin, View):
    model = Sith
    template = 'si/sith_detail.html'


class RecruitCreate(CreateView):
    model = Recruit
    template_name = 'si/recruit_create.html'
    context_object_name = 'form'
    form_class = RecruitForm
    success_url = '../{slug}/questions/'


class SithCreate(ObjectCreateMixin, View):
    model_form = SithForm
    template = 'si/sith_create.html'


class RecruitUpdate(ObjectUpdateMixin, View):
    model = Recruit
    model_form = RecruitForm
    template = 'si/recruit_update.html'


class SithUpdate(ObjectUpdateMixin, View):
    model = Sith
    model_form = SithForm
    template = 'si/sith_update.html'


def siths_planet(request, slug):
    planet_id = Planet.objects.get(slug__iexact=slug).pk
    planet_name = Planet.objects.get(slug__iexact=slug).name
    siths = Sith.objects.filter(planet=planet_id)
    # get_object_or_404(Chats, slug__iexact=
    return render(request, 'si/siths_planet.html', context={'siths': siths, 'planet': planet_name})


def siths_order(request, slug):
    order_id = Order.objects.get(slug__iexact=slug).pk
    order_name = Order.objects.get(slug__iexact=slug).name
    siths = Sith.objects.filter(order=order_id)
    # get_object_or_404(Chats, slug__iexact=
    return render(request, 'si/siths_order.html', context={'siths': siths, 'order': order_name})


def recruits_planet(request, slug):
    planet_id = Planet.objects.get(slug__iexact=slug).pk
    planet_name = Planet.objects.get(slug__iexact=slug).name
    recruits = Recruit.objects.filter(planet=planet_id)
    # get_object_or_404(Chats, slug__iexact=
    return render(request, 'si/recruits_planet.html', context={'recruits': recruits, 'planet': planet_name})


def recruits_order(request, slug):
    print('-- SLug:  ', slug, type(slug))
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
    print('---recruits: ', recruits)

    return render(request, 'si/recruits_order.html', context={'recruits': recruits, 'order': order_name})


def sith_authorization(request):
    return render(request, 'si/sith_authorization.html')


def task_view(request):
    return render(request, 'si/the_task.html')


# -----------------------------------------------------

class RecruitQuestions(View):
    def get(self, request, slug):
        recruit = get_object_or_404(Recruit, slug__iexact=slug)
        question = random.sample(list(Test.objects.all()), 1)[0].question
        # question = random.sample(list(Test.objects.all()), 2)
        print('====question: ', question)

        # form = RecruitQuestionsForm(question)
        # form = RecruitQuestionsForm(label_suffix=question)
        form = RecruitQuestionsForm(label_suffix=question)

        # form.label_suffix = question
        # form.label = question
        return render(request, 'si/recruit_questions.html', context={'form': form, 'recruit': recruit})
        # return render(request, 'si/recruit_questions.html', context={'form': form})

    def post(self, request, slug):
        pass
    #     recruit = get_object_or_404(Recruit, slug__iexact=slug)
    #     bound_form = RecruitQuestionsForm('', request.POST)
    #     print('===2=bound_form:', bound_form.fields['q'].label, '==data:', bound_form.data['q'])
    #     bound_form.save()
    #     # print('===BOUND_FOR: ', bound_form)
    #     return render(request, 'si/recruit_questions.html', context={'form': bound_form, 'recruit': recruit})



    # class RecruitCreate2(ObjectCreateMixin, View):
    #     model_form = RecruitForm
    #     template = 'si/recruit_create.html'
    #     # success_url = Recruit.get_questions_url
    #     # success_url = reverse_lazy('recruit_questions_url', kwargs={'slug': Recruit.get_questions_url})

    # success_url = reverse_lazy('recruit_questions_url', kwargs={'slug': '{slug}'})
    # print('--Success URL: ', success_url())
    # success_url = redirect('recruit_detail_url')
    # success_url = reverse_lazy('get_absolute_url')

    # def form_valid(self, form):
    #     obj = form.save(commit=False)
    #     obj.profile_id = self.request.user.id
    #     # obj.slug = self.get_success_url()
    #     print('====slug: ', obj.slug)
    #     obj.save()
    #     self.success_url = self.model.get_absolute_url(obj)

    # def get_success_url(self):
    #     if 'slug' in self.kwargs:
    #         slug = self.kwargs['slug']
    #     else:
    #         slug = 'demo'
    #     return reverse_lazy('recruit_questions_url', kwargs={'slug': slug})

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



