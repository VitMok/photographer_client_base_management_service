import time
import asyncio

from django.http import HttpResponseRedirect
from django.urls import reverse
from telethon.tl.functions.contacts import ImportContactsRequest
from telethon.tl.types import InputPhoneContact

from photographer_client_base_management_service.celery import app

from apps.data.models import Client
from .models import Sending, CodeTelegramChrome
from .telegram import Telegram, TelegramChrome
from .services import _get_clients_for_sending


@app.task(bind=True, max_retries=None)
def adding_contacts(self, code=0):
    """ Добавление пользователей из бд в контакты телеграм аккаунта """
    try:
        telegram = Telegram()
        assert telegram.client_severus.connect()
        clients = Client.objects.filter(is_added_to_contacts=False)[:50]
        for client in clients:
            time.sleep(2)
            telegram.add_contact(client)
        telegram.client_severus.disconnect()
        raise Exception('Перезапуск задачи')
    except Exception as exc:
        raise self.retry(exc=exc, countdown=240)

loop_2 = asyncio.new_event_loop()
asyncio.set_event_loop(loop_2)
loop_2 = asyncio.get_event_loop()

@app.task(bind=True, max_retries=None)
def sending_messages(self, sending_id):
    try:
        telegram = Telegram()
        loop_2.run_until_complete(telegram.connection_photo())
        if not loop_2.run_until_complete(telegram.check_sign_in_photo()):
            return HttpResponseRedirect(reverse('sending:input_code_photo'))
        sending = Sending.objects.get(pk=sending_id)
        clients_quantity = sending.messages_quantity - sending.sent_messages_quantity
        clients = _get_clients_for_sending(clients_quantity, sending)
        for client in clients:
            time.sleep(2)
            loop_2.run_until_complete(telegram.send_message(client))
            sending.sent_messages_quantity += 1
            sending.save()
        sending.is_finished = True
        sending.save()
    except Exception as exc:
        raise self.retry(exc=exc, countdown=240)

@app.task(bind=True, max_retries=None)
def adding_contacts_to_chrome_telegram(self):
    try:
        TelegramChrome.sign_in()
        code = CodeTelegramChrome.objects.all()
        while not code:
            code = CodeTelegramChrome.objects.all()
        TelegramChrome.input_code(code[0].code)
        code[0].delete()
        TelegramChrome.go_to_contacts()
        clients = Client.objects.filter(
            is_added_to_contacts=False,
        )[:5000]
        for client in clients:
            TelegramChrome.add_contact(client)
        raise Exception('50 клиентов добавлены.')
    except Exception as exc:
        TelegramChrome.driver_close()
        raise self.retry(exc=exc, countdown=60)
