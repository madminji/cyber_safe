from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from .models import GameChoice, GameSession, GameTurn


RISK_KEYWORDS = {
    "ru": (
        "хорошо",
        "ок",
        "да",
        "установ",
        "скача",
        "откро",
        "перейд",
        "код",
        "парол",
        "паспорт",
        "карт",
        "отправ",
        "перешл",
        "скажу",
        "введ",
    ),
    "uz": (
        "ha",
        "xo'p",
        "mayli",
        "o'rnat",
        "yukla",
        "och",
        "kod",
        "parol",
        "pasport",
        "karta",
        "yubor",
        "kirit",
    ),
}

SAFE_KEYWORDS = {
    "ru": (
        "не буду",
        "не установ",
        "удал",
        "официаль",
        "сам провер",
        "проверю",
        "сайт",
        "приложение банка",
        "поддержк",
        "заблок",
        "позвоню",
        "не перейд",
        "не откро",
    ),
    "uz": (
        "o'rnatmay",
        "yuklamay",
        "o'chir",
        "rasmiy",
        "tekshir",
        "sayt",
        "qo'llab-quvvatlash",
        "blok",
        "qo'ng'iroq",
        "ochmay",
    ),
}


def localized(obj, field, language):
    return getattr(obj, f"{field}_{language}")


def infer_choice_from_custom_text(*, step, custom_text, language):
    text = custom_text.strip().lower()
    choices = list(step.choices.all())
    if not text or not choices:
        return None

    safest = max(choices, key=lambda choice: choice.points)
    riskiest = min(choices, key=lambda choice: choice.points)
    middle = sorted(choices, key=lambda choice: choice.points)[len(choices) // 2]

    safe_score = sum(1 for keyword in SAFE_KEYWORDS[language] if keyword in text)
    risk_score = sum(1 for keyword in RISK_KEYWORDS[language] if keyword in text)

    if safe_score > risk_score:
        return safest
    if risk_score > safe_score:
        return riskiest

    for choice in choices:
        choice_text = localized(choice, "text", language).lower()
        choice_words = [
            word.strip(".,!?;:()«»\"'")
            for word in choice_text.split()
            if len(word.strip(".,!?;:()«»\"'")) >= 5
        ]
        if any(word in text for word in choice_words):
            return choice

    return middle


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
def answer_game_step(*, session, user, choice_id=None, custom_text=""):
    locked = GameSession.objects.select_for_update().select_related(
        "scenario",
        "current_step",
    ).get(id=session.id)
    if locked.user_id != user.id:
        raise ValidationError("Game session not found.")
    if locked.status != GameSession.Status.ACTIVE or locked.current_step_id is None:
        raise ValidationError("Game session has already been completed.")
    if choice_id:
        try:
            choice = GameChoice.objects.get(
                id=choice_id,
                step=locked.current_step,
            )
        except GameChoice.DoesNotExist as exc:
            raise ValidationError("Selected answer does not belong to this step.") from exc
    else:
        choice = infer_choice_from_custom_text(
            step=locked.current_step,
            custom_text=custom_text,
            language=locked.language,
        )
        if choice is None:
            raise ValidationError("Write your answer or choose one of the strategies.")

    GameTurn.objects.create(
        session=locked,
        step=locked.current_step,
        choice=choice,
        custom_text=custom_text[:600],
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
