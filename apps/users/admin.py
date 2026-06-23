from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import OTPChallenge, User


@admin.register(User)
class CyberSafeUserAdmin(UserAdmin):
    ordering = ("-date_joined",)
    list_display = (
        "phone_masked",
        "full_name",
        "role",
        "is_verified",
        "is_staff",
        "date_joined",
    )
    search_fields = ("phone_hash", "full_name")
    readonly_fields = ("phone_hash", "phone_encrypted", "phone_masked", "date_joined", "updated_at")
    fieldsets = (
        (None, {"fields": ("phone_masked", "password")}),
        ("Profile", {"fields": ("full_name", "region", "language", "points")}),
        (
            "Permissions",
            {"fields": ("role", "is_verified", "is_active", "is_staff", "is_superuser")},
        ),
        ("Technical", {"fields": ("phone_hash", "phone_encrypted", "date_joined", "updated_at")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "phone_hash",
                    "phone_encrypted",
                    "phone_masked",
                    "password1",
                    "password2",
                ),
            },
        ),
    )


@admin.register(OTPChallenge)
class OTPChallengeAdmin(admin.ModelAdmin):
    list_display = ("phone_masked", "purpose", "attempts", "expires_at", "used_at", "created_at")
    readonly_fields = (
        "phone_hash",
        "phone_encrypted",
        "phone_masked",
        "code_hash",
        "attempts",
        "expires_at",
        "used_at",
        "created_at",
    )
