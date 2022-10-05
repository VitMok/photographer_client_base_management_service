from django.http import HttpResponseRedirect
from django.urls import reverse
from rest_framework import status
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
import asyncio
import telethon
from selenium import webdriver

from .serializers import CodeSerializer, FilterSendingSerializer, CodeChromeTelegramSerializer
from .telegram import Telegram
from .tasks import adding_contacts, sending_messages, adding_contacts_to_chrome_telegram
from photographer_client_base_management_service.celery import app


class TelethonVersion_0_19_Permission(permissions.BasePermission):
    """ Проверка установлена ли версия telethon 0.19 """
    message = 'У вас не установлена библиотека telethon версии 0.19!\n' \
              'Установите и повторите попытку.'

    def has_permission(self, request, view):
        if telethon.__version__ == '0.19':
            return True
        return False

class TelethonVersionPermission(permissions.BasePermission):
    """ Проверка установлена ли последняя версия telethon """
    message = 'Обновите версию библиотеки telethon и повторите попытку!'

    def has_permission(self, request, view):
        if telethon.__version__ != '0.19':
            return True
        return False

class TelegramContactsUpdateView(APIView):
    """ Обновление контактной книжки телеграм аккаунта """
    permission_classes = [permissions.IsAdminUser, TelethonVersion_0_19_Permission]

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        self.telegram = Telegram()

    def get(self, request):
        assert self.telegram.client_severus.connect()
        return Response(
            {'message': 'Нажмите кнопку POST, чтобы запустить обновление контактов.'}
        )

    def post(self, request):
        app.control.purge()
        if self.telegram.check_sign_in():
            adding_contacts.delay()
            return Response({'message': 'Обновление контактов запущено.'})
        return HttpResponseRedirect(reverse('sending:input_code'))

class InputCodeSignInView(generics.CreateAPIView):
    """ Ввод кода для входа в телеграм аккаунт """
    serializer_class = CodeSerializer
    permission_classes = [permissions.IsAdminUser, TelethonVersion_0_19_Permission]

    def create(self, request, *args, **kwargs):
        telegram = Telegram()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            telegram.input_code(serializer.data['code'])
            adding_contacts.delay(serializer.data['code'])
            return Response({'message': 'Обновление контактов запущено.'})
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop = asyncio.get_event_loop()

class SendingMessagesView(generics.ListCreateAPIView):
    """ Запуск рассылки сообщений """
    permission_classes = [permissions.IsAdminUser, TelethonVersionPermission]

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        self.telegram = Telegram()
        loop.run_until_complete(self.telegram.connection_photo())
        self.serializer_class = self.get_serializer_class()

    def list(self, request, *args, **kwargs):
        if self.serializer_class == CodeSerializer:
            return Response({'message': 'Введите код для входа в телеграм аккаунт'})
        return Response({'message': 'Нажмите кнопку POST, чтобы запустить рассылку сообщений.'})

    def create(self, request, *args, **kwargs):
        if self.get_serializer_class() == CodeSerializer:
            serializer = self.get_serializer_class()(data=request.data)
            if serializer.is_valid():
                loop.run_until_complete(self.telegram.input_code_photo(serializer.data['code']))
                return HttpResponseRedirect(reverse('sending:send_messages'))
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer = self.get_serializer_class()(data=request.data)
            if serializer.is_valid():
                sending = serializer.save()
                app.control.purge()
                sending_messages.delay(sending.id)
                return Response({'message': 'Рассылка запущена.'})
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_serializer_class(self):
        if loop.run_until_complete(self.telegram.check_sign_in_photo()):
            return FilterSendingSerializer
        return CodeSerializer

class InputCodePhotoAccount(generics.CreateAPIView):
    serializer_class = CodeSerializer

    def create(self, request, *args, **kwargs):
        telegram = Telegram()
        serializer = CodeSerializer(data=request.data)
        if serializer.is_valid():
            loop.run_until_complete(telegram.input_code_photo(serializer.data['code']))
            return HttpResponseRedirect(reverse('sending:send_messages'))
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AddingContactsChromeTelegramView(APIView):# DRIVER = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver")
    """  """

    def get(self, request):
        return Response({'message': 'Нажмите на кнопку POST для запуска добавления контактов.'})

    def post(self, request):
        adding_contacts_to_chrome_telegram.delay()
        return HttpResponseRedirect(reverse('sending:input_code_chrome'))

class InputCodeChromeTelegramView(generics.ListCreateAPIView):
    """  """
    serializer_class = CodeChromeTelegramSerializer

    def list(self, request, *args, **kwargs):
        return Response({'message': 'Введите отправленный вам код для авторизации.'})
