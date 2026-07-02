import pytest
from django.core.management import call_command
from django.urls import reverse
from rest_framework.test import APIClient

from apps.users.models import User
from apps.webgame.models import (
    GameCharacter,
    GameScenario3D,
    GameSession3D,
    UserGameProfile,
)


@pytest.fixture
def seeded_webgame():
    call_command("seed_webgame")


@pytest.fixture
def user():
    return User.objects.create_user(
        phone="+998901112233",
        full_name="Web Player",
        is_verified=True,
    )


def client_for(user):
    client = APIClient()
    client.force_authenticate(user)
    return client


@pytest.mark.django_db
def test_guest_sees_only_default_scenario(seeded_webgame):
    response = APIClient().get(reverse("webgame-scenarios"))

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["is_default"] is True


@pytest.mark.django_db
def test_authenticated_user_sees_all_scenarios(seeded_webgame, user):
    response = client_for(user).get(reverse("webgame-scenarios"))

    assert response.status_code == 200
    assert len(response.data) >= 4


@pytest.mark.django_db
def test_guest_can_play_default_but_score_is_not_in_leaderboard(seeded_webgame):
    client = APIClient()
    scenario = GameScenario3D.objects.get(is_default=True)
    character = GameCharacter.objects.first()

    start = client.post(
        reverse("webgame-start"),
        {"scenario_id": scenario.id, "character_id": character.id},
        format="json",
    )

    assert start.status_code == 201
    assert start.data["difficulty"] == GameScenario3D.Difficulty.EASY
    assert "correct_value" not in start.data["steps"][0]
    assert start.data["steps"][0]["options"]


@pytest.mark.django_db
def test_completed_authenticated_session_updates_profile_and_leaderboard(
    seeded_webgame,
    user,
):
    client = client_for(user)
    scenario = GameScenario3D.objects.get(is_default=True)
    character = GameCharacter.objects.first()

    start = client.post(
        reverse("webgame-start"),
        {"scenario_id": scenario.id, "character_id": character.id},
        format="json",
    )
    assert start.status_code == 201
    session_id = start.data["id"]
    session = GameSession3D.objects.select_related("mission").get(id=session_id)
    correct_values = {
        str(step.id): step.correct_value for step in session.mission.steps.all()
    }

    for step in start.data["steps"]:
        response = client.post(
            reverse("webgame-action", kwargs={"session_id": session_id}),
            {
                "mission_step_id": step["id"],
                "selected_value": correct_values[step["id"]],
            },
            format="json",
        )
        assert response.status_code == 200
        assert response.data["correct"] is True

    completed = client.post(reverse("webgame-complete", kwargs={"session_id": session_id}))

    assert completed.status_code == 200
    assert completed.data["score_percent"] == 100
    assert completed.data["turns"]
    assert completed.data["turns"][0]["selected_label"]
    assert completed.data["turns"][0]["correct_label"]
    profile = UserGameProfile.objects.get(user=user)
    assert profile.total_score > 0
    assert profile.missions_completed == 1

    result = client.get(reverse("webgame-result", kwargs={"session_id": session_id}))
    assert result.status_code == 200
    assert result.data["session_id"] == str(session_id)
    assert len(result.data["turns"]) == len(start.data["steps"])

    profile_response = client.get(reverse("webgame-profile"))
    assert profile_response.status_code == 200
    assert profile_response.data["total_score"] > 0
    assert profile_response.data["recent_sessions"]

    leaderboard = APIClient().get(reverse("webgame-leaderboard"))
    assert leaderboard.status_code == 200
    assert leaderboard.data[0]["user_name"] == "Web Player"
