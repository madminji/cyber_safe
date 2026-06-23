from django.core.management.base import BaseCommand, CommandError

from apps.users.models import User
from apps.users.phone import phone_lookup


class Command(BaseCommand):
    help = "Set a CyberSafe user role by phone number."

    def add_arguments(self, parser):
        parser.add_argument("--phone", required=True)
        parser.add_argument(
            "--role",
            required=True,
            choices=User.Role.values,
        )

    def handle(self, *args, **options):
        try:
            user = User.objects.get(phone_hash=phone_lookup(options["phone"]))
        except (User.DoesNotExist, ValueError) as exc:
            raise CommandError("User with this phone number was not found.") from exc
        user.role = options["role"]
        user.is_staff = options["role"] in {
            User.Role.MODERATOR,
            User.Role.ADMIN,
        }
        user.save(update_fields=["role", "is_staff", "updated_at"])
        self.stdout.write(
            self.style.SUCCESS(
                f"Role for {user.phone_masked} changed to {user.role}."
            )
        )
