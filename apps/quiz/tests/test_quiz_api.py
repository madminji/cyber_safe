import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.certificates.models import Certificate
from apps.quiz.models import Choice, Question
from apps.quiz.models import TestSession as QuizSession
from apps.users.models import User


@pytest.fixture
def questions():
    created = []
    for index in range(3):
        question = Question.objects.create(
            text_ru=f"Вопрос {index}",
            text_uz=f"Savol {index}",
            category=Question.Category.PHISHING,
            difficulty=Question.Difficulty.EASY,
            explanation_ru=f"Объяснение {index}",
            explanation_uz=f"Izoh {index}",
        )
        Choice.objects.create(
            question=question,
            text_ru="Правильно",
            text_uz="To‘g‘ri",
            is_correct=True,
            order=1,
        )
        Choice.objects.create(
            question=question,
            text_ru="Неправильно",
            text_uz="Noto‘g‘ri",
            is_correct=False,
            order=2,
        )
        created.append(question)
    return created


@pytest.fixture
def authenticated_client():
    user = User.objects.create_user(
        phone="+998901234567",
        full_name="Мадина Тест",
        is_verified=True,
    )
    client = APIClient()
    client.force_authenticate(user)
    return client, user


def answer_payload(start_response, correct=True):
    answers = []
    for question_data in start_response.data["questions"]:
        question = Question.objects.get(id=question_data["id"])
        choice = question.choices.get(is_correct=correct)
        answers.append({"question_id": question.id, "choice_id": choice.id})
    return {"answers": answers, "duration_seconds": 42}


@pytest.mark.django_db
def test_anonymous_user_can_take_test_without_certificate(questions):
    client = APIClient()
    start = client.post(reverse("quiz-start"), {"language": "ru"}, format="json")

    assert start.status_code == 201
    assert "is_correct" not in str(start.data)

    submit = client.post(
        reverse("quiz-submit", kwargs={"session_id": start.data["session_id"]}),
        answer_payload(start),
        format="json",
    )

    assert submit.status_code == 200
    assert submit.data["score"] == 100
    assert submit.data["level"] == QuizSession.Level.EXPERT
    assert submit.data["certificate_id"] is None


@pytest.mark.django_db
def test_authenticated_pass_creates_verifiable_pdf_certificate(
    questions,
    authenticated_client,
):
    client, user = authenticated_client
    start = client.post(reverse("quiz-start"), {"language": "uz"}, format="json")
    submit = client.post(
        reverse("quiz-submit", kwargs={"session_id": start.data["session_id"]}),
        answer_payload(start),
        format="json",
    )

    assert submit.status_code == 200
    certificate = Certificate.objects.get(id=submit.data["certificate_id"])
    assert certificate.user == user
    assert certificate.score == 100

    verification = APIClient().get(
        reverse("certificate-detail", kwargs={"certificate_id": certificate.id})
    )
    assert verification.status_code == 200
    assert verification.data["owner_name"] == "Мадина Тест"
    assert verification.data["is_valid"] is True

    certificate_list = client.get(reverse("certificate-list"))
    assert certificate_list.status_code == 200
    assert certificate_list.data[0]["id"] == str(certificate.id)

    pdf_response = APIClient().get(
        reverse("certificate-pdf", kwargs={"certificate_id": certificate.id})
    )
    assert pdf_response.status_code == 200
    pdf_bytes = b"".join(pdf_response.streaming_content)
    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 1000


@pytest.mark.django_db
def test_failed_test_does_not_create_certificate(questions, authenticated_client):
    client, _ = authenticated_client
    start = client.post(reverse("quiz-start"), {"language": "ru"}, format="json")
    submit = client.post(
        reverse("quiz-submit", kwargs={"session_id": start.data["session_id"]}),
        answer_payload(start, correct=False),
        format="json",
    )

    assert submit.status_code == 200
    assert submit.data["score"] == 0
    assert submit.data["certificate_id"] is None
    assert Certificate.objects.count() == 0


@pytest.mark.django_db
def test_choice_from_another_question_is_rejected(questions):
    client = APIClient()
    start = client.post(reverse("quiz-start"), {"language": "ru"}, format="json")
    payload = answer_payload(start)
    first_question_id = payload["answers"][0]["question_id"]
    other_question = next(question for question in questions if question.id != first_question_id)
    other_choice = other_question.choices.first()
    payload["answers"][0]["choice_id"] = other_choice.id

    submit = client.post(
        reverse("quiz-submit", kwargs={"session_id": start.data["session_id"]}),
        payload,
        format="json",
    )

    assert submit.status_code == 400


@pytest.mark.django_db
def test_completed_session_cannot_be_submitted_twice(questions):
    client = APIClient()
    start = client.post(reverse("quiz-start"), {"language": "ru"}, format="json")
    payload = answer_payload(start)
    url = reverse("quiz-submit", kwargs={"session_id": start.data["session_id"]})

    assert client.post(url, payload, format="json").status_code == 200
    assert client.post(url, payload, format="json").status_code == 400


@pytest.mark.django_db
def test_another_user_cannot_submit_owned_session(questions, authenticated_client):
    owner_client, _ = authenticated_client
    start = owner_client.post(reverse("quiz-start"), {"language": "ru"}, format="json")
    stranger = User.objects.create_user(
        phone="+998911234567",
        full_name="Stranger",
        is_verified=True,
    )
    stranger_client = APIClient()
    stranger_client.force_authenticate(stranger)

    response = stranger_client.post(
        reverse("quiz-submit", kwargs={"session_id": start.data["session_id"]}),
        answer_payload(start),
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_daily_quiz_is_reused_once_per_day_and_tracks_status(
    questions,
    authenticated_client,
):
    client, user = authenticated_client

    first = client.post(reverse("quiz-daily"), {"language": "ru"}, format="json")
    second = client.post(reverse("quiz-daily"), {"language": "ru"}, format="json")

    assert first.status_code == 201
    assert first.data["kind"] == QuizSession.Kind.DAILY
    assert second.status_code == 200
    assert second.data["session_id"] == first.data["session_id"]

    submit = client.post(
        reverse("quiz-submit", kwargs={"session_id": first.data["session_id"]}),
        answer_payload(first),
        format="json",
    )
    assert submit.status_code == 200
    assert submit.data["kind"] == QuizSession.Kind.DAILY
    assert submit.data["certificate_id"] is None

    status = client.get(reverse("quiz-daily"))
    assert status.status_code == 200
    assert status.data["completed"] is True
    assert status.data["streak"] == 1
    user.refresh_from_db()
    assert user.points > 0
