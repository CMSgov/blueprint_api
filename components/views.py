from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import ComponentFilter
from .models import Component
from .serializers import ComponentListSerializer, ComponentSerializer


# Use for read-write endpoints to represent a collection of model instances.
# Provides get and post method handlers.
class ComponentListView(generics.ListCreateAPIView):
    queryset = Component.objects.all().order_by("pk")
    serializer_class = ComponentSerializer

    def list(self, request):
        queryset = self.get_queryset()
        serializer = ComponentListSerializer(queryset, many=True)
        return Response(serializer.data)


# Use for read or update endpoints to represent a single model instance.
# Provides get, put, and patch method handlers.
class ComponentDetailView(generics.RetrieveUpdateAPIView):
    queryset = Component.objects.all().order_by("pk")
    serializer_class = ComponentSerializer


class ComponentListSearchView(APIView):
    def get(self, request, *args, **kwargs):
        page_number = self.request.query_params.get("page", default=1)

        filtered_qs = ComponentFilter(
            self.request.GET,
            queryset=Component.objects.all().order_by("pk"),
        ).qs

        paginator = Paginator(filtered_qs, 20)
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        serializer_class = ComponentListSerializer
        serializer = serializer_class(page_obj, many=True)

        response = serializer.data
        response.append({"total_item_count": paginator.count})
        return Response(response, status=status.HTTP_200_OK)
