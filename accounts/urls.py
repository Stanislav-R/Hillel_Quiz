from django.urls import path

from .views import AccountLoginView, AccountLogoutView, AccountRegistrationDoneView, AccountRegistrationView, \
    AccountUpdateProfileView, account_profile_view, user_activate

app_name = 'accounts'

urlpatterns = [
    path('registration/асtivate/<str:sign>/', user_activate, name='register_activate'),
    path('registration/done/', AccountRegistrationDoneView.as_view(), name='registration_done'),
    path('registration/', AccountRegistrationView.as_view(), name='registration'),
    path('login/', AccountLoginView.as_view(), name='login'),
    path('logout/', AccountLogoutView.as_view(), name='logout'),
    path('profile/', account_profile_view, name='profile'),
    path('profile_change/', AccountUpdateProfileView.as_view(), name='profile_change'),
]
