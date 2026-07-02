import random

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from .models import (
    GameAction,
    GameCharacter,
    GameMission,
    GameMissionStep,
    GameScenario3D,
    GameSession3D,
    UserGameProfile,
)


DIFFICULTIES = [
    GameScenario3D.Difficulty.EASY,
    GameScenario3D.Difficulty.MEDIUM,
    GameScenario3D.Difficulty.HARD,
]


def localized(obj, field, language):
    return getattr(obj, f"{field}_{language}")


def localized_option_label(step, value, language):
    for item in step.options:
        if item.get("value") == value:
            return item.get(f"label_{language}") or item.get("label_ru") or value
    return value


def session_percent(session):
    return (
        min(100, round(max(0, session.score) * 100 / session.max_score))
        if session.max_score
        else 0
    )


def session_level(session):
    percent = session_percent(session)
    if percent >= 80:
        return "expert"
    if percent >= 55:
        return "strong"
    return "practice"


def session_review_payload(session, language):
    actions = {
        action.step_id: action
        for action in session.actions.select_related("step").all()
    }
    turns = []
    for step in session.mission.steps.all():
        action = actions.get(step.id)
        if action is None:
            continue
        feedback_field = "feedback_correct" if action.correct else "feedback_wrong"
        turns.append(
            {
                "step": step.order,
                "prompt": localized(step, "prompt", language),
                "selected_value": action.selected_value,
                "selected_label": localized_option_label(
                    step,
                    action.selected_value,
                    language,
                ),
                "correct_value": step.correct_value,
                "correct_label": localized_option_label(
                    step,
                    step.correct_value,
                    language,
                ),
                "correct": action.correct,
                "points_delta": action.points_delta,
                "feedback": localized(step, feedback_field, language),
            }
        )
    return {
        "session_id": str(session.id),
        "scenario_title": localized(session.scenario, "title", language),
        "mission_title": localized(session.mission, "title", language),
        "character_name": localized(session.character, "name", language),
        "difficulty": session.difficulty,
        "score": session.score,
        "max_score": session.max_score,
        "score_percent": session_percent(session),
        "points_awarded": session.points_awarded,
        "level": session_level(session),
        "turns": turns,
    }


def get_or_create_profile(user):
    profile, _ = UserGameProfile.objects.get_or_create(user=user)
    return profile


def choose_difficulty(*, authenticated):
    if not authenticated:
        return GameScenario3D.Difficulty.EASY
    return random.choice(DIFFICULTIES)


@transaction.atomic
def save_selected_character(*, user, character_id):
    try:
        character = GameCharacter.objects.get(id=character_id, is_active=True)
    except GameCharacter.DoesNotExist as exc:
        raise ValidationError("Character not found.") from exc
    profile = get_or_create_profile(user)
    profile.selected_character = character
    profile.save(update_fields=["selected_character"])
    return profile


@transaction.atomic
def start_session(*, user, scenario_id, character_id):
    authenticated = user.is_authenticated
    scenarios = GameScenario3D.objects.filter(is_published=True)
    if not authenticated:
        scenarios = scenarios.filter(is_default=True)
    try:
        scenario = scenarios.get(id=scenario_id)
    except GameScenario3D.DoesNotExist as exc:
        raise ValidationError("Scenario not available.") from exc
    try:
        character = GameCharacter.objects.get(id=character_id, is_active=True)
    except GameCharacter.DoesNotExist as exc:
        raise ValidationError("Character not found.") from exc

    difficulty = choose_difficulty(authenticated=authenticated)
    mission = scenario.missions.filter(difficulty=difficulty).first()
    if mission is None:
        mission = scenario.missions.order_by("difficulty").first()
    if mission is None:
        raise ValidationError("Scenario has no missions.")

    max_score = sum(max(step.points, 0) for step in mission.steps.all())
    session = GameSession3D.objects.create(
        user=user if authenticated else None,
        scenario=scenario,
        mission=mission,
        character=character,
        difficulty=mission.difficulty,
        max_score=max_score,
    )
    if authenticated:
        profile = get_or_create_profile(user)
        profile.selected_character = character
        profile.last_played_at = timezone.now()
        profile.save(update_fields=["selected_character", "last_played_at"])
    return session


def _validate_session_owner(*, session, user):
    if session.user_id and (not user.is_authenticated or session.user_id != user.id):
        raise ValidationError("Game session not found.")


@transaction.atomic
def submit_action(*, session_id, user, step_id, selected_value):
    try:
        session = (
            GameSession3D.objects.select_for_update()
            .select_related("mission", "user")
            .get(id=session_id)
        )
    except GameSession3D.DoesNotExist as exc:
        raise ValidationError("Game session not found.") from exc
    _validate_session_owner(session=session, user=user)
    if session.status != GameSession3D.Status.ACTIVE:
        raise ValidationError("Game session has already been completed.")

    try:
        step = GameMissionStep.objects.get(id=step_id, mission=session.mission)
    except GameMissionStep.DoesNotExist as exc:
        raise ValidationError("Mission step not found.") from exc

    if GameAction.objects.filter(session=session, step=step).exists():
        raise ValidationError("This mission step was already answered.")

    allowed_values = {item.get("value") for item in step.options}
    if selected_value not in allowed_values:
        raise ValidationError("Selected object does not belong to this mission step.")

    correct = selected_value == step.correct_value
    points_delta = step.points if correct else step.penalty
    GameAction.objects.create(
        session=session,
        step=step,
        selected_value=selected_value[:300],
        correct=correct,
        points_delta=points_delta,
    )
    session.score += points_delta
    session.save(update_fields=["score"])
    completed = session.actions.count() >= session.mission.steps.count()
    return session, step, correct, points_delta, completed


@transaction.atomic
def complete_session(*, session_id, user):
    try:
        session = (
            GameSession3D.objects.select_for_update()
            .select_related("user", "mission")
            .get(id=session_id)
        )
    except GameSession3D.DoesNotExist as exc:
        raise ValidationError("Game session not found.") from exc
    _validate_session_owner(session=session, user=user)

    if session.status == GameSession3D.Status.COMPLETED:
        return session
    if session.actions.count() < session.mission.steps.count():
        raise ValidationError("Mission is not completed.")

    session.status = GameSession3D.Status.COMPLETED
    session.completed_at = timezone.now()
    normalized = max(0, session.score)
    session.points_awarded = (
        min(100, round(normalized * 100 / session.max_score)) // 10
        if session.max_score
        else 0
    )
    session.save(update_fields=["status", "completed_at", "points_awarded"])

    if session.user_id:
        profile = get_or_create_profile(session.user)
        profile.total_score += max(0, session.score)
        profile.missions_completed += 1
        profile.last_played_at = timezone.now()
        profile.save(
            update_fields=["total_score", "missions_completed", "last_played_at"]
        )
        if session.points_awarded:
            session.user.points += session.points_awarded
            session.user.save(update_fields=["points", "updated_at"])
    return session
