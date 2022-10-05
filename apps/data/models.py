from django.db import models
from django.core import validators
from django.contrib.postgres.indexes import HashIndex


class Client(models.Model):
    """ Клиент """
    name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Имя'
    )
    phone = models.CharField(
        unique=True,
        max_length=11,
        validators=[validators.RegexValidator(regex=r'\d{11}')],
        verbose_name='Номер телефона'
    )
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name='Почта'
    )
    date = models.DateField(
        verbose_name='Дата последнего визита'
    )
    total_sum = models.PositiveIntegerField(
        default=0,
        verbose_name='Общая сумма'
    )
    visits_quantity = models.PositiveIntegerField(
        default=1,
        verbose_name='Количество посещений'
    )
    is_added_to_contacts = models.BooleanField(
        default=False,
        verbose_name='Статус добавления в контакты'
    )
    is_in_telegram = models.BooleanField(
        default=False,
        verbose_name='Наличие пользователя в телеграмме'
    )
    telegram_username = models.CharField(
        max_length=255,
        default='',
        verbose_name='Ник в телеграмме'
    )
    is_invited = models.BooleanField(
        default=False,
        verbose_name='Статус приглашения'
    )

    class Meta:
        db_table = 'clients'
        indexes = [
            HashIndex(fields=['phone'],
                      name='i_phone'),
        ]
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'

    def __str__(self):
        return self.phone

