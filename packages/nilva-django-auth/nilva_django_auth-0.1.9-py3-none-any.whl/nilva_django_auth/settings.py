from datetime import timedelta
from django.conf import settings
from django.test.signals import setting_changed
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _

def format_lazy(format_string, *args, **kwargs):
    """
    Lazily format a lazy string.
    """
    return format_string.format(*args, **kwargs) if args or kwargs else format_string

DEFAULTS = {
    # Cookie settings
    'USE_COOKIES': False,
    'AUTH_COOKIE_NAME': 'auth',
    'REFRESH_COOKIE_NAME': 'refresh',
    'SECURE_COOKIES': True,
    'HTTPONLY_COOKIES': True,
    'SAMESITE_COOKIES': 'Lax',

    # Custom user model
    'USER_MODEL': 'auth.User',

    # Session management
    'BLACKLIST_ALL_MIN_SESSION_AGE': timedelta(minutes=5),

    # SimpleJWT settings
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=5),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": False,
    "BLACKLIST_CACHE_TIMEOUT": 300,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": settings.SECRET_KEY,
    "VERIFYING_KEY": "",
    "AUDIENCE": None,
    "ISSUER": None,
    "JSON_ENCODER": None,
    "JWK_URL": None,
    "LEEWAY": 0,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "nilva_django_auth.simplejwt.authentication.default_user_authentication_rule",
    "AUTH_TOKEN_CLASSES": ("nilva_django_auth.simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "JTI_CLAIM": "jti",
    "TOKEN_USER_CLASS": "nilva_django_auth.simplejwt.models.TokenUser",
    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),
    "TOKEN_OBTAIN_SERIALIZER": "nilva_django_auth.simplejwt.serializers.TokenObtainPairSerializer",
    "TOKEN_REFRESH_SERIALIZER": "nilva_django_auth.simplejwt.serializers.TokenRefreshSerializer",
    "TOKEN_BLACKLIST_SERIALIZER": "nilva_django_auth.simplejwt.serializers.TokenBlacklistSerializer",
    "TOKEN_BLACKLIST_ALL_SERIALIZER": "nilva_django_auth.simplejwt.serializers.TokenBlacklistAllSerializer",
    "TOKEN_BLACKLIST_SESSIONS_SERIALIZER": "nilva_django_auth.simplejwt.serializers.TokenBlacklistSessionsSerializer",
    "TOKEN_VERIFY_SERIALIZER": "nilva_django_auth.simplejwt.serializers.TokenVerifySerializer",
    "SLIDING_TOKEN_OBTAIN_SERIALIZER": "nilva_django_auth.simplejwt.serializers.TokenObtainSlidingSerializer",
    "SLIDING_TOKEN_REFRESH_SERIALIZER": "nilva_django_auth.simplejwt.serializers.TokenRefreshSlidingSerializer",
}

IMPORT_STRINGS = [
    # SimpleJWT import strings
    "AUTH_TOKEN_CLASSES",
    "JSON_ENCODER",
    "TOKEN_USER_CLASS",
    "USER_AUTHENTICATION_RULE",
]

REMOVED_SETTINGS = [
    # SimpleJWT removed settings
    "AUTH_HEADER_TYPE",
    "AUTH_TOKEN_CLASS",
    "SECRET_KEY",
    "TOKEN_BACKEND_CLASS",
]


def perform_import(val, setting_name):
    """
    If the given setting is a string import notation,
    then perform the necessary import or imports.
    """
    if val is None:
        return None
    elif isinstance(val, str):
        return import_from_string(val, setting_name)
    elif isinstance(val, (list, tuple)):
        return [import_from_string(item, setting_name) for item in val]
    return val


def import_from_string(val, setting_name):
    """
    Attempt to import a class from a string representation.
    """
    try:
        return import_string(val)
    except ImportError as e:
        msg = "Could not import '%s' for API setting '%s'. %s: %s." % (
            val, setting_name, e.__class__.__name__, e)
        raise ImportError(msg)


class APISettings:
    """
    A settings object that allows accessing the NILVA_AUTH settings as properties.
    For example:
        from nilva_django_auth.settings import api_settings
        print(api_settings.TOKEN_LIFETIME)
    """
    def __init__(self, user_settings=None, defaults=None, import_strings=None, removed_settings=None):
        if user_settings:
            self._user_settings = user_settings
        self.defaults = defaults or DEFAULTS
        self.import_strings = import_strings or IMPORT_STRINGS
        self.removed_settings = removed_settings or REMOVED_SETTINGS
        self._cached_attrs = set()

    @property
    def user_settings(self):
        if not hasattr(self, '_user_settings'):
            self._user_settings = {}
            # Get settings from NILVA_AUTH
            nilva_auth_settings = getattr(settings, 'NILVA_AUTH', {})
            self._user_settings.update(nilva_auth_settings)

            # For backward compatibility, if SIMPLE_JWT is defined, use it for SimpleJWT-specific settings
            simple_jwt_settings = getattr(settings, 'SIMPLE_JWT', {})
            if simple_jwt_settings:
                # Only update with SimpleJWT settings if they don't already exist in NILVA_AUTH
                for key, value in simple_jwt_settings.items():
                    if key not in self._user_settings:
                        self._user_settings[key] = value

            # Check for removed settings
            self.__check_user_settings(self._user_settings)
        return self._user_settings

    def __check_user_settings(self, user_settings):
        for setting in self.removed_settings:
            if setting in user_settings:
                raise RuntimeError(
                    format_lazy(
                        _(
                            "The '{}' setting has been removed. Please refer to documentation for available settings."
                        ),
                        setting,
                    )
                )
        return user_settings

    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError("Invalid API setting: '%s'" % attr)

        try:
            # Check if present in user settings
            val = self.user_settings[attr]
        except KeyError:
            # Fall back to defaults
            val = self.defaults[attr]

        # Coerce import strings into classes
        if attr in self.import_strings:
            val = perform_import(val, attr)

        # Cache the result
        self._cached_attrs.add(attr)
        setattr(self, attr, val)
        return val

    def reload(self):
        """
        Reload settings after a change. Used mainly in testing.
        """
        for attr in self._cached_attrs:
            delattr(self, attr)
        self._cached_attrs.clear()
        if hasattr(self, '_user_settings'):
            delattr(self, '_user_settings')


api_settings = APISettings(None, DEFAULTS, IMPORT_STRINGS, REMOVED_SETTINGS)


def reload_api_settings(*args, **kwargs):
    """
    Reset settings. Used in testing.
    """
    setting = kwargs['setting']
    if setting in ['NILVA_AUTH', 'SIMPLE_JWT']:
        api_settings.reload()


setting_changed.connect(reload_api_settings)
