import json
from unittest.mock import MagicMock, patch

import pytest
from django.test import override_settings

from apps.game.ai import OpenRouterError, chat_completion, enrich_game_session
from apps.game.models import GameScenario, GameSession
from apps.users.models import User


@override_settings(
    OPENROUTER_API_KEY="test-secret",
    OPENROUTER_MODEL="openrouter/free",
    OPENROUTER_TIMEOUT_SECONDS=3,
)
@patch("apps.game.ai.urlopen")
def test_chat_completion_uses_openrouter_contract(mock_urlopen):
    response = MagicMock()
    response.read.return_value = json.dumps(
        {
            "model": "free/test-model",
            "choices": [{"message": {"content": "Generated response"}}],
        }
    ).encode()
    mock_urlopen.return_value.__enter__.return_value = response

    content, model = chat_completion(
        messages=[{"role": "user", "content": "test"}]
    )

    assert content == "Generated response"
    assert model == "free/test-model"
    request = mock_urlopen.call_args.args[0]
    assert request.full_url == "https://openrouter.ai/api/v1/chat/completions"
    assert request.headers["Authorization"] == "Bearer test-secret"
    payload = json.loads(request.data.decode())
    assert payload["model"] == "openrouter/free"
    assert payload["stream"] is False


@override_settings(OPENROUTER_API_KEY="")
def test_chat_completion_requires_configuration():
    with pytest.raises(OpenRouterError):
        chat_completion(messages=[{"role": "user", "content": "test"}])


@pytest.mark.django_db
@override_settings(OPENROUTER_API_KEY="test-secret")
@patch("apps.game.ai.generate_next_message")
def test_ai_message_is_saved_without_changing_game_score(
    mock_generate,
):
    mock_generate.return_value = ("Personalized scammer response", "free/test-model")
    user = User.objects.create_user(
        phone="+998901234567",
        full_name="Player",
        is_verified=True,
    )
    scenario = GameScenario.objects.create(
        slug="ai-test",
        title_ru="AI test",
        title_uz="AI test",
        description_ru="Test",
        description_uz="Test",
        scam_type="bank_call",
        difficulty="easy",
        is_published=True,
    )
    first = scenario.steps.create(
        order=1,
        message_ru="First",
        message_uz="First",
        tactic_ru="Tactic",
        tactic_uz="Tactic",
    )
    choice = first.choices.create(
        text_ru="Answer",
        text_uz="Answer",
        feedback_ru="Feedback",
        feedback_uz="Feedback",
        points=10,
    )
    second = scenario.steps.create(
        order=2,
        message_ru="Fallback next",
        message_uz="Fallback next",
        tactic_ru="Tactic",
        tactic_uz="Tactic",
    )
    session = GameSession.objects.create(
        user=user,
        scenario=scenario,
        current_step=second,
        current_message="Fallback next",
        language="ru",
        score=10,
        max_score=20,
    )

    enrich_game_session(
        session=session,
        selected_choice=choice,
        completed=False,
    )

    session.refresh_from_db()
    assert session.current_message == "Personalized scammer response"
    assert session.ai_used is True
    assert session.ai_model == "free/test-model"
    assert session.score == 10


@pytest.mark.django_db
@override_settings(OPENROUTER_API_KEY="test-secret")
@patch("apps.game.ai.generate_next_message")
def test_ai_failure_keeps_local_fallback(mock_generate):
    mock_generate.side_effect = OpenRouterError("rate limited")
    user = User.objects.create_user(
        phone="+998901234567",
        full_name="Player",
        is_verified=True,
    )
    scenario = GameScenario.objects.create(
        slug="fallback-test",
        title_ru="Fallback",
        title_uz="Fallback",
        description_ru="Test",
        description_uz="Test",
        scam_type="bank_call",
        difficulty="easy",
        is_published=True,
    )
    step = scenario.steps.create(
        order=1,
        message_ru="Local fallback",
        message_uz="Local fallback",
        tactic_ru="Tactic",
        tactic_uz="Tactic",
    )
    choice = step.choices.create(
        text_ru="Answer",
        text_uz="Answer",
        feedback_ru="Feedback",
        feedback_uz="Feedback",
        points=10,
    )
    session = GameSession.objects.create(
        user=user,
        scenario=scenario,
        current_step=step,
        current_message="Local fallback",
        language="ru",
        max_score=10,
    )

    enrich_game_session(
        session=session,
        selected_choice=choice,
        completed=False,
    )

    session.refresh_from_db()
    assert session.current_message == "Local fallback"
    assert session.ai_used is False
