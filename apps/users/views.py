from django.conf import settings
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from .serializers import (
    LogoutSerializer,
    RequestOTPSerializer,
    UserSerializer,
    VerifyOTPSerializer,
)


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
