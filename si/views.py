# from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import View, CreateView
from django.urls import reverse_lazy, reverse
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Sith, Recruit, Planet, Test
from .forms import RecruitForm, QForm
import random
from django.forms import formset_factory
from django.shortcuts import redirect


def index(request):
    return render(request, 'si/index.html')
    # return HttpResponse('<h1>Hi Ok!</h1>')


class RecruitCreateView(CreateView):
    template_name = 'si/recruit_create.html'
    form_class = RecruitForm
    success_url = reverse_lazy('index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['planet'] = Planet.objects.all()
        return context
        # return render(request, 'si/recruit_questions.html', context=context)

    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['planet'] = Planet.objects.all()
        return redirect(reverse('recruit_questions_url'))
    # redirect_url = 'recruit_questions_url'


class RecruitQuestions(View):
    pass


# class RecruitQuestionsView(CreateView):
class RecruitQuestionsView(View):
    # def get(self, request):
    @staticmethod
    def get(request):
        count = 3
        questions = random.sample(list(Test.objects.all()), count)
        formset = formset_factory(QForm, extra=count)()
        for i, form in enumerate(formset):
            form.label_suffix = questions[i]

        return render(request, 'si/recruit_questions.html', context={'form': formset})


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

def sith_authorization(request):
    return render(request, 'si/sith_authorization.html')


def task_view(request):
    return render(request, 'si/the_task.html')


def recruits_list(request):
    recruits = Recruit.objects.all()
    return render(request, 'si/recruits_list.html', context={'recruits': recruits})


def recruit_detail(request, slug):
    recruit = Recruit.objects.get(slug__exact=slug)
    return render(request, 'si/recruit_detail.html', context={'recruit': recruit})


def siths_list(request):
    siths = Sith.objects.all()
    return render(request, 'si/siths_list.html', context={'siths': siths})


def siths_count_hands(request, count):
    # siths = Sith.objects.all()
    queryset = []
    for si in Sith.objects.all():
        if si.get_count_hands() >= count:
            queryset.append(si)
    print(queryset)
    print(request.path)

    return render(request, 'si/siths_count_hands.html', context={'siths': queryset})


def sith_detail(request, slug):
    sith = Sith.objects.get(slug__iexact=slug)
    return render(request, 'si/sith_detail.html', context={'sith': sith})


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



