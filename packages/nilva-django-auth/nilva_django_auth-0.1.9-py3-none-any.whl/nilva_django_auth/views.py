import time

from django.core.cache import cache
from django.utils import timezone
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from nilva_django_auth.models import UserSession
from nilva_django_auth.serializers import SessionSerializer
from nilva_django_auth.session_management import SessionManagement
from nilva_django_auth.simplejwt.authentication import JWTAuthentication
from nilva_django_auth.simplejwt.settings import api_settings


def cache_api_data(func):
    def inner(*args, **kwargs):
        func_self = args[0]

        cache_key = func_self.get_cache_key()
        start = time.time()
        cache_data = cache.get(cache_key)
        end = time.time()
        if cache_data is not None:
            return Response(cache_data)

        response = func(*args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            cache.set(cache_key, response.data, )
        return response

    return inner


class SessionListView(ListAPIView):
    """
    API view for listing user sessions.

    Returns a JSON response with a list of active sessions for the current user.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = SessionSerializer
    pagination_class = None

    def get_cache_key(self):
        return SessionManagement.get_session_list_cache_key(self.request.user.id)

    def get_queryset(self):
        """
        Get a list of all active sessions for the current user.

        Returns:
            QuerySet of active UserSession objects for the current user.
        """
        user_id = self.request.user.id

        # Get all active sessions for the user from the database
        return UserSession.objects.filter(user_id=user_id, is_active=True, exp__gte=timezone.now()).order_by(
            '-last_activity'
        )

    def get_serializer_context(self):
        """
        Add current_jti to the serializer context.
        """
        context = super().get_serializer_context()

        # Extract the JTI from the request's token
        token = self.request.auth
        if token:
            context['current_jti'] = token.get(api_settings.JTI_CLAIM)

        return context

    @cache_api_data
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
