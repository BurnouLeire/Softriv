from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'roles']

    def get_roles(self, obj):
        return obj.roles


class CreateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    roles = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name', 'email', 'roles']

    def create(self, validated_data):
        roles = validated_data.pop('roles', [])
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            email=validated_data.get('email', ''),
        )
        if roles:
            from django.contrib.auth.models import Group
            grupos = Group.objects.filter(name__in=roles)
            user.groups.set(grupos)
        return user