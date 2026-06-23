from django.contrib.auth.base_user import BaseUserManager

from .phone import build_phone_fields


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, phone=None, full_name="", password=None, **extra_fields):
        phone = phone or extra_fields.pop("phone_hash", None)
        if not phone:
            raise ValueError("Phone number is required")

        phone_fields = build_phone_fields(phone)
        user = self.model(full_name=full_name, **phone_fields, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, phone=None, full_name="", password=None, **extra_fields):
        phone = phone or extra_fields.pop("phone_hash", None)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_verified", True)
        extra_fields.setdefault("role", "admin")

        if not password:
            raise ValueError("Superusers must have a password")
        return self.create_user(phone, full_name, password, **extra_fields)
