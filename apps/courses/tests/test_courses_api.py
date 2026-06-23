import pytest
from django.core.management import call_command
from django.urls import reverse
from rest_framework.test import APIClient

from apps.courses.models import Course, LessonProgress
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
