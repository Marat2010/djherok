from django.contrib import admin

from .models import Planets, Recruits, Sith, Tests


class RecruitsAdmin(admin.ModelAdmin):
    list_display = ('name', 'planet', 'age', 'email')
    list_display_links = ('name', 'planet')
    search_fields = ('name', 'planet', )


class SithAdmin(admin.ModelAdmin):
    list_display = ('name', 'planet')
    list_display_links = ('name', 'planet')
    search_fields = ('name', 'planet', )


class TestsAdmin(admin.ModelAdmin):
    list_display = ('order_code', 'list_questions')
    list_display_links = ('order_code', 'list_questions')
    search_fields = ('order_code', 'list_questions', )


admin.site.register(Planets)
admin.site.register(Recruits, RecruitsAdmin)
# admin.site.register(Sith)
admin.site.register(Sith, SithAdmin)

admin.site.register(Tests, TestsAdmin)




