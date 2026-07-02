import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.courses.exporter import lesson_to_payload
from apps.courses.models import Course


class Command(BaseCommand):
    help = "Export existing course lessons to the unified JSON lesson format."

    def add_arguments(self, parser):
        parser.add_argument(
            "output_dir",
            nargs="?",
            default="docs/lesson_imports",
            help="Directory where JSON lesson files will be written.",
        )
        parser.add_argument(
            "--course",
            dest="course_slug",
            help="Export only one course by slug.",
        )
        parser.add_argument(
            "--published-only",
            action="store_true",
            help="Export only published courses and published lessons.",
        )

    def handle(self, *args, **options):
        output_dir = Path(options["output_dir"])
        courses = Course.objects.prefetch_related(
            "lessons__blocks",
            "lessons__tasks",
            "lessons__questions__choices",
        )

        if options["course_slug"]:
            courses = courses.filter(slug=options["course_slug"])
            if not courses.exists():
                raise CommandError(f"Course '{options['course_slug']}' was not found.")

        if options["published_only"]:
            courses = courses.filter(is_published=True)

        exported = 0
        for course in courses:
            lessons = course.lessons.all()
            if options["published_only"]:
                lessons = lessons.filter(is_published=True)
            course_dir = output_dir / course.slug
            course_dir.mkdir(parents=True, exist_ok=True)

            for lesson in lessons:
                payload = lesson_to_payload(lesson)
                filename = f"{lesson.order:02d}-{lesson.slug or lesson.id}.json"
                target = course_dir / filename
                target.write_text(
                    json.dumps(payload, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
                exported += 1

        self.stdout.write(
            self.style.SUCCESS(f"Exported {exported} lessons to {output_dir}.")
        )
