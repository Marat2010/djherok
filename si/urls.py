from django.urls import path
# from .views import index, choice, by_planet, RecruitsCreateView
from .views import index, RecruitCreateView, RecruitQuestions, recruits_list, siths_list, sith_authorization, task_view
from .views import sith_detail, recruit_detail, siths_count_hands, RecruitQuestionsView

urlpatterns = [
    path('', index, name='index'),
    path('recruit_create/', RecruitCreateView.as_view(), name='recruit_create_url'),

    path('recruit/<str:slug>/questions/', RecruitQuestions.as_view(), name='recruit_questions_url'),

    path('recruit_questions/', RecruitQuestionsView.as_view(), name='recruit_questions_url'),

    path('sith_authorization/', sith_authorization, name='sith_authorization_url'),


    path('siths/', siths_list, name='siths_list_url'),
    # path('siths/', siths_list, name='siths_count_hands_url'),
    path('siths/count_hands_shadow/<int:count>/', siths_count_hands, name='siths_count_hands_url'),
    path('sith/<str:slug>/', sith_detail, name='sith_detail_url'),
    path('recruits/', recruits_list, name='recruits_list_url'),
    path('recruit/<str:slug>/', recruit_detail, name='recruit_detail_url'),
    path('task/', task_view, name='task_view_url'),

    # path('add/', RecruitsCreateView.as_view(), name='add'),
    # path('<int:planet_id>/', by_planet, name='by_planet'),
    # path('', index, name='index'),
]

