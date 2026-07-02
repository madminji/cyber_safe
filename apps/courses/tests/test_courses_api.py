import json

import pytest
from django.core.management import call_command
from django.urls import reverse
from rest_framework.test import APIClient

from apps.courses.models import (
    Course,
    Lesson,
    LessonBlock,
    LessonChoice,
    LessonProgress,
    LessonQuestion,
    LessonTask,
)
from apps.users.models import User


@pytest.fixture
def seeded_course():
    call_command("seed_courses")
    return Course.objects.get(slug="digital-safety-basics")


@pytest.fixture
def user():
    return User.objects.create_user(
        phone="+998901234567",
        full_name="Course Student",
        is_verified=True,
    )


def auth_client(user):
    client = APIClient()
    client.force_authenticate(user)
    return client


@pytest.fixture
def admin_user():
    return User.objects.create_superuser(
        phone="+998901111111",
        full_name="Course Admin",
        password="admin-pass",
    )


@pytest.fixture
def import_course():
    return Course.objects.create(
        slug="cybersafe-basic",
        title_ru="CyberSafe Basic",
        title_uz="CyberSafe Basic",
        description_ru="Base course",
        description_uz="Base course",
        level=Course.Level.BASIC,
        is_published=True,
        order=1,
    )


def lesson_import_payload(course_slug="cybersafe-basic"):
    return {
        "course_slug": course_slug,
        "lesson_slug": "safe-clicking",
        "module": {
            "slug": "phishing",
            "title": {"ru": "Модуль 1. Фишинг", "uz": "1-modul. Fishing"},
        },
        "order": 1,
        "title": {"ru": "Безопасный клик", "uz": "Xavfsiz bosish"},
        "summary": {
            "ru": "Как проверять ссылки перед переходом.",
            "uz": "Havolalarni bosishdan oldin tekshirish.",
        },
        "content": {
            "ru": "Фишинговые ссылки часто маскируются под банки и доставки.",
            "uz": "Fishing havolalari ko‘pincha bank va yetkazib berish xizmatlari sifatida yashiriladi.",
        },
        "blocks": [
            {
                "type": "definition",
                "order": 1,
                "title": {"ru": "Определение", "uz": "Ta’rif"},
                "body": {
                    "ru": "Фишинг — это обман для получения данных.",
                    "uz": "Fishing — ma’lumotlarni olish uchun aldov.",
                },
            },
            {
                "type": "checklist",
                "order": 2,
                "title": {"ru": "Проверка", "uz": "Tekshirish"},
                "items": ["Проверьте домен", "Не вводите SMS-код"],
            },
        ],
        "tasks": [
            {
                "type": "text",
                "title": {"ru": "Своё правило", "uz": "Shaxsiy qoida"},
                "instruction": {
                    "ru": "Запишите одно правило безопасного клика.",
                    "uz": "Xavfsiz bosish bo‘yicha bitta qoida yozing.",
                },
            }
        ],
        "quiz": [
            {
                "text": {
                    "ru": "Что делать со ссылкой из подозрительного SMS?",
                    "uz": "Shubhali SMS havolasi bilan nima qilish kerak?",
                },
                "choices": [
                    {
                        "text": {"ru": "Открыть сразу", "uz": "Darhol ochish"},
                        "is_correct": False,
                    },
                    {
                        "text": {
                            "ru": "Проверить через официальный сайт",
                            "uz": "Rasmiy sayt orqali tekshirish",
                        },
                        "is_correct": True,
                    },
                ],
                "explanation": {
                    "ru": "Официальный сайт или приложение безопаснее ссылки из сообщения.",
                    "uz": "Rasmiy sayt yoki ilova xabardagi havoladan xavfsizroq.",
                },
            }
        ],
    }


@pytest.mark.django_db
def test_course_catalog_is_public_and_has_zero_anonymous_progress(seeded_course):
    response = APIClient().get(reverse("course-list"))

    assert response.status_code == 200
    assert response.data[0]["title"] == "Основы цифровой безопасности"
    assert response.data[0]["lessons_count"] == 8
    assert response.data[0]["completed_lessons"] == 0
    assert response.data[0]["progress_percent"] == 0


@pytest.mark.django_db
def test_lesson_requires_authentication(seeded_course):
    lesson = seeded_course.lessons.first()

    response = APIClient().get(reverse("lesson-detail", kwargs={"lesson_id": lesson.id}))

    assert response.status_code == 401


@pytest.mark.django_db
def test_correct_answer_completes_lesson_and_awards_points_once(seeded_course, user):
    lesson = seeded_course.lessons.first()
    correct_choice = lesson.question.choices.get(is_correct=True)
    client = auth_client(user)
    url = reverse("lesson-answer", kwargs={"lesson_id": lesson.id})

    first = client.post(url, {"choice_id": correct_choice.id}, format="json")
    second = client.post(url, {"choice_id": correct_choice.id}, format="json")

    assert first.status_code == 200
    assert first.data["correct"] is True
    assert first.data["completed_now"] is True
    assert second.data["completed_now"] is False
    user.refresh_from_db()
    assert user.points == 10
    assert LessonProgress.objects.filter(user=user, lesson=lesson).count() == 1


@pytest.mark.django_db
def test_lesson_detail_contains_course_navigation_and_module(seeded_course, user):
    lesson = seeded_course.lessons.first()
    response = auth_client(user).get(
        reverse("lesson-detail", kwargs={"lesson_id": lesson.id}),
        {"language": "ru"},
    )

    assert response.status_code == 200
    assert response.data["course_title"] == seeded_course.title_ru
    assert len(response.data["course_lessons"]) == 8
    assert response.data["course_lessons"][0]["module_title"].startswith("Модуль")


@pytest.mark.django_db
def test_wrong_answer_does_not_complete_lesson(seeded_course, user):
    lesson = seeded_course.lessons.first()
    wrong_choice = lesson.question.choices.filter(is_correct=False).first()

    response = auth_client(user).post(
        reverse("lesson-answer", kwargs={"lesson_id": lesson.id}),
        {"choice_id": wrong_choice.id},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["correct"] is False
    assert LessonProgress.objects.count() == 0


@pytest.mark.django_db
def test_course_progress_is_calculated_for_authenticated_user(seeded_course, user):
    lesson = seeded_course.lessons.first()
    LessonProgress.objects.create(user=user, lesson=lesson)

    response = auth_client(user).get(reverse("course-list"))

    assert response.status_code == 200
    assert response.data[0]["completed_lessons"] == 1
    assert response.data[0]["progress_percent"] == 12


@pytest.mark.django_db
def test_lesson_import_requires_admin(import_course, user):
    response = auth_client(user).post(
        reverse("admin-lesson-import"),
        {"payload": lesson_import_payload()},
        format="json",
    )

    assert response.status_code == 403
    assert Lesson.objects.count() == 0


@pytest.mark.django_db
def test_admin_can_import_lesson_payload(import_course, admin_user):
    response = auth_client(admin_user).post(
        reverse("admin-lesson-import"),
        {"payload": lesson_import_payload()},
        format="json",
    )

    assert response.status_code == 201
    assert response.data["status"] == "created"
    assert response.data["blocks_count"] == 2
    assert response.data["tasks_count"] == 1
    assert response.data["questions_count"] == 1

    lesson = Lesson.objects.get(slug="safe-clicking")
    assert lesson.course == import_course
    assert lesson.module_slug == "phishing"
    assert lesson.questions.count() == 1
    assert lesson.questions.first().choices.count() == 2
    assert LessonBlock.objects.filter(lesson=lesson).count() == 2
    assert LessonTask.objects.filter(lesson=lesson).count() == 1


@pytest.mark.django_db
def test_lesson_import_updates_existing_lesson_without_duplicates(import_course, admin_user):
    client = auth_client(admin_user)
    url = reverse("admin-lesson-import")
    first_payload = lesson_import_payload()
    second_payload = lesson_import_payload()
    second_payload["title"]["ru"] = "Обновлённый безопасный клик"

    first = client.post(url, {"payload": first_payload}, format="json")
    second = client.post(url, {"payload": second_payload}, format="json")

    assert first.status_code == 201
    assert second.status_code == 200
    assert second.data["status"] == "updated"
    assert Lesson.objects.count() == 1
    lesson = Lesson.objects.get()
    assert lesson.title_ru == "Обновлённый безопасный клик"
    assert lesson.blocks.count() == 2
    assert lesson.tasks.count() == 1
    assert lesson.questions.count() == 1


@pytest.mark.django_db
def test_lesson_import_returns_clear_validation_errors(import_course, admin_user):
    payload = lesson_import_payload()
    del payload["title"]

    response = auth_client(admin_user).post(
        reverse("admin-lesson-import"),
        {"payload": payload},
        format="json",
    )

    assert response.status_code == 400
    assert "title" in response.data["error"]["details"]


@pytest.mark.django_db
def test_exported_lesson_json_can_be_imported_without_duplicates(import_course, tmp_path):
    lesson = Lesson.objects.create(
        course=import_course,
        slug="legacy-lesson",
        module_slug="legacy-module",
        module_title_ru="Старый модуль",
        module_title_uz="Eski modul",
        title_ru="Старый урок",
        title_uz="Eski dars",
        summary_ru="Краткое описание",
        summary_uz="Qisqa tavsif",
        content_ru="Теория старого урока",
        content_uz="Eski dars nazariyasi",
        order=1,
        duration_minutes=7,
    )
    question = LessonQuestion.objects.create(
        lesson=lesson,
        text_ru="Что безопаснее?",
        text_uz="Qaysi biri xavfsizroq?",
        explanation_ru="Проверять через официальный канал.",
        explanation_uz="Rasmiy kanal orqali tekshirish.",
    )
    LessonChoice.objects.create(
        question=question,
        text_ru="Перейти по ссылке",
        text_uz="Havolaga o‘tish",
        is_correct=False,
        order=1,
    )
    LessonChoice.objects.create(
        question=question,
        text_ru="Открыть официальный сайт",
        text_uz="Rasmiy saytni ochish",
        is_correct=True,
        order=2,
    )

    call_command("export_lessons_json", str(tmp_path), "--course", import_course.slug)
    exported_file = tmp_path / import_course.slug / "01-legacy-lesson.json"
    payload = json.loads(exported_file.read_text(encoding="utf-8"))

    assert payload["lesson_slug"] == "legacy-lesson"
    assert payload["quiz"][0]["choices"][1]["is_correct"] is True

    call_command("import_lessons_json", str(tmp_path))

    assert Lesson.objects.count() == 1
    lesson.refresh_from_db()
    assert lesson.questions.count() == 1
    assert lesson.questions.first().choices.count() == 2


@pytest.mark.django_db
def test_enrich_lessons_json_splits_content_into_blocks_and_tasks(tmp_path):
    course_dir = tmp_path / "cybersafe-basic"
    course_dir.mkdir()
    lesson_file = course_dir / "01-safe-clicking.json"
    lesson_file.write_text(
        json.dumps(
            {
                "course_slug": "cybersafe-basic",
                "lesson_slug": "safe-clicking",
                "module": {"slug": "phishing", "title": {"ru": "Модуль", "uz": "Modul"}},
                "order": 1,
                "title": {"ru": "Безопасный клик", "uz": "Xavfsiz bosish"},
                "summary": {"ru": "Описание", "uz": "Tavsif"},
                "content": {
                    "ru": (
                        "Цель урока\n\n"
                        "Понять безопасный алгоритм.\n\n"
                        "Теория\n\n"
                        "Фишинг — это попытка получить данные через обман.\n\n"
                        "Пример: сообщение просит срочно открыть ссылку.\n\n"
                        "Признаки риска\n\n"
                        "Просят SMS-код.\n\n"
                        "Что делать\n\n"
                        "Открыть официальный сайт вручную.\n\n"
                        "Практика\n\n"
                        "Задание 1. Разберите карточки с сообщениями.\n\n"
                        "Задание 2. Запишите 3 правила."
                    ),
                    "uz": "",
                },
                "blocks": [
                    {
                        "type": "theory",
                        "order": 1,
                        "title": {"ru": "Теория", "uz": "Nazariya"},
                        "body": {"ru": "Старый блок", "uz": "Eski blok"},
                    }
                ],
                "tasks": [],
                "quiz": [],
                "duration_minutes": 5,
                "is_published": True,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    call_command("enrich_lessons_json", str(tmp_path))
    payload = json.loads(lesson_file.read_text(encoding="utf-8"))

    assert [block["type"] for block in payload["blocks"]] == [
        "note",
        "definition",
        "example",
        "warning",
        "checklist",
    ]
    assert payload["tasks"][0]["type"] == "scenario"
    assert payload["tasks"][1]["type"] == "checklist"


@pytest.mark.django_db
def test_moderator_can_manage_lessons_from_content_panel(import_course, admin_user):
    lesson = Lesson.objects.create(
        course=import_course,
        slug="panel-lesson",
        title_ru="Урок панели",
        title_uz="Panel darsi",
        summary_ru="Описание",
        summary_uz="Tavsif",
        content_ru="Теория",
        content_uz="Nazariya",
        order=1,
    )
    client = auth_client(admin_user)

    content = client.get(reverse("admin-course-content"))
    exported = client.get(reverse("admin-lesson-export", kwargs={"lesson_id": lesson.id}))
    deleted = client.delete(reverse("admin-lesson-delete", kwargs={"lesson_id": lesson.id}))

    assert content.status_code == 200
    assert content.data[0]["lessons"][0]["slug"] == "panel-lesson"
    assert exported.status_code == 200
    assert exported.json()["lesson_slug"] == "panel-lesson"
    assert deleted.status_code == 204
    assert not Lesson.objects.filter(id=lesson.id).exists()


@pytest.mark.django_db
def test_citizen_cannot_delete_lesson(import_course, user):
    lesson = Lesson.objects.create(
        course=import_course,
        slug="protected-lesson",
        title_ru="Защищённый урок",
        title_uz="Himoyalangan dars",
        summary_ru="Описание",
        summary_uz="Tavsif",
        content_ru="Теория",
        content_uz="Nazariya",
        order=1,
    )

    response = auth_client(user).delete(
        reverse("admin-lesson-delete", kwargs={"lesson_id": lesson.id})
    )

    assert response.status_code == 403
    assert Lesson.objects.filter(id=lesson.id).exists()
