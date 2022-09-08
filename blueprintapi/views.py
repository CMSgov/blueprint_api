from django.db import OperationalError, connection
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from blueprintapi.authentication import ExpiringTokenAuthentication


@api_view(["GET"])
def index(request):
    response = {"content": "Home"}
    return Response(response)


@api_view(["GET"])
@permission_classes([IsAuthenticatedOrReadOnly, ])
def healthcheck(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        one = cursor.fetchone()[0]
        if one != 1:
            raise OperationalError("Could not connect to database")
    response = {"content": "Healthy"}
    return Response(response)


class UserObtainTokenView(ObtainAuthToken):
    def post(self, request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        response_data = {
                'token': token.key,
                'user': {'username': user.username, 'full_name': user.get_full_name(), 'email': user.email},
            }

        if not created:
            auth = ExpiringTokenAuthentication()
            try:
                auth.authenticate_credentials(token.key)
            except AuthenticationFailed:
                new_token = Token.objects.create(user=user)
                response_data["token"] = new_token.key

            return Response(response_data)

        return Response(response_data)
