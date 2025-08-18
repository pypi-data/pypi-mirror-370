# alignment/api/urls.py

from django.urls import path, include
from django.http import JsonResponse
from .views import ( 
    GenerateAPIKeyView, LoginView, 
    ListAPIKeysView, DeleteAPIKeyView, 
    LogoutView, TokenValidateView,
    ListUserAPIKeysView
    )


def social_login_success(request):
    return JsonResponse({"message": "Social login successful", "user": request.user.username})


urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("generate/", GenerateAPIKeyView.as_view(), name="generate-api-key"),
    path('dj-rest-auth/registration/', include('dj_rest_auth.registration.urls')),
    path("api-keys/", ListAPIKeysView.as_view(), name="list-api-keys"),
    path("api-keys/<int:key_id>/", DeleteAPIKeyView.as_view(), name="delete-api-key"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("token/validate/", TokenValidateView.as_view()),
    path("my-api-keys/", ListUserAPIKeysView.as_view(), name="my-api-keys"),
    path('dj-rest-auth/', include('dj_rest_auth.urls')),
]