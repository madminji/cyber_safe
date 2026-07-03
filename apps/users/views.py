from django.conf import settings
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from apps.core.permissions import IsAdmin

from .serializers import (
    AdminUserSerializer,
    LeaderboardEntrySerializer,
    LogoutSerializer,
    RequestOTPSerializer,
    UserSerializer,
    VerifyOTPSerializer,
)
from .models import User


class RequestOTPView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = RequestOTPSerializer

    @extend_schema(request=RequestOTPSerializer)
    def post(self, request):
        serializer = RequestOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        challenge, code = serializer.save()
        data = {
            "challenge_id": challenge.id,
            "expires_in": settings.OTP_TTL_SECONDS,
            "message": "OTP sent if the phone number is eligible.",
        }
        if settings.OTP_ECHO_IN_RESPONSE:
            data["development_otp"] = code
        return Response(data, status=status.HTTP_201_CREATED)


class VerifyOTPView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = VerifyOTPSerializer

    @extend_schema(request=VerifyOTPSerializer)
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, tokens = serializer.save()
        return Response(
            {
                **tokens,
                "user": UserSerializer(user).data,
            }
        )


class MeView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    @extend_schema(request=UserSerializer)
    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class AdminUserListView(ListAPIView):
    permission_classes = [IsAdmin]
    serializer_class = AdminUserSerializer

    def get_queryset(self):
        queryset = User.objects.order_by("-points", "date_joined")
        role = self.request.query_params.get("role")
        if role in User.Role.values:
            queryset = queryset.filter(role=role)
        search = self.request.query_params.get("search", "").strip()
        if search:
            queryset = queryset.filter(full_name__icontains=search)
        return queryset


class AdminUserDetailView(GenericAPIView):
    permission_classes = [IsAdmin]
    serializer_class = AdminUserSerializer

    def get_object(self, user_id):
        return User.objects.get(id=user_id)

    def patch(self, request, user_id):
        try:
            user = self.get_object(user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=404)
        serializer = self.get_serializer(
            user,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LeaderboardView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = LeaderboardEntrySerializer

    @extend_schema(operation_id="users_leaderboard")
    def get(self, request):
        users = User.objects.filter(is_active=True).order_by("-points", "date_joined")[
            :50
        ]
        current_user_id = request.user.id if request.user.is_authenticated else None
        rows = [
            {
                "rank": index,
                "user_name": user.full_name or user.phone_masked,
                "points": user.points,
                "is_current_user": user.id == current_user_id,
            }
            for index, user in enumerate(users, start=1)
        ]
        return Response(self.get_serializer(rows, many=True).data)


class LogoutView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LogoutSerializer

    @extend_schema(request=LogoutSerializer, responses={204: None})
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            RefreshToken(serializer.validated_data["refresh"]).blacklist()
        except TokenError:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_204_NO_CONTENT)
