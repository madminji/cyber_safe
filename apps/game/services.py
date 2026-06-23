from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from .models import GameChoice, GameSession, GameTurn


@transaction.atomic
def start_game(*, user, scenario, language):
    first_step = scenario.steps.order_by("order").first()
    if first_step is None:
        raise ValidationError("Scenario has no steps.")
    max_score = sum(
        max(step.choices.values_list("points", flat=True), default=0)
        for step in scenario.steps.prefetch_related("choices")
    )
    return GameSession.objects.create(
        user=user,
        scenario=scenario,
        current_step=first_step,
        current_message=(
            first_step.message_uz if language == "uz" else first_step.message_ru
        ),
        language=language,
        max_score=max_score,
    )


@transaction.atomic
def answer_game_step(*, session, user, choice_id):
    locked = GameSession.objects.select_for_update().select_related(
        "scenario",
        "current_step",
    ).get(id=session.id)
    if locked.user_id != user.id:
        raise ValidationError("Game session not found.")
    if locked.status != GameSession.Status.ACTIVE or locked.current_step_id is None:
        raise ValidationError("Game session has already been completed.")
    try:
        choice = GameChoice.objects.get(
            id=choice_id,
            step=locked.current_step,
        )
    except GameChoice.DoesNotExist as exc:
        raise ValidationError("Selected answer does not belong to this step.") from exc

    GameTurn.objects.create(
        session=locked,
        step=locked.current_step,
        choice=choice,
        points=choice.points,
    )
    locked.score += choice.points
    next_step = locked.scenario.steps.filter(order__gt=locked.current_step.order).first()
    completed = next_step is None
    if completed:
        locked.status = GameSession.Status.COMPLETED
        locked.current_step = None
        locked.completed_at = timezone.now()
        normalized = max(0, locked.score)
        locked.score_percent = (
            min(100, round(normalized * 100 / locked.max_score))
            if locked.max_score
            else 0
        )
        locked.points_awarded = max(0, round(locked.score_percent / 10))
        if locked.points_awarded:
            user.points += locked.points_awarded
            user.save(update_fields=["points", "updated_at"])
    else:
        locked.current_step = next_step
        locked.current_message = (
            next_step.message_uz if locked.language == "uz" else next_step.message_ru
        )
    locked.save(
        update_fields=[
            "score",
            "status",
            "current_step",
            "current_message",
            "completed_at",
            "score_percent",
            "points_awarded",
        ]
    )
    return locked, choice, completed
