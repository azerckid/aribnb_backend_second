import jwt
import requests

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.db.models import Prefetch
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import ParseError, NotFound
from rest_framework.authentication import TokenAuthentication
from config.authentication import JWTAuthentication, NoCSRFSessionAuthentication

from users.models import User
from reviews.models import Review
from bookings.models import Booking
from . import serializers

class Me(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [NoCSRFSessionAuthentication, TokenAuthentication, JWTAuthentication]

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

    permission_classes = [AllowAny]
    authentication_classes = []  # CSRF 검증 우회

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

    permission_classes = [AllowAny]

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
    authentication_classes = [NoCSRFSessionAuthentication, TokenAuthentication, JWTAuthentication]

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

    permission_classes = [AllowAny]
    authentication_classes = []  # CSRF 검증 우회

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
    authentication_classes = [NoCSRFSessionAuthentication, TokenAuthentication, JWTAuthentication]  # CSRF 우회하면서 세션 인증 지원

    def post(self, request):
        logout(request)
        return Response({"ok": True})

class JWTLogIn(APIView):

    permission_classes = [AllowAny]
    authentication_classes = []  # CSRF 검증 우회

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
        if user is None:
            return Response(
                {"error": "Invalid credentials."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        token = jwt.encode({"pk": user.pk}, settings.SECRET_KEY, algorithm="HS256")
        return Response({"token": token})

class GitHubLogIn(APIView):

    permission_classes = [AllowAny]
    authentication_classes = []  # CSRF 검증 우회

    def post(self, request):
        # 디버깅: 요청 데이터 확인
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"GitHub callback - request.data: {request.data}, request.POST: {request.POST}, Content-Type: {request.content_type}")
        
        # 프론트엔드에서 보낸 code 확인 (JSON 또는 form-data 모두 지원)
        code = request.data.get("code") or request.POST.get("code")
        if not code:
            # 디버깅: 요청 데이터 확인
            error_msg = f"code is required. Received data: {dict(request.data)}, POST: {dict(request.POST)}, Content-Type: {request.content_type}"
            logger.error(error_msg)
            raise ParseError(error_msg)
        
        # GitHub 액세스 토큰 요청
        client_id = settings.GITHUB_CLIENT_ID
        client_secret = settings.GITHUB_CLIENT_SECRET
        
        logger.error(f"GitHub OAuth - client_id: {client_id[:10]}..., client_secret: {'***' if client_secret else 'EMPTY'}, code: {code}")
        
        access_token_response = requests.post(
            "https://github.com/login/oauth/access_token",
            data={
                "client_id": client_id,
                "client_secret": client_secret,
                "code": code,
            },
            headers={"Accept": "application/json"},
        )
        
        logger.error(f"GitHub OAuth response - status: {access_token_response.status_code}, body: {access_token_response.text}")
        
        if access_token_response.status_code != 200:
            raise ParseError(f"Failed to get access token from GitHub. Status: {access_token_response.status_code}, Response: {access_token_response.text}")
        
        access_token_data = access_token_response.json()
        access_token = access_token_data.get("access_token")
        if not access_token:
            error_description = access_token_data.get("error_description", "Unknown error")
            raise ParseError(f"Access token not found in GitHub response: {error_description}, Full response: {access_token_data}")
        
        # GitHub 사용자 정보 요청
        user_response = requests.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        
        if user_response.status_code != 200:
            raise ParseError("Failed to get user info from GitHub.")
        
        user_data = user_response.json()
        github_id = str(user_data.get("id"))
        github_username = user_data.get("login")
        github_email = user_data.get("email")
        github_avatar = user_data.get("avatar_url", "")
        
        # 사용자 찾기 또는 생성
        try:
            user = User.objects.get(username=github_id)
        except User.DoesNotExist:
            user = User.objects.create(
                username=github_id,
                email=github_email or f"{github_id}@github.com",
                name=user_data.get("name", github_username),
                avatar=github_avatar,
            )
            user.set_unusable_password()
            user.save()
        
        # 세션 로그인
        login(request, user)
        return Response({"ok": True})

class KakaoLogIn(APIView):

    permission_classes = [AllowAny]
    authentication_classes = []  # CSRF 검증 우회

    def post(self, request):
        # 디버깅: 요청 데이터 확인
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Kakao callback - request.data: {request.data}, request.POST: {request.POST}, Content-Type: {request.content_type}")
        
        # 프론트엔드에서 보낸 code 확인 (JSON 또는 form-data 모두 지원)
        code = request.data.get("code") or request.POST.get("code")
        if not code:
            # 디버깅: 요청 데이터 확인
            error_msg = f"code is required. Received data: {dict(request.data)}, POST: {dict(request.POST)}, Content-Type: {request.content_type}"
            logger.error(error_msg)
            raise ParseError(error_msg)
        
        # 카카오 액세스 토큰 요청
        client_id = settings.KAKAO_CLIENT_ID
        client_secret = settings.KAKAO_CLIENT_SECRET
        redirect_uri = settings.KAKAO_REDIRECT_URI
        
        logger.error(f"Kakao OAuth - client_id: {client_id[:10] if client_id else 'EMPTY'}..., client_secret: {'***' if client_secret else 'EMPTY'}, code: {code}")
        
        access_token_response = requests.post(
            "https://kauth.kakao.com/oauth/token",
            data={
                "grant_type": "authorization_code",
                "client_id": client_id,
                "client_secret": client_secret,
                "code": code,
                "redirect_uri": redirect_uri,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        
        logger.error(f"Kakao OAuth response - status: {access_token_response.status_code}, body: {access_token_response.text}")
        
        if access_token_response.status_code != 200:
            raise ParseError(f"Failed to get access token from Kakao. Status: {access_token_response.status_code}, Response: {access_token_response.text}")
        
        access_token_data = access_token_response.json()
        access_token = access_token_data.get("access_token")
        if not access_token:
            error_description = access_token_data.get("error_description", "Unknown error")
            raise ParseError(f"Access token not found in Kakao response: {error_description}, Full response: {access_token_data}")
        
        # 카카오 사용자 정보 요청
        user_response = requests.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        
        if user_response.status_code != 200:
            raise ParseError("Failed to get user info from Kakao.")
        
        user_data = user_response.json()
        kakao_id = str(user_data.get("id"))
        kakao_account = user_data.get("kakao_account", {})
        kakao_email = kakao_account.get("email", "")
        kakao_profile = kakao_account.get("profile", {})
        kakao_nickname = kakao_profile.get("nickname", "")
        kakao_avatar = kakao_profile.get("profile_image_url", "")
        
        # 사용자 찾기 또는 생성
        try:
            user = User.objects.get(username=kakao_id)
        except User.DoesNotExist:
            user = User.objects.create(
                username=kakao_id,
                email=kakao_email or f"{kakao_id}@kakao.com",
                name=kakao_nickname or f"kakao_{kakao_id}",
                avatar=kakao_avatar,
            )
            user.set_unusable_password()
            user.save()
        
        # 세션 로그인
        login(request, user)
        return Response({"ok": True})
