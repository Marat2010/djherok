from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.views.generic import View
import django.views.decorators.csrf
from bitr24.tg_utils import *
from bitrix24.bitrix24 import Bitrix24
# from django.views.generic import ListView
# from django.views.generic import DetailView


# from .models import Chat, Bitr
from .models import *
# from .utils import ObjectDetailMixin, ObjectCreateMixin, ObjectUpdateMixin, ObjectDeleteMixin
from .utils import *
from .forms import BitrForm, ChatForm, MessageForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q


# Используем пока веб хук(входящий). Код(bx24_code_app) и ключ(bx24_key_app) (Серверное локальное приложение
# без интерфейса в Битрикс24) будем использовать позже (REST по протоколу авторизации OAuth 2.0)
# Используем пока веб хук(входящий) - всё от одного пользователя admin (используем bx24_webhook_in)
# Input webhook in Bitrix24
bx24_webhook_in = os.environ['bx24_webhook_in']
# Bitrix24 server app without UI
bx24_code_app = os.environ['bx24_code_app']
bx24_key_app = os.environ['bx24_key_app']
URL_bx24 = 'https://telebot.bitrix24.ru/rest/1/' + bx24_webhook_in + '/'
file_b24 = './bitr24/bx24.json'
file_bx24_tok = './bitr24/bx24_tok_file.json'
# Использование библиотеки bitrix24-python3-client
# bx24 = Bitrix24('telebot.bitrix24.ru', bx24_code_app, bx24_key_app)  # Создание экземпляра.


def call_method(method):
    pass
#     'tasks.task.list',
#     {filter:{'>STATUS':2, REPLICATE:'N', '::SUBFILTER-PARAMS':{FAVORITE:'Y'}}},
#     function(res){console.log(res.answer.result);}
# );


def send_bx24(method='', **kwargs):     # отправка запроса в битрикс24 (WebHook)
    url = URL_bx24 + method
    print(url)
    r = requests.post(url, json=kwargs)
    r = r.json()  # преобразование ответа в json
    return r


def answ_bx24(msg):     # обработчик запроса от битрих24
    msg = ''
    answer = read_json(file_b24)
    return answer


# @django.views.decorators.csrf.csrf_exempt
# def index(request):
#     if request.method == 'POST':        # if request.content_type == 'application/json':
#         r = request.body.decode('utf-8')
#         r = json.loads(r)
#         write_json(r)   # Запсиь данных чата в файла answer.json.
#         chat_id = r['message']['chat']['id']
#         message = r['message']['text']
#         up_data_chat(chat_id=chat_id, message=message)  # обновление данных в списке словарей чата.
#
#         if message in ['/profile', 'P']:
#             bx24 = Bitrix24('telebot.bitrix24.ru', bx24_code_app, bx24_key_app)
#             bx24.access_token = read_json(file_bx24_tok)['access_token']
#             print(bx24.call_method('user.get'))
#             try:
#                 r_bx24 = bx24.call_method('user.get')
#                 # r_bx24 = bx24.call_method('user.get')['error']
#             except Exception:
#                 refresh_token = read_json(file_bx24_tok)['refresh_token']
#                 # bx24.refresh_token = refresh_token
#                 bx24.refresh_tokens(refresh_token=refresh_token)  # Обновить текущие токены (время жизни 'access_token'-1 час)
#                 r_bx24 = bx24.call_method('user.get')
#
#             print("--Тест в Телеграмм Битрикс24: {}".format(r_bx24))
#             answer = 'Инфо:\n'
#             for i in r_bx24['result']:
#                 answer = answer + '* {}: {} {}\n'.format(i['NAME'], i['PERSONAL_MOBILE'], i['EMAIL'])
#
#         elif message in ['/help', '/start', 'H']:
#             r_bx24 = send_bx24('profile')
#             answer = 'Добро пожаловать в Bitrix24, {}.\n Команды:\n/task или "T" - просмотр задач и их дедлайн\n' \
#                      '/profile или "P" - просмотр своего профиля\n' \
#                      '/L "текст" - сообщение которое разместиться в живой ленте'.format(r_bx24['result']['NAME'])
#         elif message == 'Лиды':
#             # r_bx24 = send_bx24('crm.lead.get', id=1)
#             r_bx24 = send_bx24('crm.lead.list')
#             leads = r_bx24['result']
#             answer = ''
#             for i in leads:
#                 date = str(i['BIRTHDATE'])
#                 date = date.replace('T', ' ')[:16]
#                 answer = answer + '* {}\n ->ДР: {}\n'.format(i['TITLE'], date)
#             answer = 'Лиды получены:\n {}'.format(answer)
#         elif message in ['/task', 'T']:
#             r_bx24 = send_bx24('tasks.task.list')
#             tasks = r_bx24['result']['tasks']
#             answer = ''
#             for i in tasks:
#                 answer = answer + '*' + i['title'] + '\n'
#                 try:
#                     date = str(i['deadline'])
#                     date = date.replace('T', ' ')[:16]
#                 except Exception as ex:
#                     print("---Исключение: {}".format(ex))
#                     date = "не установлен"
#                 answer = answer + " --> Дедлайн: {}\n".format(str(date))
#             answer = '*** Кол-во задач: {} ***\n{}'.format(r_bx24['total'], answer)
#         elif '/L' in message:
#             ll = message.split()
#             if len(ll) > 1:
#                 msg = message[3:]
#                 send_bx24('log.blogpost.add', POST_TITLE='-*** От БОССА ***-', POST_MESSAGE=msg)
#             r_bx24 = send_bx24('log.blogpost.get')
#             r_bx24['result'] = r_bx24['result'][:7]  # уменьшение кол-ва сообщ до 7
#             msgs = ''
#             for i in r_bx24['result']:
#                 msgs += "{}: {}\n".format(i['DATE_PUBLISH'][11:16], i['DETAIL_TEXT'])
#             print(msgs)
#             answer = '-** Последние сообщения: **-\n*' + msgs
#         else:
#             r_bx24 = send_bx24('profile')
#             answer = 'Что именно хотели, {} {}?'.format(r_bx24['result']['NAME'], r_bx24['result']['LAST_NAME'])
#         write_json(r_bx24, file_b24)  # запись в свой файл - b24.json для дальнейшего анализа
#
#         # answer = answ_bx24(message)
#         print(answer)
#         r = send_message(chat_id, text=answer)
#         return HttpResponse(r, content_type="application/json")
#     else:
#         d = read_json(file_b24)
#         d = json.dumps(d, indent=2, ensure_ascii=False, sort_keys=True)  # print("Вывод:\n" + d)
#
#         data_bot = read_json(file_data_bot)
#         ans_d_bot = ""
#         for i in data_bot:
#             ans_d_bot += 'ID: {:>9}. Вр: {}. Польз: {:>10}. Запросов: {:>4}. Посл: {} - ({}). Яз:{}\n' \
#                          ' ---/ Запросы: {} \---\n'.\
#                 format(i['chat_id'], i['date_msg'], i['username'], i['num_req'],
#                        i['location'][0], i['location'][1], i['lang_code'], i['requests'])
#
#         return HttpResponse("Ответ Bitrix24:\n{}\n Данные чата:\n{}".format
#                             (d, ans_d_bot), content_type="application/json")


# @django.views.decorators.csrf.csrf_exempt
# def tg(request):
#     if request.method == 'POST':        # if request.content_type == 'application/json':
#         r = request.body.decode('utf-8')
#         r = json.loads(r)
#         print('---r---:{}'.format(r))
#         write_json(r)   # Запсиь данных чата в файла answer.json.
#         chat_id = r['message']['chat']['id']
#         first_name = r['message']['chat']['first_name']
#         username = r['message']['chat']['username']
#         message = r['message']['text']
#         chat_tg = {'chat_id': chat_id, 'first_name': first_name, 'username': username}
#         print('--chat_tg--{}:'.format(chat_tg))
#         print('--chat_id--:{}'.format(chat_id))
#         try:
#             chat = Chat.objects.get(chat_id=chat_id)
#
#         #     chat = Chat.objects.get(chat_id=100)
#         #     chat = Chat.objects.get('chat_id' = int(chat_id))
#         #     print('----chat---:'.format(chat))
#         except Exception:
#
#             chat.chat_id = chat_id
#         chat.mmessage.message=message
#         chat.first_name = first_name
#         chat.username = username
#         # chat.objects['messages'] = message
#         chat.message = message
#         # message.message = message
#         # chat.messages = message
#         chat.save()
#
#
#         # print('---chat---{}--msg----{}'.format(chat, message))
#         answer = '-Все хорошо!!!-'
#         r = send_message(chat_id, text=answer)
#         return HttpResponse(r, content_type="application/json")
#     # def get(self, request, slug):
#     #     bitr = Bitr.objects.get(slug__iexact=slug)
#     #     bound_form = BitrForm(instance=bitr)
#     #     return render(request, 'bitr24/bitr_update_form.html', context={'form': bound_form, 'bitr': bitr})
#     #
#     # def post(self, request, slug):
#     #     bitr = Bitr.objects.get(slug__iexact=slug)
#     #     bound_form = BitrForm(request.POST, instance=bitr)
#     #
#     #     if bound_form.is_valid():
#     #         new_tag = bound_form.save()
#     #         return redirect(new_tag)
#     #     return render(request, 'bitr24/bitr_update_form.html', context={'form': bound_form, 'bitr': bitr})
#     else:
#         return HttpResponse('<h1>qwe QWE Редирект</h1>')
#
#     # bitrs = Bitr.objects.all()
#     # return render(request, 'bitr24/bitrs_list.html', context={'bitrs': bitrs})


# class Tg(View):
#     model = Chat
#     model_form = ChatForm
#     template = 'bitr24/chat_update_form.html'
#     # raise_exception = True
#     chat_id = 300
#     slug = model.objects.get(chat_id=chat_id)
#     slug = slug.slug
#
#     def get(self, request, slug='vasya-1579115331'):
#         obj = self.model.objects.get(slug__iexact=slug)
#         bound_form = self.model_form(instance=obj)
#         return render(request, self.template, context={'form': bound_form, self.model.__name__.lower(): obj})
#
#     def post(self, request, slug):
#         obj = self.model.objects.get(slug__iexact=slug)
#         bound_form = self.model_form(request.POST, instance=obj)
#
#         if bound_form.is_valid():
#             new_obj = bound_form.save()
#             return redirect(new_obj)
#         return render(request, self.template, context={'form': bound_form, self.model.__name__.lower(): obj})


def chats_list(request):
    search_query = request.GET.get('search', '')

    if search_query:
        chats = Chat.objects.filter(Q(first_name__contains=search_query) | Q(username__contains=search_query))
    else:
        chats = Chat.objects.all()

    paginator = Paginator(chats, 5)

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


def auth(request):
    if request.method == 'POST':        # if request.content_type == 'application/json':
        r = request.body.decode('utf-8')
        r = json.loads(r)
        write_json(r)   # Запсиь данных чата в файла answer.json.
        code_id = r['code']

        print("--- Значение POST r: {}".format(r))
        r_bx24 = '--POST запрос'
        # r = json.loads(r)
        # write_json(r)   # Запсиь данных чата в файла answer.json.
    else:
        # url_tok = 'https://telebot.bitrix24.ru/oauth/authorize/?client_id={}&response_type=code'.format(bx24_code_app)
        # url_tok - URL для запроса авторизации пользователем, после 'удачи' которого получим 'code'
        r = request.GET     # получение словаря от битрикс24 после авторизации пользователем
        try:
            code_id = request.GET['code']   # получение 'code'-первый автор.код, для второго шага OAuth-авторизации
            # Использование библиотеки bitrix24-python3-client
            bx24 = Bitrix24('telebot.bitrix24.ru', bx24_code_app, bx24_key_app)  # Создание экземпляра.

            bx24_tokens = bx24.request_tokens(code_id)  # Запрос токенов для взаимодействия с API Битрикс24
            write_json(bx24_tokens, file_bx24_tok)      # запись в файл
            # dict_tokens = bx24.get_tokens()         # Проверить токены или были ли заменены старые токены
            # bx24.refresh_token()        # Обновить текущие токены (время жизни 'access_token'-1 час)
        except Exception as e:
            print('--Ошибка: {}'.format(e))
            url_tok = 'https://telebot.bitrix24.ru/oauth/authorize/?client_id={}' \
                      '&response_type=code'.format(bx24_code_app)
            url_tok = '<a href="{}">Переход для авторизации на Bitrix24</a>'.format(url_tok)
            date_msg = read_json(file_bx24_tok)['expires']
            date_msg = datetime.datetime.fromtimestamp(int(date_msg)).strftime('%H:%M:%S %d-%m-%Y')

            r_bx24 = "- Авторизуйтесь пож-та: <br>\n{} <br>\n Дата действия до: {}".format(url_tok, date_msg)
        else:
            # r_bx24 = bx24.call_method('user.get', {'ID': 1})
            r_bx24 = bx24.call_method('user.get')
        print("--Тест запроса в Битрикс24: {}".format(r_bx24))
        print("++ : {} ++".format(r))

    return HttpResponse("Ответ Bitrix24:\n{}".format(r_bx24))


# https://dd31cddc.ngrok.io
# https://7d55509d.ngrok.io
# https://api.telegram.org/bot1016865412:AAECUp6v6T6tNdSLxbfR0M2BuU90Yy4R-gQ/setWebhook?url=https://dd31cddc.ngrok.io/bitr24/tg/
# deleteWebhook     getWebhookInfo  setWebhook


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
# url_tok = 'https://telebot.bitrix24.ru/oauth/authorize/?client_id={}&response_type=code'.format(bx24_code_app)
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
