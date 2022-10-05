from rest_framework import serializers

from .models import Sending, CodeTelegramChrome


class CodeSerializer(serializers.Serializer):
    """ Сериализатор кода для входа
    в телеграм аккаунт """
    code = serializers.IntegerField(
        min_value=0
    )

class FilterSendingSerializer(serializers.ModelSerializer):
    """ Фильтрация рассылки """

    class Meta:
        model = Sending
        exclude = ('sent_messages_quantity',
                   'is_finished')

class CodeChromeTelegramSerializer(serializers.ModelSerializer):
    """  """

    class Meta:
        model = CodeTelegramChrome
        fields = '__all__'
