from django.http import JsonResponse


def index(request):
    response = {
        "content": "Home"
    }
    return JsonResponse(response)

def healthcheck(request):
    response = {
        "health": "Healthy",
        "response": 200
    }
    return JsonResponse(response)
