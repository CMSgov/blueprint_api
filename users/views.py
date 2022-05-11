from django.http import JsonResponse


def index(request):
    response = {"content": "Users"}
    return JsonResponse(response)
