import pytest
from django.core.management import call_command

from apps.users.models import User


@pytest.mark.django_db
def test_set_user_role_command_promotes_existing_user():
    user = User.objects.create_user(
        phone="+998901234567",
        full_name="Moderator Candidate",
        is_verified=True,
    )

    call_command(
        "set_user_role",
        phone="+998901234567",
        role="moderator",
    )

    user.refresh_from_db()
    assert user.role == User.Role.MODERATOR
    assert user.is_staff is True
