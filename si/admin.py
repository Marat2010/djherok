from django.contrib import admin

from .models import Planet, Order, Sith, Recruit, Test, Answer, RecruitAnswer
from .forms import TestForm


class PlanetAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'get_siths', 'get_recruits')
    list_display_links = ('name', 'slug')
    search_fields = ('name', 'slug')


class OrderAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'get_siths')
    list_display_links = ('name', 'code')
    search_fields = ('name', 'code')


class SithAdmin(admin.ModelAdmin):
    list_display = ('name', 'planet', 'order', 'slug', 'get_recruits')
    list_display_links = ('name', 'planet', 'order')
    search_fields = ('name', 'planet__name', 'order__name')
    # search_fields = ('name', 'planet', 'order', 'slug')


class RecruitAdmin(admin.ModelAdmin):
    list_display = ('name', 'planet', 'age', 'email', 'slug', 'sith')
    list_display_links = ('name', 'planet', 'age', 'email', 'sith')
    search_fields = ('name', 'planet__name', 'age', 'email', 'sith__name',)
    # search_fields = ('name', 'planet', 'age', 'email', 'slug', 'sith')


class TestAdmin(admin.ModelAdmin):
    list_display = ('order', 'question', 'slug', 'get_answers', 'right_answ')
    # list_display = ('order', 'question', 'slug', 'answers', 'right_answ')
    list_display_links = ('order', 'question', 'right_answ')
    search_fields = ('question',)

    autocomplete_fields = ('answers', )
    # autocomplete_fields = ('right_answ', 'answers', )

    form = TestForm     # Для выбора прав.ответа из сущестующих

    def formfield_for_foreignkey(self, db_field, request, **kwargs):  # Для выбора прав.ответа из сущестующих
        if db_field.name == 'right_answ':
            try:
                object_id = request.resolver_match.kwargs['object_id']
                # # Второй способ поиска объекта модели:
                # object_id = request.META['PATH_INFO'].rstrip('/').split('/')[-2]
                kwargs["queryset"] = Answer.objects.filter(tests=object_id)
            except KeyError as e:
                print('--Ошибка поиска object-id, нет объекта (Новый объект). )', e)
                # kwargs["queryset"] = Answer.objects.none()
                kwargs["queryset"] = Answer.objects.filter(pk=1)
        return super().formfield_for_choice_field(db_field, request, **kwargs)


class AnswerAdmin(admin.ModelAdmin):
    list_display = ('answer',)
    list_display_links = ('answer',)
    search_fields = ('answer',)


class RecruitAnswerAdmin(admin.ModelAdmin):
    list_display = ('recruit', 'question', 'answer',)
    list_display_links = ('recruit', 'question',)
    search_fields = ('recruit__name', 'question__question',)
    # search_fields = ('recruit', 'question',)


admin.site.register(Planet, PlanetAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Sith, SithAdmin)
admin.site.register(Recruit, RecruitAdmin)
admin.site.register(Test, TestAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(RecruitAnswer, RecruitAnswerAdmin)


# from django.core.exceptions import ValidationError
# -------------------------------------------------
# def save_model(self, request, obj, form, change):
#     form.save()
#     answer = []
#     if obj.answers.all():
#         answer += [ans.answer for ans in obj.answers.all()]
#     print('---Save_model', answer)
#     if obj.right_answ not in obj.answers.all():
#         raise ValidationError('Выберите правильный ответ из предоставленных ответов!!!')
#     form.cleaned_data['answer'] = answer
#     super(TestAdmin, self).save_model(request, obj, form, change)
#--------------------------------------------
# from django.core.exceptions import ValidationError
# from django import forms
# from .forms import MyTestAdminForm

# form = MyTestAdminForm(forms.ModelForm)
# def clean_right_answ(self):
#     # do something that validates your data
#     object_id = request.resolver_match.kwargs['object_id']
#     if object_id.right_answ not in object_id.answers.all():
#         raise ValidationError('Выберите правильный ответ из предоставленных ответов!!!')
#     return self.cleaned_data["name"]

#--------------------------------------
# kwargs['right_answ'] = Test.answers.all()
# print('---KWARGS: {}{}\n gj----:{}'.format(kwargs,  request.__dict__, self.model.__dict__))
# print('---KWARGS: {}\n gj----:{}\n'.format(kwargs, self.get_queryset(request)))

# def right_answ(self, obj):
#     return obj.right_answ
# right_answ.empty_value_display = 'Выберите из ответов'

# def formfield_for_manytomany(self, db_field, request, **kwargs):
