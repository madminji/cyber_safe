import re
import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.courses.models import Lesson, LessonBlock, LessonChoice, LessonQuestion, LessonTask


CYRILLIC_RE = re.compile(r"[А-Яа-яЁё]")


FIELD_SPECS = (
    ("lesson.title", Lesson, "title_ru", "title_uz"),
    ("lesson.summary", Lesson, "summary_ru", "summary_uz"),
    ("lesson.content", Lesson, "content_ru", "content_uz"),
    ("lesson.module_title", Lesson, "module_title_ru", "module_title_uz"),
    ("block.title", LessonBlock, "title_ru", "title_uz"),
    ("block.body", LessonBlock, "body_ru", "body_uz"),
    ("task.title", LessonTask, "title_ru", "title_uz"),
    ("task.instruction", LessonTask, "instruction_ru", "instruction_uz"),
    ("question.text", LessonQuestion, "text_ru", "text_uz"),
    ("question.explanation", LessonQuestion, "explanation_ru", "explanation_uz"),
    ("choice.text", LessonChoice, "text_ru", "text_uz"),
)


def object_label(obj) -> str:
    if isinstance(obj, Lesson):
        return f"{obj.course.slug}/{obj.order}-{obj.slug or obj.id}"
    if hasattr(obj, "lesson"):
        lesson = obj.lesson
        return f"{lesson.course.slug}/{lesson.order}-{lesson.slug or lesson.id}"
    if hasattr(obj, "question"):
        lesson = obj.question.lesson
        return f"{lesson.course.slug}/{lesson.order}-{lesson.slug or lesson.id}"
    return str(obj.pk)


class Command(BaseCommand):
    help = "Audit lesson RU/UZ localization completeness."

    def add_arguments(self, parser):
        parser.add_argument(
            "--fail-on-issues",
            action="store_true",
            help="Exit with an error when missing or suspicious Uzbek text is found.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=20,
            help="Maximum number of examples per issue type.",
        )
        parser.add_argument(
            "--json-dir",
            help="Also audit lesson JSON files in this directory.",
        )

    def handle(self, *args, **options):
        limit = options["limit"]
        total_missing = 0
        total_same = 0
        total_cyrillic = 0

        for label, model, ru_field, uz_field in FIELD_SPECS:
            missing = []
            same = []
            cyrillic = []

            for obj in model.objects.all():
                ru = (getattr(obj, ru_field) or "").strip()
                uz = (getattr(obj, uz_field) or "").strip()
                if ru and not uz:
                    missing.append(object_label(obj))
                elif ru and uz == ru:
                    same.append(object_label(obj))
                if uz and CYRILLIC_RE.search(uz):
                    cyrillic.append(object_label(obj))

            total_missing += len(missing)
            total_same += len(same)
            total_cyrillic += len(cyrillic)

            self.stdout.write(
                f"{label}: missing={len(missing)} same_as_ru={len(same)} "
                f"uz_has_cyrillic={len(cyrillic)}"
            )
            for issue_name, examples in (
                ("missing", missing),
                ("same_as_ru", same),
                ("uz_has_cyrillic", cyrillic),
            ):
                if examples:
                    shown = ", ".join(examples[:limit])
                    suffix = "" if len(examples) <= limit else f" ... +{len(examples) - limit}"
                    self.stdout.write(f"  {issue_name}: {shown}{suffix}")

        summary = (
            f"Summary: missing={total_missing}, same_as_ru={total_same}, "
            f"uz_has_cyrillic={total_cyrillic}"
        )
        if total_missing or total_same or total_cyrillic:
            self.stdout.write(self.style.WARNING(summary))
            if options["fail_on_issues"]:
                raise CommandError(summary)
        else:
            self.stdout.write(self.style.SUCCESS(summary))

        if options.get("json_dir"):
            json_missing = 0
            json_same = 0
            json_cyrillic = 0
            source = Path(options["json_dir"])
            for lesson_file in source.rglob("*.json"):
                payload = json.loads(lesson_file.read_text(encoding="utf-8"))
                pairs = [
                    (payload.get("title", {}).get("ru", ""), payload.get("title", {}).get("uz", "")),
                    (payload.get("summary", {}).get("ru", ""), payload.get("summary", {}).get("uz", "")),
                    (payload.get("content", {}).get("ru", ""), payload.get("content", {}).get("uz", "")),
                    (
                        payload.get("module", {}).get("title", {}).get("ru", ""),
                        payload.get("module", {}).get("title", {}).get("uz", ""),
                    ),
                ]
                for block in payload.get("blocks", []):
                    pairs.append((block.get("title", {}).get("ru", ""), block.get("title", {}).get("uz", "")))
                    pairs.append((block.get("body", {}).get("ru", ""), block.get("body", {}).get("uz", "")))
                for task in payload.get("tasks", []):
                    pairs.append((task.get("title", {}).get("ru", ""), task.get("title", {}).get("uz", "")))
                    pairs.append((task.get("instruction", {}).get("ru", ""), task.get("instruction", {}).get("uz", "")))
                for question in payload.get("quiz", []):
                    pairs.append((question.get("text", {}).get("ru", ""), question.get("text", {}).get("uz", "")))
                    pairs.append((question.get("explanation", {}).get("ru", ""), question.get("explanation", {}).get("uz", "")))
                    for choice in question.get("choices", []):
                        pairs.append((choice.get("text", {}).get("ru", ""), choice.get("text", {}).get("uz", "")))

                for ru, uz in pairs:
                    ru = (ru or "").strip()
                    uz = (uz or "").strip()
                    if ru and not uz:
                        json_missing += 1
                    elif ru and uz == ru:
                        json_same += 1
                    if uz and CYRILLIC_RE.search(uz):
                        json_cyrillic += 1

            json_summary = (
                f"JSON summary: missing={json_missing}, same_as_ru={json_same}, "
                f"uz_has_cyrillic={json_cyrillic}"
            )
            if json_missing or json_same or json_cyrillic:
                self.stdout.write(self.style.WARNING(json_summary))
                if options["fail_on_issues"]:
                    raise CommandError(json_summary)
            else:
                self.stdout.write(self.style.SUCCESS(json_summary))
