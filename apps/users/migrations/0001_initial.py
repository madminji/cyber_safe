import uuid

from django.db import migrations, models

import apps.users.managers


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="OTPChallenge",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("phone_hash", models.CharField(db_index=True, max_length=64)),
                ("phone_encrypted", models.TextField()),
                ("phone_masked", models.CharField(max_length=13)),
                ("code_hash", models.CharField(max_length=64)),
                (
                    "purpose",
                    models.CharField(
                        choices=[("authenticate", "Authenticate")],
                        default="authenticate",
                        max_length=20,
                    ),
                ),
                ("full_name", models.CharField(blank=True, max_length=150)),
                ("region", models.CharField(blank=True, max_length=30)),
                (
                    "language",
                    models.CharField(
                        choices=[("ru", "Русский"), ("uz", "O‘zbekcha")],
                        default="ru",
                        max_length=5,
                    ),
                ),
                ("attempts", models.PositiveSmallIntegerField(default=0)),
                ("expires_at", models.DateTimeField()),
                ("used_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="User",
            fields=[
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(blank=True, null=True, verbose_name="last login"),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text=(
                            "Designates that this user has all permissions without "
                            "explicitly assigning them."
                        ),
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("phone_hash", models.CharField(max_length=64, unique=True)),
                ("phone_encrypted", models.TextField()),
                ("phone_masked", models.CharField(max_length=13)),
                ("full_name", models.CharField(blank=True, max_length=150)),
                ("region", models.CharField(blank=True, max_length=30)),
                (
                    "language",
                    models.CharField(
                        choices=[("ru", "Русский"), ("uz", "O‘zbekcha")],
                        default="ru",
                        max_length=5,
                    ),
                ),
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("citizen", "Citizen"),
                            ("moderator", "Moderator"),
                            ("admin", "Admin"),
                        ],
                        default="citizen",
                        max_length=20,
                    ),
                ),
                ("is_verified", models.BooleanField(default=False)),
                ("is_active", models.BooleanField(default=True)),
                ("is_staff", models.BooleanField(default=False)),
                ("points", models.PositiveIntegerField(default=0)),
                ("date_joined", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text=(
                            "The groups this user belongs to. A user will get all "
                            "permissions granted to each of their groups."
                        ),
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={"abstract": False},
            managers=[
                ("objects", apps.users.managers.UserManager()),
            ],
        ),
        migrations.AddIndex(
            model_name="otpchallenge",
            index=models.Index(
                fields=["phone_hash", "-created_at"],
                name="users_otpch_phone_h_8326e0_idx",
            ),
        ),
    ]
