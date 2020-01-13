from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.views.generic import View
import django.views.decorators.csrf
from bitr24.tg_utils import *
from bitrix24.bitrix24 import Bitrix24
# from django.views.generic import ListView
# from django.views.generic import DetailView


from .models import Chat, Bitr
from .utils import ObjectDetailMixin


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


@django.views.decorators.csrf.csrf_exempt
def index(request):
    if request.method == 'POST':        # if request.content_type == 'application/json':
        r = request.body.decode('utf-8')
        r = json.loads(r)
        write_json(r)   # Запсиь данных чата в файла answer.json.
        chat_id = r['message']['chat']['id']
        message = r['message']['text']
        up_data_chat(chat_id=chat_id, message=message)  # обновление данных в списке словарей чата.

        if message in ['/profile', 'P']:
            bx24 = Bitrix24('telebot.bitrix24.ru', bx24_code_app, bx24_key_app)
            bx24.access_token = read_json(file_bx24_tok)['access_token']
            print(bx24.call_method('user.get'))
            try:
                r_bx24 = bx24.call_method('user.get')
                # r_bx24 = bx24.call_method('user.get')['error']
            except Exception:
                refresh_token = read_json(file_bx24_tok)['refresh_token']
                # bx24.refresh_token = refresh_token
                bx24.refresh_tokens(refresh_token=refresh_token)  # Обновить текущие токены (время жизни 'access_token'-1 час)
                r_bx24 = bx24.call_method('user.get')

            print("--Тест в Телеграмм Битрикс24: {}".format(r_bx24))
            answer = 'Инфо:\n'
            for i in r_bx24['result']:
                answer = answer + '* {}: {} {}\n'.format(i['NAME'], i['PERSONAL_MOBILE'], i['EMAIL'])

        elif message in ['/help', '/start', 'H']:
            r_bx24 = send_bx24('profile')
            answer = 'Добро пожаловать в Bitrix24, {}.\n Команды:\n/task или "T" - просмотр задач и их дедлайн\n' \
                     '/profile или "P" - просмотр своего профиля\n' \
                     '/L "текст" - сообщение которое разместиться в живой ленте'.format(r_bx24['result']['NAME'])
        elif message == 'Лиды':
            # r_bx24 = send_bx24('crm.lead.get', id=1)
            r_bx24 = send_bx24('crm.lead.list')
            leads = r_bx24['result']
            answer = ''
            for i in leads:
                date = str(i['BIRTHDATE'])
                date = date.replace('T', ' ')[:16]
                answer = answer + '* {}\n ->ДР: {}\n'.format(i['TITLE'], date)
            answer = 'Лиды получены:\n {}'.format(answer)
        elif message in ['/task', 'T']:
            r_bx24 = send_bx24('tasks.task.list')
            tasks = r_bx24['result']['tasks']
            answer = ''
            for i in tasks:
                answer = answer + '*' + i['title'] + '\n'
                try:
                    date = str(i['deadline'])
                    date = date.replace('T', ' ')[:16]
                except Exception as ex:
                    print("---Исключение: {}".format(ex))
                    date = "не установлен"
                answer = answer + " --> Дедлайн: {}\n".format(str(date))
            answer = '*** Кол-во задач: {} ***\n{}'.format(r_bx24['total'], answer)
        elif '/L' in message:
            ll = message.split()
            if len(ll) > 1:
                msg = message[3:]
                send_bx24('log.blogpost.add', POST_TITLE='-*** От БОССА ***-', POST_MESSAGE=msg)
            r_bx24 = send_bx24('log.blogpost.get')
            r_bx24['result'] = r_bx24['result'][:7]  # уменьшение кол-ва сообщ до 7
            msgs = ''
            for i in r_bx24['result']:
                msgs += "{}: {}\n".format(i['DATE_PUBLISH'][11:16], i['DETAIL_TEXT'])
            print(msgs)
            answer = '-** Последние сообщения: **-\n*' + msgs
        else:
            r_bx24 = send_bx24('profile')
            answer = 'Что именно хотели, {} {}?'.format(r_bx24['result']['NAME'], r_bx24['result']['LAST_NAME'])
        write_json(r_bx24, file_b24)  # запись в свой файл - b24.json для дальнейшего анализа

        # answer = answ_bx24(message)
        print(answer)
        r = send_message(chat_id, text=answer)
        return HttpResponse(r, content_type="application/json")
    else:
        d = read_json(file_b24)
        d = json.dumps(d, indent=2, ensure_ascii=False, sort_keys=True)  # print("Вывод:\n" + d)

        data_bot = read_json(file_data_bot)
        ans_d_bot = ""
        for i in data_bot:
            ans_d_bot += 'ID: {:>9}. Вр: {}. Польз: {:>10}. Запросов: {:>4}. Посл: {} - ({}). Яз:{}\n' \
                         ' ---/ Запросы: {} \---\n'.\
                format(i['chat_id'], i['date_msg'], i['username'], i['num_req'],
                       i['location'][0], i['location'][1], i['lang_code'], i['requests'])

        return HttpResponse("Ответ Bitrix24:\n{}\n Данные чата:\n{}".format
                            (d, ans_d_bot), content_type="application/json")


def chats_list(request):
    chats = Chat.objects.all()
    return render(request, 'bitr24/index.html', context={'chats': chats})


class ChatDetail(ObjectDetailMixin, View):
    model = Chat
    template = 'bitr24/chat_detail.html'


class BitrDetail(ObjectDetailMixin, View):
    model = Bitr
    template = 'bitr24/bitr_detail.html'


def bitrs_list(request):
    bitrs = Bitr.objects.all()
    return render(request, 'bitr24/bitrs_list.html', context={'bitrs': bitrs})


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
# https://api.telegram.org/bot1016865412:AAECUp6v6T6tNdSLxbfR0M2BuU90Yy4R-gQ/setWebhook?url=https://12cea2ed.ngrok.io/bitr24/

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
