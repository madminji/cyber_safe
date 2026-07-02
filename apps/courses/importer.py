import json
from dataclasses import dataclass
from typing import Any

from django.db import transaction
from django.utils.text import slugify
from rest_framework.exceptions import ValidationError

from .models import Course, Lesson, LessonBlock, LessonChoice, LessonQuestion, LessonTask


SUPPORTED_BLOCK_TYPES = {choice.value for choice in LessonBlock.Type}
SUPPORTED_TASK_TYPES = {choice.value for choice in LessonTask.Type}


@dataclass(frozen=True)
class LessonImportResult:
    lesson: Lesson
    created: bool
    blocks_count: int
    tasks_count: int
    questions_count: int


def parse_lesson_import_file(uploaded_file) -> dict[str, Any]:
    try:
        raw = uploaded_file.read().decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValidationError({"file": "File must be UTF-8 encoded JSON."}) from exc
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValidationError({"file": f"Invalid JSON: {exc.msg} at line {exc.lineno}."}) from exc
    if not isinstance(payload, dict):
        raise ValidationError({"file": "Top-level JSON value must be an object."})
    return payload


def _required(payload: dict[str, Any], field: str):
    value = payload.get(field)
    if value in (None, "", [], {}):
        raise ValidationError({field: "This field is required."})
    return value


def _text_pair(data: dict[str, Any], field: str, *, required: bool = True) -> tuple[str, str]:
    value = data.get(field)
    if value is None:
        if required:
            raise ValidationError({field: "This field is required."})
        return "", ""
    if isinstance(value, str):
        return value, value
    if not isinstance(value, dict):
        raise ValidationError({field: "Expected string or localized object with ru/uz."})
    ru = value.get("ru") or value.get("default") or ""
    uz = value.get("uz") or ru
    if required and not ru:
        raise ValidationError({field: "Russian text is required."})
    return str(ru), str(uz)


def _validate_ordered_list(payload: dict[str, Any], field: str) -> list[dict[str, Any]]:
    items = payload.get(field, [])
    if items in (None, ""):
        return []
    if not isinstance(items, list):
        raise ValidationError({field: "Expected a list."})
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValidationError({f"{field}.{index}": "Expected an object."})
    return items


def validate_lesson_import_payload(payload: dict[str, Any]) -> dict[str, Any]:
    course_slug = payload.get("course_slug")
    course_id = payload.get("course_id")
    if not course_slug and not course_id:
        raise ValidationError({"course": "Provide course_slug or course_id."})

    title_ru, title_uz = _text_pair(payload, "title")
    summary_ru, summary_uz = _text_pair(payload, "summary")
    content_ru, content_uz = _text_pair(payload, "content")
    order = _required(payload, "order")
    try:
        order = int(order)
    except (TypeError, ValueError) as exc:
        raise ValidationError({"order": "Order must be an integer."}) from exc
    if order < 1:
        raise ValidationError({"order": "Order must be greater than 0."})

    lesson_slug = payload.get("lesson_slug") or payload.get("slug")
    if lesson_slug:
        lesson_slug = slugify(str(lesson_slug))
    else:
        lesson_slug = slugify(title_ru)[:140]

    module = payload.get("module", {}) or {}
    if not isinstance(module, dict):
        raise ValidationError({"module": "Expected an object."})
    module_slug = slugify(str(module.get("slug", ""))) if module.get("slug") else ""
    module_title_ru, module_title_uz = _text_pair(module, "title", required=False)

    blocks = _validate_ordered_list(payload, "blocks")
    tasks = _validate_ordered_list(payload, "tasks")
    questions = _validate_ordered_list(payload, "quiz")

    for index, block in enumerate(blocks):
        block_type = block.get("type")
        if block_type not in SUPPORTED_BLOCK_TYPES:
            raise ValidationError(
                {f"blocks.{index}.type": f"Unsupported block type: {block_type}."}
            )
        _text_pair(block, "body", required=block_type not in {"checklist", "materials"})

    for index, task in enumerate(tasks):
        task_type = task.get("type", LessonTask.Type.TEXT)
        if task_type not in SUPPORTED_TASK_TYPES:
            raise ValidationError(
                {f"tasks.{index}.type": f"Unsupported task type: {task_type}."}
            )
        _text_pair(task, "title")
        _text_pair(task, "instruction")

    for q_index, question in enumerate(questions):
        _text_pair(question, "text")
        _text_pair(question, "explanation")
        choices = question.get("choices")
        if not isinstance(choices, list) or len(choices) < 2:
            raise ValidationError(
                {f"quiz.{q_index}.choices": "Each quiz question needs at least two choices."}
            )
        correct_count = 0
        for c_index, choice in enumerate(choices):
            _text_pair(choice, "text")
            if bool(choice.get("is_correct")):
                correct_count += 1
        if correct_count != 1:
            raise ValidationError(
                {f"quiz.{q_index}.choices": "Exactly one correct choice is required."}
            )

    return {
        "course_id": course_id,
        "course_slug": course_slug,
        "lesson_slug": lesson_slug,
        "module_slug": module_slug,
        "module_title_ru": module_title_ru,
        "module_title_uz": module_title_uz,
        "title_ru": title_ru,
        "title_uz": title_uz,
        "summary_ru": summary_ru,
        "summary_uz": summary_uz,
        "content_ru": content_ru,
        "content_uz": content_uz,
        "objectives": payload.get("objectives", []),
        "duration_minutes": int(payload.get("duration_minutes") or 5),
        "video_url_ru": (payload.get("video_url") or {}).get("ru", "")
        if isinstance(payload.get("video_url"), dict)
        else payload.get("video_url", ""),
        "video_url_uz": (payload.get("video_url") or {}).get("uz", "")
        if isinstance(payload.get("video_url"), dict)
        else payload.get("video_url", ""),
        "order": order,
        "is_published": bool(payload.get("is_published", True)),
        "blocks": blocks,
        "tasks": tasks,
        "quiz": questions,
        "materials": payload.get("materials", []),
    }


def _get_course(data: dict[str, Any]) -> Course:
    lookup = {"id": data["course_id"]} if data.get("course_id") else {"slug": data["course_slug"]}
    try:
        return Course.objects.get(**lookup)
    except Course.DoesNotExist as exc:
        raise ValidationError({"course": "Course was not found."}) from exc


def _block_data(block: dict[str, Any]) -> dict[str, Any]:
    data = dict(block.get("data") or {})
    for key in ("items", "language", "links"):
        if key in block:
            data[key] = block[key]
    return data


@transaction.atomic
def import_lesson_from_payload(payload: dict[str, Any]) -> LessonImportResult:
    data = validate_lesson_import_payload(payload)
    course = _get_course(data)

    lesson = None
    if data["lesson_slug"]:
        lesson = Lesson.objects.filter(course=course, slug=data["lesson_slug"]).first()
    if lesson is None:
        lesson = Lesson.objects.filter(course=course, order=data["order"]).first()

    created = lesson is None
    if created:
        lesson = Lesson(course=course)

    lesson.slug = data["lesson_slug"]
    lesson.module_slug = data["module_slug"]
    lesson.module_title_ru = data["module_title_ru"]
    lesson.module_title_uz = data["module_title_uz"]
    lesson.title_ru = data["title_ru"]
    lesson.title_uz = data["title_uz"]
    lesson.summary_ru = data["summary_ru"]
    lesson.summary_uz = data["summary_uz"]
    lesson.content_ru = data["content_ru"]
    lesson.content_uz = data["content_uz"]
    lesson.video_url_ru = data["video_url_ru"]
    lesson.video_url_uz = data["video_url_uz"]
    lesson.duration_minutes = data["duration_minutes"]
    lesson.order = data["order"]
    lesson.is_published = data["is_published"]
    lesson.save()

    lesson.blocks.all().delete()
    lesson.tasks.all().delete()
    lesson.questions.all().delete()

    blocks_to_create = []
    for index, block in enumerate(data["blocks"], start=1):
        title_ru, title_uz = _text_pair(block, "title", required=False)
        body_ru, body_uz = _text_pair(block, "body", required=False)
        blocks_to_create.append(
            LessonBlock(
                lesson=lesson,
                type=block["type"],
                title_ru=title_ru,
                title_uz=title_uz,
                body_ru=body_ru,
                body_uz=body_uz,
                data=_block_data(block),
                order=int(block.get("order") or index),
            )
        )
    if data["objectives"]:
        blocks_to_create.insert(
            0,
            LessonBlock(
                lesson=lesson,
                type=LessonBlock.Type.NOTE,
                title_ru="Цели урока",
                title_uz="Dars maqsadlari",
                data={"items": data["objectives"]},
                order=0,
            ),
        )
    if data["materials"]:
        blocks_to_create.append(
            LessonBlock(
                lesson=lesson,
                type=LessonBlock.Type.MATERIALS,
                title_ru="Дополнительные материалы",
                title_uz="Qo‘shimcha materiallar",
                data={"links": data["materials"]},
                order=len(blocks_to_create) + 1,
            )
        )
    LessonBlock.objects.bulk_create(blocks_to_create)

    tasks_to_create = []
    for index, task in enumerate(data["tasks"], start=1):
        title_ru, title_uz = _text_pair(task, "title")
        instruction_ru, instruction_uz = _text_pair(task, "instruction")
        tasks_to_create.append(
            LessonTask(
                lesson=lesson,
                type=task.get("type", LessonTask.Type.TEXT),
                title_ru=title_ru,
                title_uz=title_uz,
                instruction_ru=instruction_ru,
                instruction_uz=instruction_uz,
                data=task.get("data") or {},
                order=int(task.get("order") or index),
            )
        )
    LessonTask.objects.bulk_create(tasks_to_create)

    for q_index, question_data in enumerate(data["quiz"], start=1):
        text_ru, text_uz = _text_pair(question_data, "text")
        explanation_ru, explanation_uz = _text_pair(question_data, "explanation")
        question = LessonQuestion.objects.create(
            lesson=lesson,
            order=int(question_data.get("order") or q_index),
            text_ru=text_ru,
            text_uz=text_uz,
            explanation_ru=explanation_ru,
            explanation_uz=explanation_uz,
        )
        choices = []
        for c_index, choice_data in enumerate(question_data["choices"], start=1):
            choice_ru, choice_uz = _text_pair(choice_data, "text")
            choices.append(
                LessonChoice(
                    question=question,
                    text_ru=choice_ru,
                    text_uz=choice_uz,
                    is_correct=bool(choice_data.get("is_correct")),
                    order=int(choice_data.get("order") or c_index),
                )
            )
        LessonChoice.objects.bulk_create(choices)

    return LessonImportResult(
        lesson=lesson,
        created=created,
        blocks_count=lesson.blocks.count(),
        tasks_count=lesson.tasks.count(),
        questions_count=lesson.questions.count(),
    )
