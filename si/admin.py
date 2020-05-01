from django.contrib import admin

from .models import Planet, Order, Sith, Recruit, Test, Answer


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
    search_fields = ('name', 'planet', 'order', 'slug')


class RecruitAdmin(admin.ModelAdmin):
    list_display = ('name', 'planet', 'age', 'email', 'slug', 'answers', 'sith')
    list_display_links = ('name', 'planet', 'age', 'email', 'answers', 'sith')
    search_fields = ('name', 'planet', 'age', 'email', 'slug', 'answers', 'sith')


class TestAdmin(admin.ModelAdmin):
    list_display = ('order', 'question', 'slug', 'get_answers')
    list_display_links = ('order', 'question')
    search_fields = ('order', 'question')


class AnswerAdmin(admin.ModelAdmin):
    list_display = ('answer',)
    list_display_links = ('answer',)
    search_fields = ('answer',)


admin.site.register(Planet, PlanetAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Sith, SithAdmin)
admin.site.register(Recruit, RecruitAdmin)
admin.site.register(Test, TestAdmin)
admin.site.register(Answer, AnswerAdmin)

