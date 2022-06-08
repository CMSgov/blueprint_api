from django.db import OperationalError, connection
from django.http import JsonResponse


def index(request):
    response = {"content": "Home"}
    return JsonResponse(response)


def healthcheck(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        one = cursor.fetchone()[0]
        if one != 1:
            raise OperationalError("Could not connect to database")
    response = {"content": "Healthy"}
    return JsonResponse(response)
