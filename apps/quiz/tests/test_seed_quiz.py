import pytest
from django.core.management import call_command

from apps.quiz.models import TestAnswer as QuizAnswer
from apps.quiz.services import start_test, submit_test


@pytest.mark.django_db
def test_seed_quiz_preserves_choices_used_by_completed_tests():
    call_command("seed_quiz")
    session = start_test(user=None, language="ru")
    answers = [
        {
            "question_id": item.question_id,
            "choice_id": item.question.choices.first().id,
        }
        for item in session.session_questions.all()
    ]
    submit_test(
        session_id=session.id,
        actor=type("AnonymousActor", (), {"is_authenticated": False})(),
        answers=answers,
        duration_seconds=30,
    )
    answer_choice_ids = set(QuizAnswer.objects.values_list("choice_id", flat=True))

    call_command("seed_quiz")

    assert answer_choice_ids == set(
        QuizAnswer.objects.values_list("choice_id", flat=True)
    )
