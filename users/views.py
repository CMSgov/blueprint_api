from django.http import HttpResponse


def index(request):
    return HttpResponse("Successful connection with Users API")
