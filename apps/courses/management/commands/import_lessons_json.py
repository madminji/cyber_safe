import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from rest_framework.exceptions import ValidationError

from apps.courses.importer import import_lesson_from_payload


class Command(BaseCommand):
    help = "Import one JSON lesson file or a directory with JSON lessons."

    def add_arguments(self, parser):
        parser.add_argument(
            "path",
            nargs="?",
            default="docs/lesson_imports",
            help="JSON file or directory with JSON lesson files.",
        )

    def handle(self, *args, **options):
        source = Path(options["path"])
        if not source.exists():
            raise CommandError(f"Path '{source}' does not exist.")

        files = [source] if source.is_file() else sorted(source.rglob("*.json"))
        if not files:
            raise CommandError(f"No JSON files were found in '{source}'.")

        created = 0
        updated = 0
        errors: list[str] = []

        for lesson_file in files:
            try:
                payload = json.loads(lesson_file.read_text(encoding="utf-8"))
                result = import_lesson_from_payload(payload)
            except json.JSONDecodeError as exc:
                errors.append(f"{lesson_file}: invalid JSON at line {exc.lineno}")
                continue
            except ValidationError as exc:
                errors.append(f"{lesson_file}: {exc.detail}")
                continue

            if result.created:
                created += 1
            else:
                updated += 1

        for error in errors:
            self.stderr.write(self.style.ERROR(error))

        if errors:
            raise CommandError(
                f"Imported with {len(errors)} errors. Created: {created}. Updated: {updated}."
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Imported {len(files)} lessons. Created: {created}. Updated: {updated}."
            )
        )
