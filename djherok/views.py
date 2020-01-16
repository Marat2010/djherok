from django.http import HttpResponse
from django.shortcuts import redirect


def redirect_bitr24(request):
    return redirect('chats_list_url', permanent=True)


