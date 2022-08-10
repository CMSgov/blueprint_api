from rest_framework import serializers
from rest_framework.authtoken.models import Token
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "password", "first_name", "last_name", "email", "is_active", "auth_token", )
        extra_kwargs = {'password': {'write_only': True}, "auth_token": {"read_only": True}}

    def create(self, validated_data: dict) -> User:
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        Token.objects.create(user=user)

        return user

    def update(self, instance: User, validated_data: dict) -> User:
        password = validated_data.pop('password', None)

        if password:
            instance.set_password(password)

        for name, value in validated_data.items():
            setattr(instance, name, value)

        instance.save()

        return instance
