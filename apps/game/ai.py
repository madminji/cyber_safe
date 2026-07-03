import json
import logging
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings

logger = logging.getLogger(__name__)


class OpenRouterError(Exception):
    pass


PROMPT_LEAK_MARKERS = (
    "we need",
    "i need",
    "the task",
    "required next-step",
    "trainee replied",
    "scenario:",
    "rewrite the required",
    "as a natural reaction",
    "simulation",
    "cybersecurity training",
    "one short line",
)


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


def clean_simulation_message(content, *, language):
    message = content.strip().strip("\"'“”«»")
    lowered = message.lower()
    if any(marker in lowered for marker in PROMPT_LEAK_MARKERS):
        raise OpenRouterError("OpenRouter returned prompt/meta text.")
    if "\n" in message:
        first_line = next(
            (line.strip().strip("\"'“”«»") for line in message.splitlines() if line.strip()),
            "",
        )
        if not first_line:
            raise OpenRouterError("OpenRouter returned an empty response.")
        message = first_line
        lowered = message.lower()
        if any(marker in lowered for marker in PROMPT_LEAK_MARKERS):
            raise OpenRouterError("OpenRouter returned prompt/meta text.")
    if language == "ru" and not any("а" <= char.lower() <= "я" or char == "ё" for char in message):
        raise OpenRouterError("OpenRouter returned a non-Russian response.")
    if len(message.split()) > 70:
        raise OpenRouterError("OpenRouter returned a message that is too long.")
    return message


def generate_next_message(*, session, selected_choice, custom_text=""):
    if session.current_step_id is None:
        return None
    language_name = "Russian" if session.language == "ru" else "Uzbek"
    fallback = localized(session.current_step, "message", session.language)
    trainee_reply = custom_text or localized(selected_choice, "text", session.language)
    recent_turns = []
    for turn in session.turns.select_related("step", "choice").order_by("-created_at")[:3]:
        recent_turns.append(
            {
                "sender": localized(turn.step, "message", session.language),
                "trainee": turn.custom_text
                or localized(turn.choice, "text", session.language),
            }
        )
    recent_turns.reverse()
    messages = [
        {
            "role": "system",
            "content": (
                "You write exactly one chat message from a fictional suspicious sender. "
                "Act as a fictional scammer using social engineering, but never provide "
                "technical hacking instructions, malware code, or real payment details. "
                f"Write only in {language_name}. Keep it under 55 words. "
                "If the trainee asks a question, answer it plausibly first, then steer "
                "back to the sender's goal. Use natural messenger style. "
                "Return only the message text. No reasoning, no analysis, no labels, "
                "no quotes, no markdown, no mention of scenarios or simulations."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Scenario: {localized(session.scenario, 'title', session.language)}\n"
                f"Recent dialog: {json.dumps(recent_turns, ensure_ascii=False)}\n"
                f"The trainee replied: {trainee_reply}\n"
                f"Required next-step meaning: {fallback}\n"
                "Write the next Telegram/SMS message that the suspicious sender sends. "
                "It must sound like a direct reply to the trainee."
            ),
        },
    ]
    content, model = chat_completion(messages=messages, max_tokens=120, temperature=0.75)
    return clean_simulation_message(content, language=session.language), model


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
