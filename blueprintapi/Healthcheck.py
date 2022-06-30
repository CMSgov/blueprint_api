from django.db import OperationalError, connection
from django.http import HttpResponse, HttpResponseRedirect

class HealthCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        if request.path == '/api/healthcheck' or request.path == '/api/healthcheck/':
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                one = cursor.fetchone()[0]
                if one != 1:
                    raise OperationalError("Could not connect to database")
            response = {"content": "Healthy"}
            return HttpResponse(response)
        return self.get_response(request)
