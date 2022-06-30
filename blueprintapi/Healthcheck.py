from django.db import OperationalError, connection
from rest_framework.decorators import api_view
from rest_framework.response import Response

class HealthCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        if request.path == '/api/healthcheck':
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                one = cursor.fetchone()[0]
                if one != 1:
                    raise OperationalError("Could not connect to database")
            return Response({"content": "Healthy"})
        return self.get_response(request)
