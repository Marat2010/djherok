from django.contrib import admin

from .models import Messages, Chat, Bitr


class ChatsAdmin(admin.ModelAdmin):
    list_display = ('chat_id', 'first_name', 'slug', 'username', 'lang_code')
    list_display_links = ('chat_id', 'first_name', 'slug', 'username', 'lang_code')
    search_fields = ('chat_id', 'first_name', 'slug', 'username', 'lang_code', 'bitrs', )


class BitrAdmin(admin.ModelAdmin):
    list_display = ('bx24_id', 'bx24_name', 'access_token', 'refresh_token', 'chats')
    list_display_links = ('bx24_id', 'bx24_name', 'access_token', 'refresh_token', 'chats')
    search_fields = ('bx24_id', 'bx24_name', 'access_token', 'refresh_token', 'chats', )


class MessagesAdmin(admin.ModelAdmin):
    # list_display = ('message', 'date_msg', 'chatM')
    list_display = ('message', 'date_msg')
    list_display_links = ('message', 'date_msg')
    search_fields = ('message', 'date_msg', )


admin.site.register(Chat, ChatsAdmin)
admin.site.register(Bitr, BitrAdmin)
admin.site.register(Messages, MessagesAdmin)



