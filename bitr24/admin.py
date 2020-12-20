from django.contrib import admin

from .models import Messages, Chat, Bitr


class ChatAdmin(admin.ModelAdmin):
    list_display = ('chat_id', 'first_name', 'last_name', 'slug', 'date_chat', 'username', 'lang_code', 'get_bitrs')
    list_display_links = ('chat_id', 'first_name', 'last_name', 'slug', 'username', 'lang_code', 'get_bitrs')
    search_fields = ('chat_id', 'first_name', 'last_name', 'slug', 'date_chat', 'username', 'lang_code')


class BitrAdmin(admin.ModelAdmin):
    list_display = ('bx24_id', 'bx24_name', 'date_bx24', 'slug', 'expires', 'access_token', 'refresh_token', 'get_chats')
    list_display_links = ('bx24_id', 'bx24_name', 'slug', 'access_token', 'refresh_token')
    search_fields = ('bx24_id', 'bx24_name', 'date_bx24', 'slug', 'expires', 'access_token', 'refresh_token')


class MessagesAdmin(admin.ModelAdmin):
    list_display = ('message', 'date_msg', 'chat')
    list_display_links = ('message', 'date_msg')
    search_fields = ('message', 'date_msg')


admin.site.register(Chat, ChatAdmin)
admin.site.register(Bitr, BitrAdmin)
admin.site.register(Messages, MessagesAdmin)


# admin.site.register(Bind, BindAdmin)

# class BindAdmin(admin.ModelAdmin):
#     list_display = ('chat_id', 'bx24_id', 'message', 'date_bind')
#     list_display_links = ('chat_id', 'bx24_id', 'message', 'date_bind')
#     search_fields = ('chat_id', 'bx24_id', 'message', 'date_bind')



