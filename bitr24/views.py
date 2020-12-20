# from django.views.generic import ListView
# from django.views.generic import DetailView
# from .utils import ObjectDetailMixin, ObjectCreateMixin, ObjectUpdateMixin, ObjectDeleteMixin
# from .utils import *
# import datetime, timedelta
# from datetime import datetime, timedelta
# from django.utils import timezone
# from pytz import timezone
# from django.contrib import messages

# from django.shortcuts import redirect
# from django.urls import reverse
# from django.shortcuts import get_object_or_404
# from django.views.decorators.csrf import csrf_exempt

from django.http import HttpResponse
from django.shortcuts import render
from .models import *
from django.views.generic import View
import json
from .utils import ObjectDetailMixin, ObjectCreateMixin, ObjectUpdateMixin, ObjectDeleteMixin
from .forms import BitrForm, ChatForm, MessageForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q
from bitr24.tg_utils import send_message, rw_chat, write_json, Bx24, portal, convert_time

file_bx24_tok = './bitr24/bx24_tok_file.json'  # Файл для временного хранения словаря токенов от Битрикс24


class Tg(View):
    model = Chat
    template = 'bitr24/tg.html'

    def get(self, request):
        try:
            code_id = request.GET['code']   # получение 'code'-первый автор.код, для второго шага OAuth-авторизации
        except KeyError:                    # except Exception as code:
            chat = rw_chat()  # Просмотр Кто последний входил
            print('== GET без (code): ', chat.chat_id, chat.first_name)
            return render(request, self.template, context={self.model.__name__.lower(): chat})
        else:
            bx24 = Bx24()  # создаем экз.
            bx24_dict = bx24.request_tokens(code_id)  # Запрос токенов для взаимодействия с API Б24 (=полный словарь)
            write_json(bx24_dict, file_bx24_tok)  # запись в файл для врем.хранения словаря токенов от Битрикс24
            print('==** Из словаря EXPIRES: bx24_dict[expires]: {}'.format(bx24_dict['expires']))
            bx24_name = bx24.call_method('user.current')['result']['NAME']  # Вытаскиваем имя
            expires = convert_time(bx24_dict['expires'])  # преобразует время из 1584146509 в datetime.datetime(2020, ..
            print('==Время после преобразования: {}'.format(expires))
            bitr = Bitr.objects.update_or_create(bx24_id=bx24.user_id,      # Заносим в базу
                                                 defaults={'bx24_name': bx24_name, 'access_token': bx24.access_token,
                                                           'refresh_token': bx24.refresh_token, 'expires': expires})[0]
            bind_code = '/AUTH-' + bitr.access_token[:3] + str(bitr.bx24_id)  # формируем код привязки
            print('== Код привязки : ', bind_code)
            ss = 'Вернитесь в телеграм: <a href="tg://t.me/Bitr24_bot">К Боту</a>'
        return HttpResponse('Ответ Bitrix24: Успешно<br>\nСкопируйте код "{}" и отправьте его в боте<br>\n{}\n'.
                            format(bind_code, ss))

    def post(self, request):
        r = json.loads(request.body.decode('utf-8'))
        write_json(r)           # Запсиь данных чата в файла answer.json.
        chat = rw_chat(True)    # Запсиь данных чата в БД.
        msg = portal(chat)      # Получение ответа от портала и отправка в чат
        send_message(chat.chat_id, msg, 'html')
        return render(request, self.template, context={self.model.__name__.lower(): chat})


def chats_list(request):
    search_query = request.GET.get('search', '')

    if search_query:
        chats = Chat.objects.filter(Q(first_name__contains=search_query) | Q(username__contains=search_query))
    else:
        chats = Chat.objects.all()

    paginator = Paginator(chats, 3)

    page_number = request.GET.get('page', 1)
    page = paginator.get_page(page_number)

    is_paginated = page.has_other_pages()

    if page.has_previous():
        prev_url = '?page={}'.format(page.previous_page_number())
    else:
        prev_url = ''

    if page.has_next():
        next_url = '?page={}'.format(page.next_page_number())
    else:
        next_url = ''

    context = {
        'page_object': page,
        'is_paginated': is_paginated,
        'prev_url': prev_url,
        'next_url': next_url
    }

    return render(request, 'bitr24/index.html', context=context)


class ChatDetail(ObjectDetailMixin, View):
    model = Chat
    template = 'bitr24/chat_detail.html'


class ChatCreate(LoginRequiredMixin, ObjectCreateMixin, View):
    model_form = ChatForm
    template = 'bitr24/chat_create_form.html'
    raise_exception = True


class ChatUpdate(LoginRequiredMixin, ObjectUpdateMixin, View):
    model = Chat
    model_form = ChatForm
    template = 'bitr24/chat_update_form.html'
    raise_exception = True


class ChatDelete(LoginRequiredMixin, ObjectDeleteMixin, View):
    model = Chat
    template = 'bitr24/chat_delete_form.html'
    redirect_url = 'chats_list_url'
    raise_exception = True


def bitrs_list(request):
    bitrs = Bitr.objects.all()
    return render(request, 'bitr24/bitrs_list.html', context={'bitrs': bitrs})


class BitrDetail(ObjectDetailMixin, View):
    model = Bitr
    template = 'bitr24/bitr_detail.html'


class BitrCreate(LoginRequiredMixin, ObjectCreateMixin, View):
    model_form = BitrForm
    template = 'bitr24/bitr_create.html'
    raise_exception = True


class BitrUpdate(LoginRequiredMixin, ObjectUpdateMixin, View):
    model = Bitr
    model_form = BitrForm
    template = 'bitr24/bitr_update_form.html'
    raise_exception = True


class BitrDelete(LoginRequiredMixin, ObjectDeleteMixin, View):
    model = Bitr
    template = 'bitr24/bitr_delete_form.html'
    redirect_url = 'bitrs_list_url'
    raise_exception = True


# expires = bx24.expires[:19]
# fmt = '%Y-%m-%d %H:%M:%S'
# expires = datetime.strptime(expires, fmt)

# expires = (datetime.now() + timedelta(seconds=3600)).strftime('%H:%M:%S %d-%m-%Y')  # из тек.момента
# expires = datetime.fromtimestamp(bx24_dict['expires']).strftime('%H:%M:%S %d-%m-%Y')  # из словаря
# expires = datetime.fromtimestamp(bx24_dict['expires']).\
#     astimezone(timezone('Europe/Moscow')).strftime('%Y-%m-%d %H:%M:%S')  # из словаря

# fmt = '%Y-%m-%d %H:%M:%S %Z%z'
# expires_no_tz = datetime.fromtimestamp(bx24_dict['expires'])  # datetime.datetime(2020, 3, 14, 1, 48, 29)
# current_tz = timezone.get_current_timezone()  # <DstTzInfo 'Europe/Moscow' LMT+2:30:00 STD>
# expires = current_tz.localize(expires_no_tz)  # datetime.datetime(2020, 3, 14, 1, 48, 29, tzinfo=<DstTzInfo 'Europe/Moscow' MSK+3:00:00 STD>)
# # expires = expires.strftime(fmt)  # '2020-03-14 01:48:29'

# print('== Bitr.ACC: {}\n ==bx24.DICT: {}'.format(bitr.access_token, bx24.__dict__))

# request.session['OAuth'] = 'GET code'
# defaults={'bx24_name': '/code/', 'access_token': bx24.access_token,
# Поиск чата по последнему сообщению (не совсем правильно, в будущем надо продумать, как сделать)
# chat = Messages.objects.first().chat
# print('=== Какой chat: {}, == Какой bitr: {}'.format(chat, bitr))
# bitr.chats.add(chat)         # Привязываем записи в двух таблицах. Или так: chat.bitrs.add(bitr)
# send_message(chat.chat_id, 'Успешно!')    # Отправка сообщения

# bound_form = self.model_form(request.POST, instance=obj)
# if bound_form.is_valid():
#     new_obj = bound_form.save()
#     return redirect(new_obj)
# return render(request, self.template, context={'form': bound_form, self.model.__name__.lower(): obj})

# request.session['OAuth'] = True  # Запоминаем сессию
# request.session['bx24_id'] = bx24.user_id

# Bind.objects.update_or_create(chat_id=chat.chat_id, defaults={'message': chat.messages.first().message, 'bx24_id': bx24.user_id})
# messages.add_message(request, messages.SUCCESS, 'УРААА=========')
# return redirect('https://telebot.bitrix24.ru/oauth/authorize/?client_id=local.5e04004ad5e626.19578281&response_type=code')

# https://552208f0.ngrok.io/bitr24/
# https://0c374e2c.ngrok.io
# https://api.telegram.org/bot1016865412:AAECUp6v6T6tNdSLxbfR0M2BuU90Yy4R-gQ/setWebhook?url=https://552208f0.ngrok.io/bitr24/tg/
# deleteWebhook     getWebhookInfo  setWebhook
# -----------------------------------------------------------------
# def get_chat():
#     data = read_ans()  # print('--* Словарь из answer.json: ', data)
#     data.pop('date_msg')
#     data.pop('message')  # print('--data--:', data)
#
#     chat = Chat.objects.update_or_create(chat_id=data['chat_id'], defaults=data)[0]
#     # chat.messages.create(message=message)
#     return chat

# def post_chat():
#     data = read_ans()  # print('--* Словарь из answer.json: ', data)
#     data.pop('date_msg')
#     message = data.pop('message')  # print('--data--:', data)
#
#     chat = Chat.objects.update_or_create(chat_id=data['chat_id'], defaults=data)[0]
#     chat.messages.create(message=message)
#     return chat
# -------------------------------------------------------

# msg = """ <b>bold</b>, <strong>bold</strong><i>italic</i>, <em>italic</em><u>underline</u>, <ins>underline</ins>
# <s>strikethrough</s>, <strike>strikethrough</strike>, <del>strikethrough</del>
# <b>bold <i>italic bold <s>italic bold strikethrough</s> <u>underline italic bold</u></i> bold</b>
# <a href="https://56d0f980.ngrok.io/bitr24/tg/">Мой URL</a>
# <code>inline fixed-width code</code><pre>pre-formatted fixed-width code block</pre>
# <pre><code class="language-python">pre-formatted fixed-width code block written in the Python
# programming language</code></pre> """

# try:
    #     chat = Chat.objects.get(chat_id=chat_id)
    #     message = r['message']
    #     chat.messages.create(message=message)
    # except Exception:
    #     data = r.copy()
    #     # date_chat = data.pop('date_msg')
    #     data.pop('date_msg')
    #     message = data.pop('message')
    #     print('datatatatat: ', data)
    #     chat = Chat.objects.create(**data)
    #     chat.messages.create(message=message)
    #     print('---msg: ', message)

    # Messages.objects.create(message='Шестое  6-oe soobsh', chat=obj)
    # msg5 = Messages(message='------5-oe soobsh', chat=obj) --- !!!
    # obj.messages.create(message='new 8 soob')

    # def redirect_to(request):
    # return redirect('chats_list_url', permanent=True)
    # return redirect('tg_url', permanent=True)
    # return redirect('/bitr24/chat/')
    # return redirect('http://127.0.0.1:8000/bitr24/chat/', permanent=True)
    #     # return redirect('chats_list_url', permanent=True)
    #     return redirect('bitr24/tg/tg')

    # def get(self, request, slug):
    #     bitr = Bitr.objects.get(slug__iexact=slug)
    #     bound_form = BitrForm(instance=bitr)
    #     return render(request, 'bitr24/bitr_update_form.html', context={'form': bound_form, 'bitr': bitr})
    #
    # def post(self, request, slug):
    #     bitr = Bitr.objects.get(slug__iexact=slug)
    #     bound_form = BitrForm(request.POST, instance=bitr)
    #
    #     if bound_form.is_valid():
    #         new_tag = bound_form.save()
    #         return redirect(new_tag)
    #     return render(request, 'bitr24/bitr_update_form.html', context={'form': bound_form, 'bitr': bitr})

    # def get(self, request, slug):
    #     chat = get_object_or_404(Chats, slug__iexact=slug)
    #     return render(request, 'bitr24/chat_detail.html', context={'chat': chat})

    # def get(self, request, slug):
    #     bitr = get_object_or_404(Bitr, slug__iexact=slug)
    #     return render(request, 'bitr24/bitr_detail.html', context={'bitr': bitr})

    # def bitr_detail(request, slug):
    #     bitr = Bitr.objects.get(slug__iexact=slug)
    #     return render(request, 'bitr24/bitr_detail.html', context={'bitr': bitr})
    # def chat_detail(request, slug):
    #     chat = Chats.objects.get(slug__iexact=slug)
    #     return render(request, 'bitr24/chat_detail.html', context={'chat': chat})

    # def get(self, request):
    #     form = BitrForm()
    #     return render(request, 'bitr24/bitr_create.html', context={'form': form})
    #
    # def post(self, request):
    #     bound_form = BitrForm(request.POST)
    #     if bound_form.is_valid():
    #         new_bitr = bound_form.save()
    #         return redirect(new_bitr)
    #     return render(request, 'bitr24/bitr_create.html', context={'form': bound_form})

    # def get(self, request):
    #     form = ChatForm()
    #     return render(request, 'bitr24/chat_create_form.html', context={'form': form})
    #
    # def post(self, request):
    #     bound_form = ChatForm(request.POST)
    #     if bound_form.is_valid():
    #         new_chat = bound_form.save()
    #         return redirect(new_chat)
    #     return render(request, 'bitr24/chat_create_form.html', context={'form': bound_form})
# class BitrDelete(ObjectDeleteMixin, View):
#     def get(self, request, slug):
#         bitr = Bitr.objects.get(slug__iexact=slug)
#         return render(request, 'bitr24/bitr_delete_form.html', context={'bitr': bitr})
#
#     def post(self, request, slug):
#         bitr = Bitr.objects.get(slug__iexact=slug)
#         bitr.delete()
#         return redirect(reverse('bitrs_list_url'))

# class TbxView(View):
#     template_name = 'bitr24/base.html'
#
#     def get(self, request, *args, **kwargs):
#         chats = Chats.objects.all()
#         context = {
#             'chats': chats
#         }
#         return render(request, self.template_name, context)

# class TbxListViev(ListView):
#     model = Tbx
#     template_name = 'bitr24/all_tbx.html'
#     queryset = Tbx.objects.all()
#     context_object_name = 'tbx'
#
#
# class TbxDetailView(DetailView):
#     model = Tbx
#     template_name = 'bitr24/tbx_detail.html'
#     slug_url_kwarg = 'tbx_slug'
#     context_object_name = 'tbx_object'

    # def get_context_data(self, **kwargs):
    #     context = {}
    #     context

    # def get_queryset(self, *args, **kwargs):
    #     qs = super(TbxListViev, self).get_queryset(*args, **kwargs)
    #     return qs.filter(messages='ewed')

    # # def get_context_data(self, *, object_list=None, **kwargs):
    # def get_context_data(self, *args, **kwargs):
    #     context = {}
    #     # context['tbx'] = self.model.objects.all()
    #     context['tbx'] = self.model.objects.all()
    #     return context
# rb = bx24.request_tokens('3109115e004336860043365600000009000003db0ab199cbdddcf4ba82e6d2c59162a9')
# rb
# Out[9]:
# {'access_token': '4117115e0043368600433656000000090000039e6792be2545529a5c67b49fc57d2eeb',
#  'expires': 1578178369,
#  'expires_in': 3600,
#  'scope': 'app',
#  'domain': 'telebot.bitrix24.ru',
#  'server_endpoint': 'https://oauth.bitrix.info/rest/',
#  'status': 'L',
#  'client_endpoint': 'https://telebot.bitrix24.ru/rest/',
#  'member_id': '9c3d69f3a517c02b62fe8efa97972add',
#  'user_id': 9,
#  'refresh_token': '3196385e004336860043365600000009000003fa0de52a0b5c1d92b5aa1798f8dfe151'}
# bx24.get_tokens()
# Out[10]:
# {'access_token': '4117115e0043368600433656000000090000039e6792be2545529a5c67b49fc57d2eeb',
#  'refresh_token': '3196385e004336860043365600000009000003fa0de52a0b5c1d92b5aa1798f8dfe151'}
# url_tok = 'https://telebot.bitrix24.ru/oauth/authorize/?client_id={}&response_type=code'.format(client_id)
# https://telebot.bitrix24.ru/oauth/authorize/?client_id=local.5e04004ad5e626.19578281&response_type=code

# https://auth2.bitrix24.net/oauth/authorize/?user_lang=ru
#   &client_id=b24.5e0366727bb993.76668540&
#   redirect_uri=https%3A%2F%2Ftelebot.bitrix24.ru%2Foauth%2Fauthorize%2F%3F
#   auth_service_id%3DBitrix24Net%26
#   oauth_proxy_params%3DY2xpZW50X2lkPWxvY2FsLjVlMDQwMDRhZDVlNjI2LjE5NTc4MjgxJnJlc3BvbnNlX3R5cGU9Y29kZQ%253D%253D
#   &scope=auth,profile
#   &response_type=code
#   &mode=page&state=site_id%3Ds1%26backurl%3D%252Foauth%252F
#   authorize%252F%253F
#   check_key%253D84ef602fd5f52f0d7c6325a9509ea3bf%2526
#   client_id%253Dlocal.5e04004ad5e626.19578281%2526
#   response_type%253Dcode%26mode%3Dpage

# url_auth = https://eff26c65.ngrok.io/bitr24/?
#     code=68e00d5e00433686004336560000000100000389f69ef15efe7df1290e56b9a2bc4294
#     &state=
#     &domain=telebot.bitrix24.ru
#     &member_id=9c3d69f3a517c02b62fe8efa97972 add
#     &scope=im%2Ctask
#     &server_domain=oauth.bitrix.info
# https://1bf8ae84.ngrok.io/bitr24/?
#      code=20be0f5e004336860043365600000009000003e8b38744e1292eb28ec7220e315d9773
#      &state=
#      &domain=telebot.bitrix24.ru
#      &member_id=9c3d69f3a517c02b62fe8efa97972   add
#      &scope=im%2Clog%2Ctask
#      &server_domain=oauth.bitrix.info

# https://auth2.bitrix24.net/oauth/authorize/?user_lang=ru
#   &client_id=b24.5e0366727bb993.76668540
#   &redirect_uri=https%3A%2F%2Ftelebot.bitrix24.ru%2Foauth%2Fauthorize%2F%3Fauth_service_id%3DBitrix24Net%26oauth_proxy_params%3DY2xpZW50X2lkPWxvY2FsLjVlMDQwMDRhZDVlNjI2LjE5NTc4MjgxJnJlc3BvbnNlX3R5cGU9Y29kZQ%253D%253D
#   &scope=auth,profile&response_type=code&mode=page
#   &state=site_id%3Ds1%26backurl%3D%252Foauth%252Fauthorize%252F%253F
#   check_key%253Dbd60a988da479ab43e49fe3208603fa4%2526client_id%253D
#   local.5e04004ad5e626.19578281%2526
#   response_type%253Dcode%26mode%3Dpage

# https://f99e84fd.ngrok.io/bitr24/
# https://80e2fbd3.ngrok.io
# https://api.telegram.org/bot1016865412:AAECUp6v6T6tNdSLxbfR0M2BuU90Yy4R-gQ/setWebhook?url=https://80e2fbd3.ngrok.io/

# bx24 = Bitrix24('your-domain.bitr24.com' ,  'your.client.id' ,  'your_client_secret' )
# bx24  =  Bitrix24 ( 'your-domain.bitr24.com' ,  'your.client.id' ,  'your_client_secret' )
# Мои приложения(серверное без UI)     - https://djherok.herokuapp.com/bitrix/
# назв: Тест без UI		(Чат и уведомления (im), Задачи (task))
# Только API: Да
# Код приложения: local.5e04004ad5e626.19578281
# Ключ приложения: 0mIMVUBB7hfhWwQBLD8cIIEiVPzKjS7Mlkww7VCAyTnlyU3kne
# 		1798efe41b0c132c1ea756beae819560
# 		70a32986f1bf204dec4567147ca6a2af

# help - Описание
# task - просмотр задач
# profile - просмотр своего профиля

# https://telebot.bitrix24.ru/rest/1/jwi2dohttz51o1pk/log.blogpost.add
# https://telebot.bitrix24.ru/rest/1/jwi2dohttz51o1pk/log.blogpost.add?POST_TITLE=-** Заголовок **-&POST_MESSAGE=---Тело ообщения ---
# https://telebot.bitrix24.ru/rest/1/jwi2dohttz51o1pk/tasks.task.list
# https: // telebot.bitr24.ru / rest / 1 / jwi2dohttz51o1pk / tasks.task.list

        # data_bot = json.dumps(data_bot, ensure_ascii=False, sort_keys=True)

# https://djherok.herokuapp.com/bitrix24/
# https://api.telegram.org/bot919974881:AAHwfCsrATbNx9fxjhbSxzacw5Ip-G-aTKE/setWebhook?url=https://djherok.herokuapp.com/bitrix24/

# https://3f63a3f1.ngrok.io/bitrix24/
# https://api.telegram.org/bot919974881:AAHwfCsrATbNx9fxjhbSxzacw5Ip-G-aTKE/setWebhook?url=https://3f63a3f1.ngrok.io/bitrix24/
#  https://api.telegram.org/bot919974881:AAHwfCsrATbNx9fxjhbSxzacw5Ip-G-aTKE/getWebhookInfo
# deleteWebhook     getWebhookInfo  setWebhook

# Вместе с кодом будет представлен образец URL, который нужно использовать при отправке данных из сторонней системы
#  в Битрикс24:
# https://********.bitr24.ru/rest/1/83te1pjdphsa9u15/profile/
# где:
# ******** - имя вашего портала;
# /rest/ - указание системе на то, что данный адрес относится в вебхукам;
# /1/ - идентификатор пользователя, создавшего вебхук. Под правами этого пользователя будет работать этот вебхук.
# /83te1pjdphsa9u15/ - секретный код;
# /profile/ - метод REST, который вы хотите выполнить, обращаясь к вебхуку. Разработчик должен сам подобрать метод
#  из REST API в зависимости от целей создания вебхука.
