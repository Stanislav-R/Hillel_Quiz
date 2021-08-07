from django.contrib.auth.views import PasswordResetView
from django.urls import path

app_name = 'accounts'

urlpatterns = [
    path('password_reset/',
         PasswordResetView.as_view(template_name='accounts/password_reset_form.html'),
         name='password_reset')
]
