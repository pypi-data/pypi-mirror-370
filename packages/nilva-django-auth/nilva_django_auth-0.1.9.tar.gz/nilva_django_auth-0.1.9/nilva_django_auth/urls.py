from django.urls import path

from nilva_django_auth.simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView, \
    TokenBlacklistAllView, TokenVerifyView, TokenBlacklistSessionsView
from nilva_django_auth.views import SessionListView

app_name = 'nilva_django_auth'

urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='refresh'),
    path('logout/', TokenBlacklistView.as_view(), name='logout'),
    path('logout-all/', TokenBlacklistAllView.as_view(), name='logout-all'),
    path('logout-sessions/', TokenBlacklistSessionsView.as_view(), name='logout-sessions'),
    path('verify/', TokenVerifyView.as_view(), name='token-verify'),
    path('sessions/', SessionListView.as_view(), name='sessions'),
]
