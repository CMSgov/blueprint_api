import datetime
import pytz

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed


class ExpiringTokenAuthentication(TokenAuthentication):
    """Extend TokenAuthentication to expire existing tokens."""
    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist as exc:
            raise AuthenticationFailed(_('Invalid token.')) from exc

        if not token.user.is_active:
            raise AuthenticationFailed(_('User inactive or deleted.'))

        # This is required for the time comparison
        utc_now = datetime.datetime.utcnow()
        utc_now = utc_now.replace(tzinfo=pytz.utc)

        if utc_now - token.created > datetime.timedelta(hours=settings.AUTH_TOKEN_TTL):
            token.delete()
            raise AuthenticationFailed(_('Token has expired.'))

        return token.user, token
