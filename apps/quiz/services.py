import random
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.db.models import Prefetch
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.certificates.models import Certificate

from .models import Choice, Question, SessionQuestion, TestAnswer, TestSession


def score_level(score):
    if score >= 90:
        return TestSession.Level.EXPERT
    if score >= 75:
        return TestSession.Level.ADVANCED
    if score >= 60:
        return TestSession.Level.BASIC
    return TestSession.Level.NONE


@transaction.atomic
def question_bank_ids():
    return list(
        Question.objects.filter(is_active=True, choices__is_correct=True)
        .distinct()
        .values_list("id", flat=True)
    )


def create_session(*, user, language, question_ids, kind, daily_date=None):
    session = TestSession.objects.create(
        user=user if user and user.is_authenticated else None,
        language=language,
        kind=kind,
        daily_date=daily_date,
    )
    SessionQuestion.objects.bulk_create(
        [
            SessionQuestion(session=session, question_id=question_id, order=index)
            for index, question_id in enumerate(question_ids, start=1)
        ]
    )
    return get_session_with_questions(session.id)


@transaction.atomic
def start_test(*, user, language):
    question_ids = question_bank_ids()
    if not question_ids:
        raise ValidationError("The question bank is empty.")

    count = min(settings.QUIZ_QUESTION_COUNT, len(question_ids))
    selected_ids = random.sample(question_ids, count)
    return create_session(
        user=user,
        language=language,
        question_ids=selected_ids,
        kind=TestSession.Kind.STANDARD,
    )


@transaction.atomic
def start_daily_test(*, user, language):
    today = timezone.localdate()
    existing = TestSession.objects.filter(
        user=user,
        kind=TestSession.Kind.DAILY,
        daily_date=today,
    ).first()
    if existing:
        return get_session_with_questions(existing.id), False

    question_ids = question_bank_ids()
    if not question_ids:
        raise ValidationError("The question bank is empty.")
    count = min(settings.DAILY_QUIZ_QUESTION_COUNT, len(question_ids))
    generator = random.Random(f"{today.isoformat()}:{user.id}")
    selected_ids = generator.sample(question_ids, count)
    return (
        create_session(
            user=user,
            language=language,
            question_ids=selected_ids,
            kind=TestSession.Kind.DAILY,
            daily_date=today,
        ),
        True,
    )


def daily_quiz_status(user):
    today = timezone.localdate()
    sessions = TestSession.objects.filter(
        user=user,
        kind=TestSession.Kind.DAILY,
        status=TestSession.Status.COMPLETED,
    ).order_by("-daily_date")
    completed_dates = list(sessions.values_list("daily_date", flat=True))
    streak = 0
    cursor = today
    if completed_dates and completed_dates[0] != today:
        cursor = today - timedelta(days=1)
    completed_set = set(completed_dates)
    while cursor in completed_set:
        streak += 1
        cursor -= timedelta(days=1)
    today_session = TestSession.objects.filter(
        user=user,
        kind=TestSession.Kind.DAILY,
        daily_date=today,
    ).first()
    return {
        "date": today,
        "completed": bool(
            today_session and today_session.status == TestSession.Status.COMPLETED
        ),
        "started": bool(
            today_session and today_session.status == TestSession.Status.STARTED
        ),
        "session_id": today_session.id if today_session else None,
        "score": today_session.score if today_session else None,
        "streak": streak,
        "total_completed": sessions.count(),
    }


def get_session_with_questions(session_id):
    return TestSession.objects.prefetch_related(
        Prefetch(
            "session_questions",
            queryset=SessionQuestion.objects.select_related("question").prefetch_related(
                "question__choices"
            ),
        )
    ).get(id=session_id)


@transaction.atomic
def submit_test(*, session_id, actor, answers, duration_seconds):
    try:
        session = TestSession.objects.select_for_update().get(id=session_id)
    except TestSession.DoesNotExist as exc:
        raise ValidationError("Quiz session not found.") from exc

    if session.status != TestSession.Status.STARTED:
        raise ValidationError("Quiz session has already been completed.")
    if session.user_id and (not actor.is_authenticated or actor.id != session.user_id):
        raise ValidationError("Quiz session not found.")
    if session.started_at + timedelta(seconds=settings.QUIZ_SESSION_TTL_SECONDS) <= timezone.now():
        session.status = TestSession.Status.EXPIRED
        session.save(update_fields=["status"])
        raise ValidationError("Quiz session has expired.")

    expected_question_ids = set(
        session.session_questions.values_list("question_id", flat=True)
    )
    supplied_question_ids = {answer["question_id"] for answer in answers}
    if supplied_question_ids != expected_question_ids or len(answers) != len(expected_question_ids):
        raise ValidationError("Submit exactly one answer for every session question.")

    choices = {
        choice.id: choice
        for choice in Choice.objects.select_related("question").filter(
            id__in=[answer["choice_id"] for answer in answers]
        )
    }
    answer_rows = []
    correct_count = 0
    for answer in answers:
        choice = choices.get(answer["choice_id"])
        if choice is None or choice.question_id != answer["question_id"]:
            raise ValidationError("A selected choice does not belong to its question.")
        correct_count += int(choice.is_correct)
        answer_rows.append(
            TestAnswer(
                session=session,
                question_id=answer["question_id"],
                choice=choice,
                is_correct=choice.is_correct,
            )
        )

    TestAnswer.objects.bulk_create(answer_rows)
    score = round(correct_count * 100 / len(expected_question_ids))
    session.score = score
    session.level = score_level(score)
    session.duration_seconds = duration_seconds
    session.status = TestSession.Status.COMPLETED
    session.completed_at = timezone.now()
    session.save(
        update_fields=[
            "score",
            "level",
            "duration_seconds",
            "status",
            "completed_at",
        ]
    )

    certificate = None
    if session.kind == TestSession.Kind.DAILY and session.user_id:
        session.user.points += max(1, round(score / 20))
        session.user.save(update_fields=["points", "updated_at"])

    if (
        session.kind == TestSession.Kind.STANDARD
        and session.user_id
        and score >= 60
    ):
        certificate, _ = Certificate.objects.get_or_create(
            quiz_session=session,
            defaults={
                "user": session.user,
                "level": session.level,
                "score": score,
            },
        )
    return session, certificate
