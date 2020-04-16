from django.http import HttpResponse
from django.shortcuts import redirect


def redirect_to(request):
    # return redirect('/bitr24/tg/')
    # return redirect('/bitr24/bitr/')
    # return redirect('chats_list_url', permanent=True) # ответ: 301 -не ставить True (сложно убрать)

    return redirect('/si/')                   # ответ: 302 - по умолч. False
    # return redirect('chats_list_url')                   # ответ: 302 - по умолч. False

    # return redirect('http://127.0.0.1:8000/bitr24/chat/', permanent=True)


