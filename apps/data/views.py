from django.db import transaction, connection
from rest_framework import generics, status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import ExcelFileSerializer, ClientSerializer
from .services import _data_file


class DBDataUpdateView(generics.CreateAPIView):
    """ Обновление базы данных клиентов """
    serializer_class = ExcelFileSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        file_serializer = ExcelFileSerializer(data=request.data)
        if file_serializer.is_valid():
            cursor = connection.cursor()
            cursor.execute("TRUNCATE TABLE clients RESTART IDENTITY ")
            input_file = file_serializer.validated_data['file']
            _data_file(input_file)
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(data=file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class FileCreateView(APIView):
#     """  """
#
#     def post(self, request):
#         # file_path = 'C:\\Проект Юры\\Клиенты фотографов.xlsx'
#         file = _writing_data_to_excel_file()
#         serializer = ExcelFileSerializer(file)
#         return Response(data=serializer.data, status=status.HTTP_201_CREATED)
