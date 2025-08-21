import datetime
import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from user_agents.parsers import parse

from nilva_django_auth.simplejwt.utils import datetime_from_epoch


class UserSession(models.Model):
    """
    Model to track user sessions.
    """
    id = models.CharField(max_length=36, default=uuid.uuid4, primary_key=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sessions',
        verbose_name=_('User')
    )
    jti = models.UUIDField(
        unique=True,
        verbose_name=_('JWT ID')
    )
    user_agent = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('User Agent')
    )
    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
        verbose_name=_('IP Address')
    )
    referer = models.URLField(
        blank=True,
        null=True,
        verbose_name=_('Referer')
    )
    exp = models.DateTimeField(
        verbose_name=_('Expiration Time')
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name=_('Created At')
    )
    last_activity = models.DateTimeField(
        default=timezone.now,
        verbose_name=_('Last Activity')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Is Active')
    )

    class Meta:
        verbose_name = _('User Session')
        verbose_name_plural = _('User Sessions')
        ordering = ['-last_activity']

    def __str__(self):
        return f"{self.user} - {self.jti}"

    def update_activity(self):
        """
        Update the last activity timestamp.
        """
        self.last_activity = timezone.now()
        self.save(update_fields=['last_activity'])

    def deactivate(self):
        """
        Deactivate the session.
        """
        self.is_active = False
        self.save(update_fields=['is_active'])

    @classmethod
    def create_session(cls, user, jti, exp, request=None):
        """
        Create a new session for the user.

        Args:
            user: The user for whom the session is being created
            jti: The JWT ID
            exp: The expiration time (datetime object or Unix timestamp)
            request: The request object (optional, used to extract device info and IP address)

        Returns:
            UserSession: The created session object
        """
        ip_address = None
        user_agent_str = None
        referer = None

        # Convert exp from timestamp to datetime if it's not already a datetime
        if exp is not None and not isinstance(exp, datetime.datetime):
            exp = datetime_from_epoch(exp)
        # If exp is None, set a default expiration time (24 hours from now)
        elif exp is None:
            exp = timezone.now() + datetime.timedelta(hours=24)

        if request:
            # Extract device info from user agent
            user_agent_str = request.META.get('HTTP_USER_AGENT', '')

            # We don't need to parse user agent here as we'll compute properties on-the-fly when needed

            # Extract IP address
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0]
            else:
                ip_address = request.META.get('REMOTE_ADDR')

            # Extract referer
            referer = request.META.get('HTTP_REFERER')

        return cls.objects.create(
            user=user,
            jti=jti,
            user_agent=user_agent_str,
            ip_address=ip_address,
            referer=referer,
            exp=exp
        )

    @classmethod
    def deactivate_all_for_user(cls, user):
        """
        Deactivate all sessions for the user.
        """
        cls.objects.filter(user=user, is_active=True).update(is_active=False)

    @cached_property
    def user_agent_obj(self):
        """
        Parse and return the user agent object.
        """
        return self.user_agent and parse(self.user_agent)

    @property
    def os(self):
        """
        Get the operating system family from the user agent.
        """
        return self.user_agent_obj and self.user_agent_obj.os.family

    @property
    def device_brand(self):
        """
        Get the device brand from the user agent.
        """
        return self.user_agent_obj and self.user_agent_obj.device.brand

    @property
    def device_model(self):
        """
        Get the device model from the user agent.
        """
        return self.user_agent_obj and self.user_agent_obj.device.model

    @property
    def device_family(self):
        """
        Get the device family from the user agent.
        """
        return self.user_agent_obj and self.user_agent_obj.device.family

    @property
    def is_mobile(self):
        """
        Check if the device is mobile from the user agent.
        """
        return self.user_agent_obj and self.user_agent_obj.is_mobile

    @property
    def browser(self):
        """
        Get the browser family from the user agent.
        """
        return self.user_agent_obj and self.user_agent_obj.browser.family
