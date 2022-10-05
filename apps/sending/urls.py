from django.urls import path

from . import views


app_name = 'sending'

urlpatterns = [
    path('update-contacts/', views.TelegramContactsUpdateView.as_view()),
    path('input-code/', views.InputCodeSignInView.as_view(), name='input_code'),
    path('sending/', views.SendingMessagesView.as_view(), name='send_messages'),
    path('input-code-photo/', views.InputCodePhotoAccount.as_view(), name='input_code_photo'),
    path('adding-contacts/', views.AddingContactsChromeTelegramView.as_view(), name='adding_contacts'),
    path('input-code-chrome/', views.InputCodeChromeTelegramView.as_view(), name='input_code_chrome'),
]