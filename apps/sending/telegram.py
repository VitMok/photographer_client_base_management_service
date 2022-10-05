import redis
import time
from django.conf import settings
from telethon import TelegramClient
from telethon.tl.types import InputPhoneContact
from telethon.tl.functions.contacts import ImportContactsRequest
from teleredis import RedisSession
from selenium import webdriver
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


class Telegram:
    """  """
    redis_connector_1 = redis.Redis(host='redis', port=6379, db=1, decode_responses=False)
    redis_connector_2 = redis.Redis(host='redis', port=6379, db=2, decode_responses=False)
    session_1 = RedisSession('snape', redis_connector_1)
    session_2 = RedisSession('photo_moscow', redis_connector_2)
    # client_severus = TelegramClient(session_1,
    #                                 settings.TELEGRAM_API_ID,
    #                                 settings.TELEGRAM_HASH)
    # client_photo = TelegramClient(session_2,
    #                               settings.PHOTO_TELEGRAM_API_ID,
    #                               settings.PHOTO_TELEGRAM_HASH)

    def check_sign_in(self):
        if not Telegram.client_severus.is_user_authorized():
            Telegram.client_severus.send_code_request(settings.TELEGRAM_PHONE)
            return False
        return True

    def input_code(self, code):
        Telegram.client_severus.sign_in(settings.TELEGRAM_PHONE, code)

    def add_contact(self, client):
        contact = InputPhoneContact(client_id=0, phone='+' + client.phone,
                                    first_name=client.name, last_name="Клиент Фото Москва")
        result = Telegram.client_severus.invoke(ImportContactsRequest(contacts=[contact]))
        client.is_added_to_contacts = True
        if not result.users:
            client.is_in_telegram = False
            client.save()
            return

        client.is_in_telegram = True

        if result.users[0].username is not None:
            if result.users[0].username != 'UnsupportedUser64Bot':
                client.telegram_username = result.users[0].username
        client.save()

    async def connection_photo(self):
        await Telegram.client_photo.connect()

    async def check_sign_in_photo(self):
        if not await Telegram.client_photo.is_user_authorized():
            await Telegram.client_photo.send_code_request(settings.PHOTO_TELEGRAM_PHONE)
            return False
        return True

    async def input_code_photo(self, code):
        await Telegram.client_photo.sign_in(settings.PHOTO_TELEGRAM_PHONE, code)

    async def send_message(self, client):
        name = client.name
        if '(' in name:
            name = name[:name.find('(') - 1]
        await Telegram.client_photo.send_message(
            client.telegram_username,
            'Добрый день, {}.\nУ нас проходит акция на фотосессию\n"Знакомство с фотографом"\n'
            'Если у вас возникли вопросы или желание принять участие в фотосессии, отправьте '
            'ответное сообщение с вопросом.\n\n'
            'Группа в телеграмме с анонсами съемок: https://t.me/Mos_Foto'.format(name)
        )
        client.is_invited = True
        client.save()

class TelegramChrome:
    """  """
    # driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver")
    # driver = webdriver.Chrome("/usr/local/bin/chromedriver")

    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_prefs = {}
        chrome_options.experimental_options["prefs"] = chrome_prefs
        chrome_prefs["profile.default_content_settings"] = {"images": 2}
        self.driver = webdriver.Chrome(options=chrome_options)

    def sign_in(self):
        self.driver.get('https://web.telegram.org/k/')
        time.sleep(5)
        self.driver.find_element(By.XPATH,
                                           '/html/body/div[1]/div/div[2]/div[2]/div/div[2]/button[1]').click()
        time.sleep(2)
        self.driver.find_element(
            By.XPATH,
            '/html/body/div[1]/div/div[2]/div[1]/div/div[3]/div[2]/div[1]'
        ).send_keys('9295219892')
        time.sleep(2)
        self.driver.find_element(By.XPATH,
                                           '/html/body/div[1]/div/div[2]/div[1]/div/div[3]/button[1]/div').click()

    def input_code(self, code):
        self.driver.find_element(By.XPATH,
                                           '/html/body/div[1]/div/div[2]/div[3]/div/div[3]/div/input').send_keys(code)
        time.sleep(2)

    def go_to_contacts(self):
        self.driver.find_element(By.XPATH,
                            '/html/body/div[1]/div[1]/div[1]/div/div/div[1]/div[1]/div[2]/div[1]').click()
        time.sleep(1)
        self.driver.find_element(By.XPATH,
                            '/html/body/div[1]/div[1]/div[1]/div/div/div[1]/div[1]/div[2]/div[3]/div[3]').click()
        time.sleep(3)

    def add_contact(self, client):
        self.driver.find_element(By.XPATH,
                                           '/html/body/div[1]/div[1]/div[1]/div/div[2]/div[2]/button/div').click()
        time.sleep(2)

        first_name = self.driver.find_element(By.XPATH,
                                                        '/html/body/div[5]/div/div[2]/div[1]/div[2]')
        ActionChains(self.driver).click(first_name) \
            .send_keys_to_element(first_name, client.name).perform()

        last_name = self.driver.find_element(By.XPATH,
                                                       '/html/body/div[5]/div/div[2]/div[2]/div[2]')
        ActionChains(self.driver).click(last_name) \
            .send_keys_to_element(last_name, 'Клиент Фото Москва').perform()

        phone = self.driver.find_element(By.XPATH,
                                                   '/html/body/div[5]/div/div[3]/div[2]')
        ActionChains(self.driver).click(phone) \
            .send_keys_to_element(phone, client.phone).perform()

        add = self.driver.find_element(By.XPATH,
                                                 '/html/body/div[5]/div/div[1]/button/div')
        add.click()
        time.sleep(2)
        try:
            self.driver.find_element(By.XPATH,
                                               '/html/body/div[5]/div/div[2]/div[1]/div[2]')
        except:
            client.is_in_telegram = True
        else:
            client.is_in_telegram = False
            webdriver.ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
            time.sleep(2)
        finally:
            client.is_added_to_contacts = True
            client.save()

    def driver_close(self):
        self.driver.close()