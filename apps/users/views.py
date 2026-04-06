from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import UserSerializer
from .models import User   # 👈 IMPORTANTE

from rest_framework.views import APIView


from .serializers import CreateUserSerializer
from .permissions import IsAdminUserCustom


class CustomLoginView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            user = User.objects.get(username=request.data['username'])
            user_data = UserSerializer(user).data

            return Response({
                'token': response.data,
                'user': user_data
            })

        return response


class CreateUserView(APIView):
    permission_classes = [IsAdminUserCustom]

    def post(self, request):
        serializer = CreateUserSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
