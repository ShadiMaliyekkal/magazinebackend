from rest_framework import viewsets, permissions, status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import Post, Comment, Like, Profile
from .serializers import (
    PostSerializer,
    CommentSerializer,
    LikeSerializer,
    UserSerializer,
    ProfileSerializer,
    RegisterSerializer,
)
from .permissions import IsOwnerOrReadOnly
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


# ---- REGISTER API (Main working endpoint) ----
class RegisterAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        user = serializer.save()
        refresh = RefreshToken.for_user(user)

        data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }
        return Response(data, status=201)


# ---- POSTS ----
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().select_related("author").prefetch_related("comments", "likes")
    serializer_class = PostSerializer
    permission_classes = [IsOwnerOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})  # 👈 IMPORTANT
        return context

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        post = self.get_object()
        user = request.user
        like, created = Like.objects.get_or_create(post=post, user=user)
        if not created:
            return Response({"detail": "already liked"}, status=400)
        return Response({"detail": "liked"}, status=201)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def unlike(self, request, pk=None):
        post = self.get_object()
        user = request.user
        deleted, _ = Like.objects.filter(post=post, user=user).delete()
        if deleted:
            return Response({"detail": "unliked"}, status=200)
        return Response({"detail": "not liked"}, status=400)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def comment(self, request, pk=None):
        post = self.get_object()
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user, post=post)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


# ---- PROFILE VIEWSET ----
class ProfileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Profile.objects.select_related("user")
    serializer_class = ProfileSerializer
    lookup_field = "user__username"
