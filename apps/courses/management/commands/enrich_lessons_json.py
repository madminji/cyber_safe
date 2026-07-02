import json
import re
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError


SECTION_TITLES = {
    "цель урока": "objectives",
    "теория": "theory",
    "признаки риска": "warning",
    "что делать": "checklist",
    "практика": "practice",
    "памятка": "note",
    "дополнительно": "note",
}


def split_paragraphs(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"\n\s*\n", text or "") if part.strip()]


def split_sections(text: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current = "intro"

    for paragraph in split_paragraphs(text):
        key = paragraph.strip().lower()
        if key in SECTION_TITLES:
            current = key
            sections.setdefault(current, [])
            continue
        sections.setdefault(current, []).append(paragraph)

    return sections


def localized(ru: str, uz: str | None = None) -> dict[str, str]:
    return {"ru": ru or "", "uz": uz or ru or ""}


def list_body(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items if item)


def extract_definition(theory_paragraphs: list[str]) -> tuple[list[dict], list[str]]:
    blocks = []
    remaining = []

    for paragraph in theory_paragraphs:
        lower = paragraph.lower()
        if " — это " in paragraph and len(paragraph) <= 360:
            title = paragraph.split(" — это ", 1)[0].strip()
            blocks.append(
                {
                    "type": "definition",
                    "order": 0,
                    "title": localized(title),
                    "body": localized(paragraph),
                }
            )
            continue
        if lower.startswith("пример:") or lower.startswith("например:"):
            blocks.append(
                {
                    "type": "example",
                    "order": 0,
                    "title": localized("Пример"),
                    "body": localized(paragraph),
                }
            )
            continue
        remaining.append(paragraph)

    return blocks, remaining


def task_from_paragraph(paragraph: str, order: int) -> dict:
    clean = re.sub(r"^Задание\s+\d+\.\s*", "", paragraph.strip(), flags=re.I)
    lower = clean.lower()

    task_type = "text"
    data: dict = {}
    if "карточ" in lower or "сообщени" in lower:
        task_type = "scenario"
        data = {
            "items": [
                {
                    "text": "Ваша карта заблокирована, срочно подтвердите данные по ссылке.",
                    "risk": "dangerous",
                },
                {
                    "text": "Вы выиграли 1 000 000 сум, отправьте паспорт.",
                    "risk": "dangerous",
                },
                {
                    "text": "Ваш заказ доставлен, трек-номер проверьте на официальном сайте.",
                    "risk": "safe",
                },
            ],
            "options": ["safe", "suspicious", "dangerous"],
        }
    elif "правил" in lower or "чек" in lower or "проверь" in lower:
        task_type = "checklist"
        data = {
            "items": [
                {"text": "Я проверяю источник через официальный канал."},
                {"text": "Я не передаю SMS-коды и пароли."},
                {"text": "Я не устанавливаю приложения из сообщений."},
            ]
        }

    return {
        "type": task_type,
        "order": order,
        "title": localized(f"Задание {order}"),
        "instruction": localized(clean),
        "data": data,
    }


def enrich_payload(payload: dict) -> dict:
    content_ru = (payload.get("content") or {}).get("ru", "")
    content_uz = (payload.get("content") or {}).get("uz", content_ru)
    sections_ru = split_sections(content_ru)
    sections_uz = split_sections(content_uz)

    blocks: list[dict] = []
    tasks: list[dict] = []
    order = 1

    intro = sections_ru.get("intro", [])
    objectives = sections_ru.get("цель урока", [])
    if intro or objectives:
        blocks.append(
            {
                "type": "note",
                "order": order,
                "title": localized("Цель урока", "Dars maqsadi"),
                "body": localized("\n\n".join(intro + objectives)),
            }
        )
        order += 1

    definition_blocks, theory_remaining = extract_definition(sections_ru.get("теория", []))
    if theory_remaining:
        blocks.append(
            {
                "type": "theory",
                "order": order,
                "title": localized("Теория", "Nazariya"),
                "body": localized("\n\n".join(theory_remaining)),
            }
        )
        order += 1

    for definition_block in definition_blocks:
        definition_block["order"] = order
        blocks.append(definition_block)
        order += 1

    risk_items = sections_ru.get("признаки риска", [])
    if risk_items:
        blocks.append(
            {
                "type": "warning",
                "order": order,
                "title": localized("Признаки риска", "Xavf belgilari"),
                "body": localized(
                    "Если вы видите один или несколько признаков ниже, остановитесь и проверьте источник."
                ),
                "items": risk_items,
            }
        )
        order += 1

    action_items = sections_ru.get("что делать", [])
    if action_items:
        blocks.append(
            {
                "type": "checklist",
                "order": order,
                "title": localized("Безопасный алгоритм", "Xavfsiz algoritm"),
                "items": action_items,
            }
        )
        order += 1

    for title in ("памятка", "дополнительно"):
        paragraphs = sections_ru.get(title, [])
        if paragraphs:
            blocks.append(
                {
                    "type": "note",
                    "order": order,
                    "title": localized(title.capitalize()),
                    "body": localized("\n\n".join(paragraphs)),
                }
            )
            order += 1

    practice_paragraphs = sections_ru.get("практика", [])
    for task_order, paragraph in enumerate(practice_paragraphs, start=1):
        tasks.append(task_from_paragraph(paragraph, task_order))

    if not blocks:
        blocks = payload.get("blocks", [])

    payload["blocks"] = blocks
    payload["tasks"] = tasks
    payload["content"] = {"ru": content_ru, "uz": content_uz}
    return payload


class Command(BaseCommand):
    help = "Split exported lesson JSON content into structured blocks and tasks."

    def add_arguments(self, parser):
        parser.add_argument(
            "path",
            nargs="?",
            default="docs/lesson_imports",
            help="JSON file or directory with exported lesson JSON files.",
        )

    def handle(self, *args, **options):
        source = Path(options["path"])
        if not source.exists():
            raise CommandError(f"Path '{source}' does not exist.")

        files = [source] if source.is_file() else sorted(source.rglob("*.json"))
        if not files:
            raise CommandError(f"No JSON files were found in '{source}'.")

        changed = 0
        for lesson_file in files:
            payload = json.loads(lesson_file.read_text(encoding="utf-8"))
            enriched = enrich_payload(payload)
            lesson_file.write_text(
                json.dumps(enriched, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            changed += 1

        self.stdout.write(self.style.SUCCESS(f"Enriched {changed} lesson JSON files."))
