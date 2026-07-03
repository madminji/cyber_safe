from django.core.management.base import BaseCommand

from apps.courses.metadata import COURSE_METADATA
from apps.courses.models import Course


class Command(BaseCommand):
    help = "Synchronize localized metadata for the three CyberSafe course levels."

    def handle(self, *args, **options):
        updated = 0
        missing = []
        for slug, metadata in COURSE_METADATA.items():
            fields = {
                "title_ru": metadata["title_ru"],
                "title_uz": metadata["title_uz"],
                "description_ru": metadata["description_ru"],
                "description_uz": metadata["description_uz"],
                "level": metadata["level"],
                "order": metadata["order"],
                "is_published": True,
            }
            count = Course.objects.filter(slug=slug).update(**fields)
            if count:
                updated += count
            else:
                missing.append(slug)

        message = f"Updated {updated} course metadata records."
        if missing:
            message += f" Missing courses: {', '.join(missing)}."
        self.stdout.write(self.style.SUCCESS(message))
