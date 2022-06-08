from django.db import OperationalError, connection
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["GET"])
def index(request):
    response = {"content": "Home"}
    return Response(response)


@api_view(["GET"])
def healthcheck(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        one = cursor.fetchone()[0]
        if one != 1:
            raise OperationalError("Could not connect to database")
    response = {"content": "Healthy"}
    return Response(response)
