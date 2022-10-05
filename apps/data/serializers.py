from rest_framework import serializers

from .models import Client


class ExcelFileSerializer(serializers.Serializer):
    """ Сериализатор файла Excel """
    file = serializers.FileField()

class ClientSerializer(serializers.ModelSerializer):
    """ Сериализатор клиента """

    class Meta:
        model = Client
        fields = '__all__'