from django.urls import path, include

from rest_framework.routers import DefaultRouter

from knox import views as knox_views

from .api import (
    SignUpAPI,
    LoginApi,
    MainUser,
    UserViewSet,
)

from .views import (
    LoginResearcherView,
    SignUpResearcherView,
)


user_list = UserViewSet.as_view(
    {
        "get": "list",
    }
)

user_detail = UserViewSet.as_view(
    {
        "get": "retrieve",
    }
)

router = DefaultRouter()
router.register(r"users", UserViewSet)


urlpatterns = [
    path("", include(router.urls)),
    # path('api-auth/', include('rest_framework.urls')),
    path(
        "api/auth/sign-up-researcher/",
        SignUpAPI.as_view(),
        name="auth-register-researcher",
    ),
    path(
        "api/auth/login-researcher/", LoginApi.as_view(), name="auth-login-researcher"
    ),
    path("api/auth/user/", MainUser.as_view(), name="auth-user"),
    path(
        "api/auth/logoutall/", knox_views.LogoutAllView.as_view(), name="auth-logoutall"
    ),
    path("api/auth/logout/", knox_views.LogoutView.as_view(), name="auth-logout"),
    path(
        "sign-up-researcher/", SignUpResearcherView.as_view(), name="sign-up-researcher"
    ),
    path("login-researcher/", LoginResearcherView.as_view(), name="login-researcher"),
    # path("api/auth/", include("knox.urls")),
]
