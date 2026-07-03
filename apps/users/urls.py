from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    AdminUserDetailView,
    AdminUserListView,
    LeaderboardView,
    LogoutView,
    MeView,
    RequestOTPView,
    VerifyOTPView,
)

urlpatterns = [
    path("request-otp/", RequestOTPView.as_view(), name="request-otp"),
    path("verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", MeView.as_view(), name="me"),
    path("leaderboard/", LeaderboardView.as_view(), name="user-leaderboard"),
    path("admin/users/", AdminUserListView.as_view(), name="admin-user-list"),
    path(
        "admin/users/<uuid:user_id>/",
        AdminUserDetailView.as_view(),
        name="admin-user-detail",
    ),
]
