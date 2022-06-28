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
    queryset = Component.objects.all()
    serializer_class = ComponentSerializer

    def list(self, request):
        queryset = self.get_queryset()
        serializer = ComponentListSerializer(queryset, many=True)
        return Response(serializer.data)


# Use for read or update endpoints to represent a single model instance.
# Provides get, put, and patch method handlers.
class ComponentDetailView(generics.RetrieveUpdateAPIView):
    queryset = Component.objects.all()
    serializer_class = ComponentSerializer


class ComponentListSearchView(APIView):

    # @api_view('GET')
    def get(self, request, *args, **kwargs):
        page_number = self.request.query_params.get("page", default=1)
        search_query = self.request.query_params.get("search")

        # Start with search param, then pass it to ComponentFilter to filter by type and catalog
        if search_query is not None:
            filtered_qs = ComponentFilter(
                self.request.query_params,
                queryset=Component.objects.filter(title__contains=search_query)
                | Component.objects.filter(description__contains=search_query),
            ).qs
        else:
            filtered_qs = ComponentFilter(
                self.request.query_params,
                queryset=Component.objects.all().order_by("id"),
            ).qs
        # ordering = ["-id"] need to add ordering to filtered_qs here
        # Utilize the pagination based on 20 items on a page
        paginator = Paginator(filtered_qs, 20)
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        # serialize all the values before returning the response
        serializer_class = ComponentListSerializer
        serializer = serializer_class(page_obj, many=True)

        # update the response to include the total_item_count
        response = serializer.data
        response.append({"total_item_count": paginator.count})
        return Response(response, status=status.HTTP_200_OK)
