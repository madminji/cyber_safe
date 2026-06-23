from django.db import transaction
from rest_framework.exceptions import ValidationError

from .models import LessonChoice, LessonProgress


@transaction.atomic
def submit_lesson_answer(*, user, lesson, choice_id):
    try:
        choice = LessonChoice.objects.select_related("question").get(id=choice_id)
    except LessonChoice.DoesNotExist as exc:
        raise ValidationError("Selected answer was not found.") from exc
    if choice.question.lesson_id != lesson.id:
        raise ValidationError("Selected answer does not belong to this lesson.")

    language = user.language
    explanation = (
        choice.question.explanation_uz
        if language == "uz"
        else choice.question.explanation_ru
    )
    completed_now = False
    if choice.is_correct:
        _, completed_now = LessonProgress.objects.get_or_create(user=user, lesson=lesson)
        if completed_now:
            user.points += 10
            user.save(update_fields=["points", "updated_at"])
    return {
        "correct": choice.is_correct,
        "completed": choice.is_correct,
        "completed_now": completed_now,
        "explanation": explanation,
    }

