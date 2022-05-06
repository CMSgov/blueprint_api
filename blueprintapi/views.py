from django.http import JsonResponse


def index(request):
    response = {
        "content": "Home"
    }
    return JsonResponse(response)

def healthcheck(request):
    response = {
        "content": "Healthy"
    }
    return JsonResponse(response)
