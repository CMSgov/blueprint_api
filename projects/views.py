from django.http import JsonResponse


def index(request):
    response = {"content": "Project"}
    return JsonResponse(response)
