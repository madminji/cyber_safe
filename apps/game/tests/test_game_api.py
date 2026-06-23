import pytest
from django.core.management import call_command
from django.urls import reverse
from rest_framework.test import APIClient

from apps.game.models import GameScenario, GameSession, GameTurn
from apps.users.models import User


@pytest.fixture
def scenario():
    call_command("seed_game")
    return GameScenario.objects.get(slug="fake-bank-security-call")


@pytest.fixture
def user():
    return User.objects.create_user(
        phone="+998901234567",
        full_name="Game Player",
        is_verified=True,
    )


def client_for(user):
    client = APIClient()
    client.force_authenticate(user)
    return client


@pytest.mark.django_db
def test_scenario_list_is_public(scenario):
    response = APIClient().get(reverse("game-scenarios"))

    assert response.status_code == 200
    assert response.data[0]["steps_count"] >= 2
    assert "points" not in str(response.data)


@pytest.mark.django_db
def test_start_requires_authentication(scenario):
    response = APIClient().post(
        reverse("game-start"),
        {"scenario_id": scenario.id, "language": "ru"},
        format="json",
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_safe_choices_complete_game_and_award_points_once(scenario, user):
    client = client_for(user)
    started = client.post(
        reverse("game-start"),
        {"scenario_id": scenario.id, "language": "ru"},
        format="json",
    )
    session_id = started.data["id"]
    state = started.data
    while state["status"] == GameSession.Status.ACTIVE:
        current_step = scenario.steps.get(order=state["step_number"])
        safest = current_step.choices.order_by("-points").first()
        response = client.post(
            reverse("game-answer", kwargs={"session_id": session_id}),
            {"choice_id": safest.id},
            format="json",
        )
        assert response.status_code == 200
        state = response.data["session"]

    result = client.get(reverse("game-result", kwargs={"session_id": session_id}))
    assert result.status_code == 200
    assert result.data["score_percent"] == 100
    assert result.data["level"] == "expert"
    user.refresh_from_db()
    assert user.points == result.data["points_awarded"]

    repeated = client.post(
        reverse("game-answer", kwargs={"session_id": session_id}),
        {"choice_id": scenario.steps.first().choices.first().id},
        format="json",
    )
    assert repeated.status_code == 400
    user.refresh_from_db()
    assert user.points == result.data["points_awarded"]


@pytest.mark.django_db
def test_choice_from_another_step_is_rejected(scenario, user):
    client = client_for(user)
    started = client.post(
        reverse("game-start"),
        {"scenario_id": scenario.id, "language": "ru"},
        format="json",
    )
    wrong_choice = scenario.steps.last().choices.first()

    response = client.post(
        reverse("game-answer", kwargs={"session_id": started.data["id"]}),
        {"choice_id": wrong_choice.id},
        format="json",
    )

    assert response.status_code == 400
    assert GameTurn.objects.count() == 0


@pytest.mark.django_db
def test_other_user_cannot_access_session(scenario, user):
    owner = client_for(user)
    started = owner.post(
        reverse("game-start"),
        {"scenario_id": scenario.id, "language": "ru"},
        format="json",
    )
    stranger = User.objects.create_user(
        phone="+998911234567",
        full_name="Stranger",
        is_verified=True,
    )

    response = client_for(stranger).get(
        reverse("game-session", kwargs={"session_id": started.data["id"]})
    )

    assert response.status_code == 404

