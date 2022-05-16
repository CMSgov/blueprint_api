from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User
from .serializers import UserSerializer


class UsersListViews(APIView):

    # @api_view('POST')
    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # @api_view('GET')
    def get(request, *args, **kwargs):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UsersDetailView(APIView):
    def get_object(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    def get(self, request, user_id, *args, **kwargs):
        user_instance = self.get_object(user_id)
        if not user_instance:
            return Response(
                {"response": "The user you are looking for does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = UserSerializer(user_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, user_id, *args, **kwargs):
        user_instance = self.get_object(user_id)
        if not user_instance:
            return Response(
                {"response": "The user you are looking for does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = UserSerializer(
            instance=user_instance, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
