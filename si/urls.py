from django.urls import path
from .views import index, recruits_list, siths_list, siths_count_hands, RecruitCreate, RecruitDetail, RecruitUpdate
from .views import SithCreate, SithDetail, SithUpdate
from .views import task_view, RecruitQuestions,  sith_authorization, siths_planet, siths_order,\
    recruits_planet, recruits_order
# from .views import recruit_create

urlpatterns = [
    path('', index, name='index'),
    path('recruits/', recruits_list, name='recruits_list_url'),
    path('siths/', siths_list, name='siths_list_url'),
    path('siths/count_hands_shadow/<int:count_hands>/', siths_count_hands, name='siths_count_hands_url'),


    path('recruit/create/', RecruitCreate.as_view(), name='recruit_create_url'),
    # path('recruit/create/', recruit_create, name='recruit_create_url'),


    path('recruit/<str:slug>/', RecruitDetail.as_view(), name='recruit_detail_url'),
    path('recruit/<str:slug>/update/', RecruitUpdate.as_view(), name='recruit_update_url'),

    path('sith/create/', SithCreate.as_view(), name='sith_create_url'),
    path('sith/<str:slug>/', SithDetail.as_view(), name='sith_detail_url'),
    path('sith/<str:slug>/update/', SithUpdate.as_view(), name='sith_update_url'),

    path('siths/planet/<str:slug>/', siths_planet, name='siths_planet_url'),
    path('siths/order/<str:slug>/', siths_order, name='siths_order_url'),
    path('recruit/planet/<str:slug>/', recruits_planet, name='recruits_planet_url'),
    path('recruit/order/<str:slug>/', recruits_order, name='recruits_order_url'),



    path('recruit/<str:slug>/questions/', RecruitQuestions.as_view(), name='recruit_questions_url'),




    path('sith_authorization/', sith_authorization, name='sith_authorization_url'),
    path('task/', task_view, name='task_view_url'),
]


# path('recruit_create/', RecruitCreateView.as_view(), name='recruit_create_url'),
# path('recruit_questions/', RecruitQuestionsView.as_view(), name='recruit_questions_url'),
# path('sith/<str:slug>/', sith_detail, name='sith_detail_url'),
# path('add/', RecruitsCreateView.as_view(), name='add'),
# path('<int:planet_id>/', by_planet, name='by_planet'),
# path('', index, name='index'),
# path('recruit/<str:slug>/', recruit_detail, name='recruit_detail_url'),

