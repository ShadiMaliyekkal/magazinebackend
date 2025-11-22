# magazine/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Profile, Post, Comment, Like
from django.contrib.auth.models import User

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email")

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = ("user", "avatar", "bio")

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "author", "body", "created_at")

class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Like
        fields = ("id", "user")

class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    likes_count = serializers.IntegerField(source="likes.count", read_only=True)

    # Allow optional image upload + readable image_url
    image = serializers.ImageField(required=False, allow_null=True)
    image_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "author",
            "title",
            "content",
            "image",       # include the raw image field (relative path)
            "image_url",   # include a full absolute url for frontend use
            "created_at",
            "updated_at",
            "comments",
            "likes_count",
        )

    def get_image_url(self, obj):
        # returns absolute URL if request is available in serializer context
        if not obj.image:
            return None
        request = self.context.get("request")
        try:
            url = obj.image.url
        except Exception:
            return None
        if request:
            return request.build_absolute_uri(url)
        return url


# Register serializer for register endpoint (you already have this pattern)
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password")

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
        )
        # optionally create Profile if your view expects it
        Profile.objects.create(user=user)
        return user
