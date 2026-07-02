import json
import logging
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings

logger = logging.getLogger(__name__)


class OpenRouterError(Exception):
    pass


def openrouter_enabled():
    return bool(settings.OPENROUTER_API_KEY)


def chat_completion(*, messages, max_tokens=180, temperature=0.7):
    if not openrouter_enabled():
        raise OpenRouterError("OpenRouter is not configured.")

    payload = json.dumps(
        {
            "model": settings.OPENROUTER_MODEL,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False,
        }
    ).encode()
    request = Request(
        settings.OPENROUTER_API_URL,
        data=payload,
        method="POST",
        headers={
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": settings.PUBLIC_SITE_URL,
            "X-OpenRouter-Title": "CyberSafe Uzbekistan",
        },
    )
    try:
        with urlopen(request, timeout=settings.OPENROUTER_TIMEOUT_SECONDS) as response:
            data = json.loads(response.read().decode())
    except HTTPError as exc:
        try:
            body = json.loads(exc.read().decode())
            message = body.get("error", {}).get("message", "OpenRouter request failed.")
        except (json.JSONDecodeError, UnicodeDecodeError):
            message = "OpenRouter request failed."
        raise OpenRouterError(message) from exc
    except (URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise OpenRouterError("OpenRouter is temporarily unavailable.") from exc

    try:
        content = data["choices"][0]["message"]["content"]
        model = data.get("model", settings.OPENROUTER_MODEL)
    except (KeyError, IndexError, TypeError) as exc:
        raise OpenRouterError("OpenRouter returned an invalid response.") from exc
    if not isinstance(content, str) or not content.strip():
        raise OpenRouterError("OpenRouter returned an empty response.")
    return content.strip(), str(model)


def localized(obj, field, language):
    return getattr(obj, f"{field}_{language}")


def generate_next_message(*, session, selected_choice, custom_text=""):
    if session.current_step_id is None:
        return None
    language_name = "Russian" if session.language == "ru" else "Uzbek"
    fallback = localized(session.current_step, "message", session.language)
    trainee_reply = custom_text or localized(selected_choice, "text", session.language)
    messages = [
        {
            "role": "system",
            "content": (
                "You generate one short line for a cybersecurity training simulation. "
                "Act as a fictional scammer using social engineering, but never provide "
                "technical hacking instructions, malware code, or real payment details. "
                f"Write only in {language_name}. Keep it under 55 words. "
                "Do not mention that this is a simulation or explain the tactic."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Scenario: {localized(session.scenario, 'title', session.language)}\n"
                f"The trainee replied: {trainee_reply}\n"
                f"Required next-step meaning: {fallback}\n"
                "Rewrite the required meaning as a natural reaction to the trainee's reply."
            ),
        },
    ]
    return chat_completion(messages=messages, max_tokens=120, temperature=0.75)


def generate_final_analysis(session):
    language_name = "Russian" if session.language == "ru" else "Uzbek"
    transcript = []
    for turn in session.turns.select_related("step", "choice").all():
        transcript.append(
            {
                "tactic": localized(turn.step, "tactic", session.language),
                "trainee_answer": turn.custom_text
                or localized(turn.choice, "text", session.language),
                "selected_safe_intent": localized(
                    turn.choice,
                    "text",
                    session.language,
                ),
                "points": turn.points,
            }
        )
    messages = [
        {
            "role": "system",
            "content": (
                "You are a cybersecurity educator. Analyze a completed social-engineering "
                "training simulation. Never shame the learner. Give 3 concise, practical "
                f"sentences in {language_name}. Do not use markdown headings."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Score: {session.score_percent}%.\n"
                f"Turns: {json.dumps(transcript, ensure_ascii=False)}\n"
                "Explain the strongest decision, the main weakness, and one action rule."
            ),
        },
    ]
    return chat_completion(messages=messages, max_tokens=180, temperature=0.35)


def enrich_game_session(*, session, selected_choice, completed):
    if not openrouter_enabled():
        return session
    try:
        if completed:
            content, model = generate_final_analysis(session)
            session.ai_analysis = content[:2000]
        else:
            content, model = generate_next_message(
                session=session,
                selected_choice=selected_choice,
                custom_text=getattr(
                    session.turns.order_by("-created_at").first(),
                    "custom_text",
                    "",
                ),
            )
            session.current_message = content[:1200]
        session.ai_model = model
        session.ai_used = True
        session.save(
            update_fields=[
                "current_message",
                "ai_analysis",
                "ai_model",
                "ai_used",
            ]
        )
    except OpenRouterError:
        logger.warning("OpenRouter game enhancement failed; local fallback was used.")
    return session
