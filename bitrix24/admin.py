from django.contrib import admin

from .models import Messages, Chats


class MessagesAdmin(admin.ModelAdmin):
    list_display = ('message', 'date_msg')
    list_display_links = ('message', 'date_msg')
    search_fields = ('message', 'date_msg', )


class ChatsAdmin(admin.ModelAdmin):
    list_display = ('chat_id', 'first_name', 'username', 'message', 'lang_code')
    list_display_links = ('chat_id', 'username', 'message')
    search_fields = ('chat_id', 'username', 'message', )


admin.site.register(Messages, MessagesAdmin)
admin.site.register(Chats, ChatsAdmin)


