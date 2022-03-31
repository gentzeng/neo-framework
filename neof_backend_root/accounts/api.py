from django.contrib.auth import get_user_model
from django.contrib.auth import login

from rest_framework import status
from rest_framework import generics
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.authtoken.serializers import AuthTokenSerializer

from knox.auth import TokenAuthentication
from knox.models import AuthToken
from knox.views import LoginView as KnoxLoginView

from .serializers import (
    RegisterSerializer,
    # LoginSerializer,
    UserSerializer,
)

User = get_user_model()


class SignUpAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        _, token = AuthToken.objects.create(user)
        return Response(
            {
                "users": UserSerializer(
                    user, context=self.get_serializer_context()
                ).data,
                "token": token,
            },
            status=status.HTTP_201_CREATED,
        )

    def put(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class LoginApi(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        if user.role != User.RESEARCHER:
            return Response(
                {"role_error": "User is not a researcher!"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        login(request, user)
        response = super(LoginApi, self).post(request, format=None)

        token = response.data["token"]
        del response.data["token"]

        response.set_cookie("auth_token", token, httponly=False, samesite="strict")
        response.set_cookie("user_name", user, samesite="strict")

        return response


class MainUser(generics.RetrieveAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer
