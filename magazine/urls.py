from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet, ProfileViewSet, RegisterAPIView

router = DefaultRouter()
router.register(r"posts", PostViewSet, basename="posts")
router.register(r"profiles", ProfileViewSet, basename="profiles")

urlpatterns = [
    path("", include(router.urls)),
    path("register/", RegisterAPIView.as_view(), name="api-register"),
]
