import datetime
import time
from typing import List, Union

from django.core.cache import cache
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from nilva_django_auth.models import UserSession
from nilva_django_auth.simplejwt.exceptions import TokenError, InvalidToken
from nilva_django_auth.settings import api_settings
from nilva_django_auth.simplejwt.utils import datetime_from_epoch


class SessionManagement:
    @classmethod
    def blacklist(cls, user_id, jti):
        cls.check_blacklist(jti)
        UserSession.objects.filter(jti=jti, user_id=user_id).update(is_active=False)
        cls._invalidate_cache(jti)

    @classmethod
    def check_blacklist(cls, jti, raise_exception=True):
        cache_key = cls._blacklist_cache_key(jti)
        if cache_data := cache.get(cache_key):
            if cache_data and raise_exception:
                raise TokenError(_("Token is blacklisted"))
            return cache_data

        session = UserSession.objects.filter(jti=jti, is_active=True, exp__gte=timezone.now()).first()
        blacklisted = not session

        cache.set(cache_key, blacklisted, api_settings.BLACKLIST_CACHE_TIMEOUT)
        if blacklisted and raise_exception:
            raise TokenError(_("Token is blacklisted"))

        return blacklisted

    @classmethod
    def _blacklist_cache_key(cls, jti):
        return f"SessionManagement:token_blacklist_{jti}"

    @classmethod
    def _invalidate_cache(cls, jti: Union[str, List[str]]):
        if isinstance(jti, str):
            jti = [jti]
        cache.delete_many([cls._blacklist_cache_key(j) for j in jti])

    @classmethod
    def _invalidate_user(cls, user_id):
        cache.delete(cls.get_session_list_cache_key(user_id))

    @classmethod
    def blacklist_except(cls, user_id, exclude_jti, min_session_age=None):
        """
        Blacklist all sessions for a user except the one with the specified JTI.
        Only sessions created before the current session will be blacklisted.

        Args:
            user_id: The ID of the user whose sessions should be blacklisted
            exclude_jti: The JTI of the session to exclude from blacklisting
            min_session_age: Deprecated, kept for backward compatibility
        """
        # Get the current session to use its creation time as reference
        cls.check_session_age(exclude_jti, user_id, min_session_age)

        # Get all active sessions for this user except the current one
        # that were created before the current session
        sessions_query = UserSession.objects.filter(
            user_id=user_id,
            is_active=True,
        ).exclude(jti=exclude_jti)

        jti_list = list(sessions_query.values_list('jti', flat=True))
        if jti_list:
            cls._invalidate_cache(jti_list)
        sessions_query.update(is_active=False)

    @classmethod
    def check_session_age(cls, jti, user_id, min_session_age=None):
        if not min_session_age:
            min_session_age = api_settings.BLACKLIST_ALL_MIN_SESSION_AGE
        current_session = UserSession.objects.filter(user_id=user_id, jti=jti, is_active=True).first()
        if not current_session:
            # If current session not found, don't blacklist anything
            raise InvalidToken(_("Token is blacklisted or expired"))
        elif current_session.created_at > timezone.now() - min_session_age:
            # If the current session is too new, don't blacklist anything
            raise InvalidToken(
                _("Current session is too new. Please wait at least {} minutes before blacklisting other sessions.").format(
                    int(min_session_age.total_seconds() / 60)))

    @classmethod
    def create_session(cls, user, jti=None, exp=None, request=None):
        """
        Create a new session for the user.

        Args:
            user: The user for whom the session is being created
            jti: The JWT ID (optional)
            exp: The expiration time (optional, defaults to 24 hours from now)
                Can be a datetime object or a Unix timestamp (float)
            request: The request object (optional, used to extract device info and IP address)

        Returns:
            UserSession: The created session object
        """
        cls._invalidate_user(user.id)
        # Convert exp from timestamp to datetime if it's not already a datetime
        if exp is not None and not isinstance(exp, datetime.datetime):
            exp = datetime_from_epoch(exp)
        return UserSession.create_session(
            user=user,
            jti=jti,
            exp=exp,
            request=request
        )

    @classmethod
    def update_session(cls, old_jti, jti, exp, user_id):
        cls._invalidate_user(user_id)
        # Convert exp from timestamp to datetime if it's not already a datetime
        if not isinstance(exp, datetime.datetime):
            exp = datetime_from_epoch(exp)
        UserSession.objects.filter(jti=old_jti).update(
            exp=exp, jti=jti, last_activity=timezone.now(), is_active=True
        )

    @classmethod
    def deactivate_expired_sessions(cls, user_id=None, check_time=None):
        """
        Set is_active to False for all expired sessions.

        Args:
            user_id (int, optional): If provided, only deactivate expired sessions for this user.
            check_time (datetime or float, optional): The time to check against. If not provided, uses current time.
                If a float is provided, it's treated as a Unix timestamp and converted to datetime.

        Returns:
            int: The number of sessions that were deactivated.
        """
        if check_time is None:
            check_time = timezone.now()
        elif not isinstance(check_time, datetime.datetime):
            # Convert from Unix timestamp to datetime if necessary
            check_time = datetime_from_epoch(check_time)

        # Build the query to find expired sessions that are still active
        query = UserSession.objects.filter(is_active=True, exp__lt=check_time)

        # If user_id is provided, filter by user_id
        if user_id is not None:
            query = query.filter(user_id=user_id)

        # Update the sessions to set is_active to False
        count = query.update(is_active=False)

        return count

    @classmethod
    def get_session_list_cache_key(cls, user_id):
        return f"SessionManagement:session_list_{user_id}"

    @classmethod
    def terminate_sessions(cls, user_id, session_ids, current_jti=None, min_session_age=None):
        """
        Terminate specific sessions for a user.

        Args:
            user_id: The ID of the user whose sessions should be terminated
            session_ids: List of session IDs to terminate
            current_jti: The JTI of the current session (optional)
            min_session_age: Minimum age required for the current session (optional)

        Returns:
            int: The number of sessions that were terminated
        """
        cls.check_session_age(current_jti, user_id, min_session_age)

        # Get the sessions to terminate
        sessions = UserSession.objects.filter(
            user_id=user_id,
            id__in=session_ids,
            is_active=True
        )

        # Get the JTIs of the sessions to terminate
        jti_list = list(sessions.values_list('jti', flat=True))

        # Blacklist the sessions
        if jti_list:
            # Invalidate cache for the JTIs
            cls._invalidate_cache(jti_list)
            # Deactivate the sessions
            sessions.update(is_active=False)

        return len(jti_list)
