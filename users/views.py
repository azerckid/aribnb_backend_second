from django.contrib.auth import authenticate, login, logout
from django.db.models import Prefetch
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ParseError, NotFound

from users.models import User
from reviews.models import Review
from bookings.models import Booking
from . import serializers

class Me(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = (
            User.objects.prefetch_related(
                Prefetch("reviews", queryset=Review.objects.select_related("room", "experience")),
                Prefetch(
                    "bookings",
                    queryset=Booking.objects.select_related("room", "experience"),
                ),
            )
            .get(pk=request.user.pk)
        )
        serializer = serializers.UserProfileSerializer(user)
        return Response(serializer.data)

    def put(self, request):
        user = request.user
        serializer = serializers.PrivateUserSerializer(
            user,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                serializers.UserProfileSerializer(user).data,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Users(APIView):

    def post(self, request):
        password = request.data.get("password")
        if not password:
            raise ParseError("Password is required.")
        serializer = serializers.PrivateUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(password)
            user.save()
            return Response(
                serializers.PrivateUserSerializer(user).data,
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PublicUser(APIView):

    def get(self, request, username):
        user = (
            User.objects.prefetch_related(
                Prefetch("reviews", queryset=Review.objects.select_related("room", "experience")),
                Prefetch(
                    "bookings",
                    queryset=Booking.objects.select_related("room", "experience"),
                ),
            )
            .filter(username=username)
            .first()
        )
        if not user:
            raise NotFound
        serializer = serializers.UserProfileSerializer(user)
        return Response(serializer.data)

class ChangePassword(APIView):

    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")
        if not old_password or not new_password:
            raise ParseError("old_password and new_password are required.")
        if not user.check_password(old_password):
            raise ParseError("Current password is incorrect.")
        user.set_password(new_password)
        user.save()
        return Response({"ok": True})

class LogIn(APIView):

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        if not username or not password:
            raise ParseError("username and password are required.")
        user = authenticate(
            request,
            username=username,
            password=password,
        )
        if not user:
            return Response(
                {"error": "Invalid credentials."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        login(request, user)
        return Response({"ok": True})

class LogOut(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"ok": True})
