from django.db import models


class Sending(models.Model):
    """ Рассылка """
    min_total_sum = models.PositiveIntegerField(
        default=0,
        verbose_name='Минимальная сумма'
    )
    max_total_sum = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='Максимальная сумма'
    )
    min_visits_quantity = models.PositiveIntegerField(
        default=0,
        verbose_name='Минимальное количество посещений'
    )
    max_visits_quantity = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='Максимальное количество посещений'
    )
    messages_quantity = models.PositiveIntegerField(
        verbose_name='Количество сообщений'
    )
    sent_messages_quantity = models.PositiveIntegerField(
        default=0,
        verbose_name='Количество отправленных сообщений'
    )
    is_finished = models.BooleanField(
        default=False,
        verbose_name='Статус завершения рассылки'
    )

    class Meta:
        db_table = 'sendings'
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'

class CodeTelegramChrome(models.Model):
    """  """
    code = models.PositiveIntegerField(
        verbose_name='Код для входа в аккаунт'
    )

    class Meta:
        db_table = 'codes'