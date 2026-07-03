import re
import zipfile
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.courses.metadata import COURSE_LEVELS
from apps.courses.models import Course, Lesson, LessonChoice, LessonQuestion


MODULE_TITLES = {
    1: "Основы цифровой безопасности",
    2: "Фишинг: ссылки, сайты и поддельные страницы",
    3: "Телефонные звонки, SMS-коды и социальная инженерия",
    4: "Вредоносные приложения и APK-файлы",
    5: "Мошенничество на торговых площадках и в Telegram",
    6: "Государственные выплаты, документы и онлайн-займы",
    7: "Инвестиции, криптовалюта и финансовые пирамиды",
    8: "Пароли, двухфакторная защита и мессенджеры",
    9: "Инструменты платформы CyberSafe: анализатор, база номеров, репорты",
    10: "Действия при инциденте и итоговая сертификация",
}

COURSE_DESCRIPTION = (
    "Курс CyberSafe Uzbekistan учит граждан распознавать цифровое мошенничество "
    "и безопасно действовать в повседневных ситуациях: звонки “из банка”, "
    "SMS-коды, APK-файлы, фишинговые ссылки, поддельные выплаты, торговые "
    "площадки, онлайн-займы, инвестиционные схемы и защита аккаунтов."
)

UPDATED_SAFETY_NOTE = (
    "Актуальное правило безопасного поведения: не переходите по ссылкам из "
    "подозрительных SMS, писем и мессенджеров; открывайте банк, госуслуги или "
    "маркетплейс только через официальное приложение или вручную введённый адрес. "
    "Для важных аккаунтов используйте уникальный пароль, менеджер паролей, "
    "двухфакторную аутентификацию и своевременно обновляйте приложения."
)

CLEAN_MODULE_TITLES = {
    1: "Основы цифровой безопасности",
    2: "Фишинг: ссылки, сайты и поддельные страницы",
    3: "Телефонные звонки, SMS-коды и социальная инженерия",
    4: "Вредоносные приложения и APK-файлы",
    5: "Мошенничество на торговых площадках и в Telegram",
    6: "Государственные выплаты, документы и онлайн-займы",
    7: "Инвестиции, криптовалюта и финансовые пирамиды",
    8: "Пароли, двухфакторная защита и мессенджеры",
    9: "Инструменты платформы CyberSafe: анализатор, база номеров, репорты",
    10: "Действия при инциденте и итоговая сертификация",
}

SUPPLEMENTAL_LESSON_NOTES = {
    1: "Свежий акцент: современные мошенники чаще заставляют человека действовать быстро — нажать ссылку, назвать код, подтвердить перевод или установить приложение. Главное правило — остановиться, проверить источник и только потом принимать решение.",
    2: "Разделяйте данные на три зоны: публичные, только для проверенных сервисов и полностью секретные. SMS-коды, PIN, CVV, пароли, seed-фразы и коды восстановления не передаются никому.",
    3: "По рекомендациям FTC, фишинговые сообщения часто имитируют проблемы с аккаунтом, подозрительную активность, выигрыш, возврат денег, доставку или государственную выплату. Безопасный путь — не открывать ссылку из сообщения, а самостоятельно зайти на официальный сайт или в приложение.",
    4: "Практический чек: перед переходом по ссылке проверьте домен, контекст, ожидали ли вы сообщение, есть ли давление срочностью и просит ли форма секретные данные. Несколько признаков вместе — сильный сигнал опасности.",
    5: "При звонке “из банка” не спорьте и не доказывайте собеседнику, что вы правы. Самое безопасное действие — завершить разговор и самостоятельно связаться с банком через номер на карте или официальное приложение.",
    6: "Одноразовый код — это подтверждение действия от вашего имени. Если код назван мошеннику, он может подтвердить вход, перевод, смену пароля или привязку нового устройства.",
    7: "APK из Telegram, рекламы или личного сообщения особенно опасен, потому что обходит обычную проверку магазина приложений. Если для установки нужно отключить защиту телефона, это уже красный флаг.",
    8: "Базовая защита телефона — это экранная блокировка, обновления, запрет установки из неизвестных источников, проверка разрешений приложений и резервное копирование важных данных.",
    9: "В торговых сделках мошенники часто используют дефицит, низкую цену и срочность. Не переводите предоплату незнакомому продавцу, если нет защищённой сделки, истории продавца и понятных условий возврата.",
    10: "Если вы продавец, опасны ссылки “получить деньги”, “оформить доставку” или “подтвердить карту”. Деньги за товар не требуют ввода полного номера карты, CVV и SMS-кода на внешнем сайте.",
    11: "Фейковые выплаты часто копируют стиль госорганов и банков. Проверяйте объявления через официальный портал, сайт организации или приложение, а не через ссылку из пересланного сообщения.",
    12: "Фото паспорта и селфи с документом могут использоваться для регистрации сервисов или заявок на займы. Перед отправкой документов проверьте юридическое лицо, канал передачи и цель запроса.",
    13: "FTC предупреждает о схемах с обещанием высокой прибыли и минимального риска. Гарантированная доходность, давление “успей сегодня” и заработок за привлечение друзей — типичные признаки пирамиды.",
    14: "В романтических и крипто-инвестиционных схемах мошенник сначала строит доверие, а затем переводит разговор к “платформе”. Рост баланса на экране не доказывает, что деньги реально можно вывести.",
    15: "NIST рекомендует усиливать вход не только длиной пароля, но и устойчивой аутентификацией. Практичный минимум: уникальные пароли, менеджер паролей и MFA для почты, банка, Telegram и госуслуг.",
    16: "Для Telegram включите облачный пароль, проверьте активные сеансы и отключите незнакомые устройства. Код входа из SMS или Telegram нельзя пересылать даже человеку, который представился поддержкой.",
    17: "Анализатор помогает увидеть признаки риска, но не заменяет вашу проверку. Если инструмент показывает suspicious или dangerous, не переходите по ссылке и проверьте источник через официальный канал.",
    18: "Репорт полезен, когда он содержит дату, тип схемы, регион, краткую историю и скриншоты без лишних персональных данных. Не публикуйте чужие документы, полные номера карт и коды подтверждения.",
    19: "FBI подчёркивает важность быстрого сообщения о мошенничестве. Чем быстрее вы заблокируете карту, смените пароли, отключите подозрительные сеансы и сохраните доказательства, тем выше шанс снизить ущерб.",
    20: "Итоговый план должен быть конкретным: какие аккаунты защищены MFA, где хранятся пароли, какие документы нельзя отправлять в чат, кому звонить при инциденте и какие действия вы делаете в первые 15 минут после ошибки.",
}

LESSON_OBJECTIVES = {
    1: "Цель урока — понять, почему цифровая безопасность касается каждого и какие решения чаще всего защищают от мошенников.",
    2: "Цель урока — научиться отличать обычные данные от чувствительных и понимать, какие сведения нельзя отправлять в чат.",
    3: "Цель урока — научиться смотреть не только на дизайн сайта, но и на адрес, источник ссылки и смысл просьбы.",
    4: "Цель урока — потренироваться анализировать сообщение целиком: отправитель, причина, ссылка, срочность и запрашиваемые данные.",
    5: "Цель урока — научиться спокойно реагировать на звонок “из банка” и использовать правило контрольного звонка.",
    6: "Цель урока — понять, почему одноразовый код равен подтверждению действия и почему его нельзя сообщать никому.",
    7: "Цель урока — понять, чем опасны APK-файлы из мессенджеров и какие разрешения приложения особенно рискованны.",
    8: "Цель урока — настроить базовую защиту телефона и аккаунтов, которые используются каждый день.",
    9: "Цель урока — научиться проверять продавца, условия сделки и признаки фейкового объявления.",
    10: "Цель урока — распознавать поддельного покупателя и не вводить данные карты на внешних страницах.",
    11: "Цель урока — отличать настоящие выплаты от фейковых объявлений и проверять информацию через официальные каналы.",
    12: "Цель урока — понять, как документы могут использоваться против человека и как безопасно передавать копии документов.",
    13: "Цель урока — распознавать финансовые пирамиды по обещаниям высокой доходности, срочности и реферальным схемам.",
    14: "Цель урока — понять, как доверие используется в романтических и крипто-инвестиционных схемах.",
    15: "Цель урока — создать реалистичную систему паролей: уникальные пароли, менеджер паролей и защита почты.",
    16: "Цель урока — включить двухфакторную защиту и проверить активные сеансы в Telegram и других важных аккаунтах.",
    17: "Цель урока — научиться пользоваться анализатором как помощником, но не заменять им собственную проверку.",
    18: "Цель урока — правильно проверять номер и отправлять репорт без публикации лишних персональных данных.",
    19: "Цель урока — знать первые действия после ошибки: блокировка, смена паролей, доказательства и обращение в банк.",
    20: "Цель урока — собрать личный план безопасности, который можно применять самому и объяснить семье.",
}

WORD_NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

LESSON_HEADER_RE = re.compile(
    r"^\u041c\u043e\u0434\u0443\u043b\u044c\s+(\d+)\.\s+"
    r"\u0423\u0440\u043e\u043a\s+(\d+)\.\s+(.+)$"
)
QUESTION_RE = re.compile(r"^\d+\.\s+(.+)$")
CHOICE_RE = re.compile(r"^([A-D])\)\s+(.+)$")


@dataclass
class ParsedQuestion:
    text: str
    choices: list[tuple[str, str]]
    correct_letter: str
    explanation: str


@dataclass
class ParsedLesson:
    module_number: int
    lesson_number: int
    title: str
    summary: str
    content: str
    duration_minutes: int
    question: ParsedQuestion


def extract_docx_paragraphs(path: Path) -> list[str]:
    try:
        with zipfile.ZipFile(path) as archive:
            document = archive.read("word/document.xml")
    except (KeyError, zipfile.BadZipFile) as exc:
        raise CommandError("Файл не похож на корректный .docx документ.") from exc

    root = ElementTree.fromstring(document)
    paragraphs: list[str] = []
    for paragraph in root.findall(".//w:p", WORD_NS):
        text = "".join(
            node.text or "" for node in paragraph.findall(".//w:t", WORD_NS)
        ).strip()
        if text:
            paragraphs.append(text)
    return paragraphs


def find_index(lines: list[str], value: str, default: int | None = None) -> int:
    try:
        return lines.index(value)
    except ValueError:
        if default is None:
            raise
        return default


def parse_duration(lines: list[str]) -> int:
    label = "\u0420\u0435\u043a\u043e\u043c\u0435\u043d\u0434\u0443\u0435\u043c\u0430\u044f \u0434\u043b\u0438\u0442\u0435\u043b\u044c\u043d\u043e\u0441\u0442\u044c"
    if label not in lines:
        return 30
    raw_value = lines[lines.index(label) + 1]
    numbers = [int(value) for value in re.findall(r"\d+", raw_value)]
    if not numbers:
        return 30
    if len(numbers) == 1:
        return numbers[0]
    return round(sum(numbers[:2]) / 2)


def parse_question(lines: list[str]) -> ParsedQuestion:
    for index, line in enumerate(lines):
        question_match = QUESTION_RE.match(line)
        if not question_match:
            continue

        choices: list[tuple[str, str]] = []
        correct_letter = "A"
        explanation = "Повторите материал урока и проверьте признаки риска."

        for next_line in lines[index + 1 :]:
            choice_match = CHOICE_RE.match(next_line)
            if choice_match:
                choices.append((choice_match.group(1), choice_match.group(2)))
                continue

            if next_line.startswith(
                "\u041f\u0440\u0430\u0432\u0438\u043b\u044c\u043d\u044b\u0439 "
                "\u043e\u0442\u0432\u0435\u0442:"
            ):
                value = next_line.split(":", 1)[1].strip()
                if value:
                    correct_letter = value[0].upper()
                continue

            if next_line.startswith("\u041f\u043e\u044f\u0441\u043d\u0435\u043d\u0438\u0435:"):
                explanation = next_line.split(":", 1)[1].strip()
                break

            if QUESTION_RE.match(next_line):
                break

        if choices:
            return ParsedQuestion(
                text=question_match.group(1),
                choices=choices,
                correct_letter=correct_letter,
                explanation=explanation,
            )

    return ParsedQuestion(
        text="Какое действие безопаснее всего в подозрительной ситуации?",
        choices=[
            ("A", "Сразу перейти по ссылке"),
            ("B", "Проверить источник через официальный канал"),
            ("C", "Назвать SMS-код оператору"),
            ("D", "Установить присланный APK-файл"),
        ],
        correct_letter="B",
        explanation="Безопаснее остановиться и проверить источник через официальный канал.",
    )


def make_practice_line_user_facing(line: str, task_number: int) -> str:
    prefixes = (
        "\u0418\u043d\u0442\u0435\u0440\u0430\u043a\u0442\u0438\u0432:",
        "\u041f\u0440\u0430\u043a\u0442\u0438\u043a\u0430:",
        "\u0417\u0430\u0434\u0430\u043d\u0438\u0435 \u0432 \u043b\u0438\u0447\u043d\u044b\u0439 \u043a\u0430\u0431\u0438\u043d\u0435\u0442:",
    )
    body = line
    for prefix in prefixes:
        if body.startswith(prefix):
            body = body[len(prefix) :].strip()
            break

    replacements = {
        "\u043f\u043e\u043a\u0430\u0436\u0438\u0442\u0435 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044e": "\u0440\u0430\u0437\u0431\u0435\u0440\u0438\u0442\u0435",
        "\u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c \u0432\u0438\u0434\u0438\u0442": "\u0440\u0430\u0441\u0441\u043c\u043e\u0442\u0440\u0438\u0442\u0435",
        "\u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c \u043f\u0440\u043e\u0432\u0435\u0440\u044f\u0435\u0442": "\u043f\u0440\u043e\u0432\u0435\u0440\u044c\u0442\u0435",
        "\u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c \u043f\u0438\u0448\u0435\u0442": "\u0437\u0430\u043f\u0438\u0448\u0438\u0442\u0435",
        "\u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c \u0434\u043e\u043b\u0436\u0435\u043d": "\u0432\u0430\u043c \u043d\u0443\u0436\u043d\u043e",
        "\u041e\u043d \u0434\u043e\u043b\u0436\u0435\u043d": "\u0412\u0430\u043c \u043d\u0443\u0436\u043d\u043e",
        "\u041e\u043d\u0430 \u0434\u043e\u043b\u0436\u043d\u0430": "\u0412\u0430\u043c \u043d\u0443\u0436\u043d\u043e",
        "\u041f\u043e\u0441\u043b\u0435 \u0432\u044b\u043f\u043e\u043b\u043d\u0435\u043d\u0438\u044f \u0441\u0430\u0439\u0442 \u043f\u043e\u043a\u0430\u0437\u044b\u0432\u0430\u0435\u0442": "\u041f\u043e\u0441\u043b\u0435 \u043e\u0442\u0432\u0435\u0442\u0430 \u0441\u0440\u0430\u0432\u043d\u0438\u0442\u0435 \u0441\u0432\u043e\u0439 \u0432\u044b\u0431\u043e\u0440 \u0441",
        "\u0441\u0430\u0439\u0442 \u043f\u043e\u043a\u0430\u0437\u044b\u0432\u0430\u0435\u0442": "\u0441\u0440\u0430\u0432\u043d\u0438\u0442\u0435 \u0441",
        "\u043e\u0442\u043c\u0435\u0447\u0430\u0435\u0442": "\u043e\u0442\u043c\u0435\u0442\u044c\u0442\u0435",
        "\u0440\u0430\u0441\u043f\u0440\u0435\u0434\u0435\u043b\u044f\u0435\u0442": "\u0440\u0430\u0441\u043f\u0440\u0435\u0434\u0435\u043b\u0438\u0442\u0435",
        "\u0441 \u043f\u0440\u0430\u0432\u0438\u043b\u044c\u043d\u043e\u0435 \u0440\u0430\u0441\u043f\u0440\u0435\u0434\u0435\u043b\u0435\u043d\u0438\u0435": "\u0441 \u043f\u0440\u0430\u0432\u0438\u043b\u044c\u043d\u044b\u043c \u0440\u0430\u0441\u043f\u0440\u0435\u0434\u0435\u043b\u0435\u043d\u0438\u0435\u043c",
    }
    for old, new in replacements.items():
        body = body.replace(old, new)

    if body:
        body = body[0].upper() + body[1:]
    return f"\u0417\u0430\u0434\u0430\u043d\u0438\u0435 {task_number}. {body}"


def make_lesson_line_user_facing(line: str) -> str:
    replacements = {
        "На учебном сайте этот урок можно оформить как": "Полезно представить это как",
        "На сайте можно реализовать тренажёр: пользователь получает 8 сообщений и выбирает уровень риска: безопасно, подозрительно, опасно. Затем система объясняет решение.": (
            "Тренировка: разберите 8 учебных сообщений и определите уровень риска: безопасно, подозрительно или опасно. После ответа сравните свой выбор с объяснением."
        ),
        "На сайте могут показываться красивые графики": "Мошенническая платформа может показывать красивые графики",
        "Практика для сайта: дайте пользователю 6 сообщений. Он вставляет их в учебный анализатор и сравнивает свой вывод с вердиктом системы.": (
            "Практика: проверьте 6 учебных сообщений в анализаторе и сравните свой вывод с вердиктом системы."
        ),
        "После завершения курса можно выдать сертификат, если пользователь набрал достаточный балл и выполнил практические задания.": (
            "После завершения курса вы сможете получить сертификат, если наберёте достаточный балл и выполните практические задания."
        ),
        "Пользователь должен научиться": "Ваша задача — научиться",
        "Пользователь должен понять": "Важно понять",
        "Пользователь должен понимать": "Важно понимать",
        "Пользователь должен видеть": "Обращайте внимание на",
        "Пользователь учится": "Вы учитесь",
        "Пользователь вставляет": "Вставьте",
        "Пользователь получает": "Получите",
        "Пользователь выбирает": "Выберите",
        "Пользователь отметьте": "Отметьте",
        "Пользователь разбирает": "Разберите",
        "Пользователь знает": "Можно знать",
        "Пользователь не просто": "Вы не просто",
        "Если пользователь знает": "Если вы знаете",
        "обычный пользователь": "обычный человек",
        "Обычный пользователь": "Обычный человек",
        "пользователь должен": "нужно",
        "пользователь точно понимает": "вы точно понимаете",
        "пользователь видит": "вы видите",
        "чем осторожнее пользователь должен обращаться": "тем осторожнее нужно обращаться",
        "Сайт показывает персональный чек-лист действий.": "После выбора используйте персональный чек-лист действий.",
        "сравните с разбор каждого сообщения": "сравните свой выбор с разбором каждого сообщения",
    }
    for old, new in replacements.items():
        line = line.replace(old, new)
    final_replacements = {
        "\u041f\u0440\u0430\u043a\u0442\u0438\u043a\u0430: \u043f\u0440\u043e\u0432\u0435\u0440\u044c\u0442\u0435": "\u0417\u0430\u0434\u0430\u043d\u0438\u0435 1. \u041f\u0440\u043e\u0432\u0435\u0440\u044c\u0442\u0435",
        "\u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c \u0432\u0438\u0434\u0438\u0442": "\u0412\u044b \u0432\u0438\u0434\u0438\u0442\u0435",
        "\u041a\u043e\u0433\u0434\u0430 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c \u043f\u044b\u0442\u0430\u0435\u0442\u0441\u044f": "\u041a\u043e\u0433\u0434\u0430 \u0447\u0435\u043b\u043e\u0432\u0435\u043a \u043f\u044b\u0442\u0430\u0435\u0442\u0441\u044f",
        "\u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c \u043e\u0442\u043f\u0440\u0430\u0432\u0438\u043b": "\u0447\u0435\u043b\u043e\u0432\u0435\u043a \u043e\u0442\u043f\u0440\u0430\u0432\u0438\u043b",
        "\u041f\u043e\u0441\u043b\u0435 \u0432\u044b\u0431\u043e\u0440\u0430 \u0441\u0440\u0430\u0432\u043d\u0438\u0442\u0435": "\u041f\u043e\u0441\u043b\u0435 \u043e\u0442\u0432\u0435\u0442\u0430 \u0441\u0440\u0430\u0432\u043d\u0438\u0442\u0435",
        "\u041f\u043e\u0441\u043b\u0435 \u0432\u044b\u0431\u043e\u0440\u0430 \u0438\u0441\u043f\u043e\u043b\u044c\u0437\u0443\u0439\u0442\u0435": "\u041f\u043e\u0441\u043b\u0435 \u043e\u0442\u0432\u0435\u0442\u0430 \u0438\u0441\u043f\u043e\u043b\u044c\u0437\u0443\u0439\u0442\u0435",
        "\u0413\u043b\u0430\u0432\u043d\u0430\u044f \u043e\u0448\u0438\u0431\u043a\u0430 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044f \u2014": "\u0413\u043b\u0430\u0432\u043d\u0430\u044f \u043e\u0448\u0438\u0431\u043a\u0430 \u2014",
        "\u0412\u044b \u0432\u0438\u0434\u0438\u0442\u0435 \u0440\u043e\u0441\u0442 \u0431\u0430\u043b\u0430\u043d\u0441\u0430 \u043d\u0430 \u0441\u0430\u0439\u0442\u0435, \u043d\u043e \u0432\u044b\u0432\u0435\u0441\u0442\u0438 \u0434\u0435\u043d\u044c\u0433\u0438 \u043d\u0435 \u043c\u043e\u0436\u0435\u0442.": "\u0412\u044b \u0432\u0438\u0434\u0438\u0442\u0435 \u0440\u043e\u0441\u0442 \u0431\u0430\u043b\u0430\u043d\u0441\u0430 \u043d\u0430 \u0441\u0430\u0439\u0442\u0435, \u043d\u043e \u0432\u044b\u0432\u0435\u0441\u0442\u0438 \u0434\u0435\u043d\u044c\u0433\u0438 \u043d\u0435\u0432\u043e\u0437\u043c\u043e\u0436\u043d\u043e.",
        "\u0421\u0430\u0439\u0442 \u0434\u043e\u043b\u0436\u0435\u043d \u043f\u0440\u0435\u0434\u0443\u043f\u0440\u0435\u0436\u0434\u0430\u0442\u044c \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044f \u043e\u0431 \u044d\u0442\u043e\u043c \u0440\u044f\u0434\u043e\u043c \u0441 \u043f\u043e\u043b\u0435\u043c \u0432\u0432\u043e\u0434\u0430.": "\u041f\u043e\u043c\u043d\u0438\u0442\u0435: \u0430\u043d\u0430\u043b\u0438\u0437\u0430\u0442\u043e\u0440 \u043d\u0435 \u0437\u0430\u043c\u0435\u043d\u044f\u0435\u0442 \u0432\u0430\u0448\u0443 \u043f\u0440\u043e\u0432\u0435\u0440\u043a\u0443 \u0438 \u043d\u0435 \u0434\u0435\u043b\u0430\u0435\u0442 \u043f\u043e\u0434\u043e\u0437\u0440\u0438\u0442\u0435\u043b\u044c\u043d\u0443\u044e \u0441\u0441\u044b\u043b\u043a\u0443 \u0431\u0435\u0437\u043e\u043f\u0430\u0441\u043d\u043e\u0439.",
        "\u0421\u0438\u0441\u0442\u0435\u043c\u0430 \u043f\u043e\u043a\u0430\u0437\u044b\u0432\u0430\u0435\u0442": "\u0412\u044b \u0443\u0432\u0438\u0434\u0438\u0442\u0435",
        "\u0438 \u0432\u044b\u0431\u0438\u0440\u0430\u0435\u0442": "\u0438 \u0432\u044b\u0431\u0435\u0440\u0438\u0442\u0435",
        "\u0438 \u043f\u043e\u043b\u0443\u0447\u0430\u0435\u0442": "\u0438 \u043f\u043e\u043b\u0443\u0447\u0438\u0442\u0435",
        "\u043a\u043e\u0442\u043e\u0440\u044b\u0435 \u043e\u043d \u0431\u0443\u0434\u0435\u0442": "\u043a\u043e\u0442\u043e\u0440\u044b\u0435 \u0432\u044b \u0431\u0443\u0434\u0435\u0442\u0435",
        "\u041f\u043e\u0441\u043b\u0435 \u043a\u0430\u0436\u0434\u043e\u0433\u043e \u043f\u0440\u0438\u043c\u0435\u0440\u0430 \u043f\u043e\u043a\u0430\u0437\u044b\u0432\u0430\u0439\u0442\u0435": "\u041f\u043e\u0441\u043b\u0435 \u043a\u0430\u0436\u0434\u043e\u0433\u043e \u043f\u0440\u0438\u043c\u0435\u0440\u0430 \u0438\u0437\u0443\u0447\u0438\u0442\u0435",
        "\u0417\u0430\u0434\u0430\u043d\u0438\u0435: \u0441\u043e\u0441\u0442\u0430\u0432\u0438\u0442\u044c": "\u0417\u0430\u0434\u0430\u043d\u0438\u0435 2. \u0421\u043e\u0441\u0442\u0430\u0432\u044c\u0442\u0435",
        "\u0417\u0430\u0434\u0430\u043d\u0438\u0435: \u0437\u0430\u043f\u043e\u043b\u043d\u0438\u0442\u044c": "\u0417\u0430\u0434\u0430\u043d\u0438\u0435 2. \u0417\u0430\u043f\u043e\u043b\u043d\u0438\u0442\u0435",
        "\u0424\u0438\u043d\u0430\u043b\u044c\u043d\u043e\u0435 \u0437\u0430\u0434\u0430\u043d\u0438\u0435: \u0441\u043e\u0437\u0434\u0430\u0442\u044c": "\u0417\u0430\u0434\u0430\u043d\u0438\u0435 2. \u0421\u043e\u0437\u0434\u0430\u0439\u0442\u0435",
    }
    for old, new in final_replacements.items():
        line = line.replace(old, new)
    return line


def normalize_lesson_heading(line: str) -> str:
    heading_replacements = {
        "\u041e\u0441\u043d\u043e\u0432\u043d\u043e\u0439 \u0443\u0447\u0435\u0431\u043d\u044b\u0439 \u043c\u0430\u0442\u0435\u0440\u0438\u0430\u043b": "\u0422\u0435\u043e\u0440\u0438\u044f",
        "\u041d\u0430 \u0447\u0442\u043e \u043e\u0431\u0440\u0430\u0442\u0438\u0442\u044c \u0432\u043d\u0438\u043c\u0430\u043d\u0438\u0435": "\u041f\u0440\u0438\u0437\u043d\u0430\u043a\u0438 \u0440\u0438\u0441\u043a\u0430",
        "\u0411\u0435\u0437\u043e\u043f\u0430\u0441\u043d\u044b\u0439 \u0430\u043b\u0433\u043e\u0440\u0438\u0442\u043c \u0434\u0435\u0439\u0441\u0442\u0432\u0438\u0439": "\u0427\u0442\u043e \u0434\u0435\u043b\u0430\u0442\u044c",
        "\u041f\u0440\u0430\u043a\u0442\u0438\u0447\u0435\u0441\u043a\u043e\u0435 \u0437\u0430\u0434\u0430\u043d\u0438\u0435 \u0434\u043b\u044f \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044f": "\u041f\u0440\u0430\u043a\u0442\u0438\u043a\u0430",
        "\u0410\u043a\u0442\u0443\u0430\u043b\u044c\u043d\u043e\u0435 \u0434\u043e\u043f\u043e\u043b\u043d\u0435\u043d\u0438\u0435": "\u041f\u0430\u043c\u044f\u0442\u043a\u0430",
        "\u0414\u043e\u043f\u043e\u043b\u043d\u0438\u0442\u0435\u043b\u044c\u043d\u044b\u0439 \u0440\u0430\u0437\u0431\u043e\u0440": "\u0414\u043e\u043f\u043e\u043b\u043d\u0438\u0442\u0435\u043b\u044c\u043d\u043e",
    }
    return heading_replacements.get(line, line)


def make_content_user_facing(lines: list[str]) -> list[str]:
    practice_heading = (
        "\u041f\u0440\u0430\u043a\u0442\u0438\u0447\u0435\u0441\u043a\u043e\u0435 "
        "\u0437\u0430\u0434\u0430\u043d\u0438\u0435 \u0434\u043b\u044f "
        "\u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044f"
    )
    practice_prefixes = (
        "\u0418\u043d\u0442\u0435\u0440\u0430\u043a\u0442\u0438\u0432:",
        "\u041f\u0440\u0430\u043a\u0442\u0438\u043a\u0430:",
        "\u0417\u0430\u0434\u0430\u043d\u0438\u0435 \u0432 \u043b\u0438\u0447\u043d\u044b\u0439 \u043a\u0430\u0431\u0438\u043d\u0435\u0442:",
    )
    normalized: list[str] = []
    in_practice = False
    task_number = 1

    for line in lines:
        if line == practice_heading:
            in_practice = True
            task_number = 1
            normalized.append(normalize_lesson_heading(make_lesson_line_user_facing(line)))
            continue

        if in_practice and line.startswith(practice_prefixes):
            normalized.append(
                make_lesson_line_user_facing(
                    make_practice_line_user_facing(line, task_number)
                )
            )
            task_number += 1
            continue

        normalized.append(normalize_lesson_heading(make_lesson_line_user_facing(line)))
    return normalized


def parse_lesson_block(header: str, block: list[str]) -> ParsedLesson:
    header_match = LESSON_HEADER_RE.match(header)
    if not header_match:
        raise CommandError(f"Не удалось разобрать заголовок урока: {header}")

    module_number = int(header_match.group(1))
    lesson_number = int(header_match.group(2))
    title = header_match.group(3).strip()

    intro_label = "\u0412\u0441\u0442\u0443\u043f\u0438\u0442\u0435\u043b\u044c\u043d\u044b\u0439 \u0442\u0435\u043a\u0441\u0442 \u0434\u043b\u044f \u0441\u0442\u0440\u0430\u043d\u0438\u0446\u044b \u0443\u0440\u043e\u043a\u0430"
    test_label = "\u041c\u0438\u043d\u0438-\u0442\u0435\u0441\u0442 \u0434\u043b\u044f \u0441\u0430\u0439\u0442\u0430"

    content_start = find_index(block, intro_label, default=0) + 1
    test_start = find_index(block, test_label, default=len(block))
    content_lines = make_content_user_facing(block[content_start:test_start])
    question_lines = block[test_start + 1 :]

    summary = next(
        (
            line
            for line in content_lines
            if line
            and not line.startswith("\u041e\u0441\u043d\u043e\u0432\u043d\u043e\u0439 ")
            and not line.startswith("\u041f\u0440\u0430\u043a\u0442\u0438\u0447\u0435\u0441\u043a\u043e\u0435 ")
        ),
        title,
    )
    global_order = (module_number - 1) * 2 + lesson_number
    objective = LESSON_OBJECTIVES.get(global_order)
    prepared_lines = content_lines
    if objective:
        prepared_lines = ["Цель урока", objective, *content_lines]
    content = "\n\n".join([*prepared_lines, "Памятка", UPDATED_SAFETY_NOTE])

    return ParsedLesson(
        module_number=module_number,
        lesson_number=lesson_number,
        title=title,
        summary=summary,
        content=content,
        duration_minutes=parse_duration(block),
        question=parse_question(question_lines),
    )


def parse_lessons(paragraphs: list[str]) -> list[ParsedLesson]:
    starts: list[tuple[int, re.Match[str]]] = []
    for index, paragraph in enumerate(paragraphs):
        match = LESSON_HEADER_RE.match(paragraph)
        if match:
            starts.append((index, match))

    if not starts:
        raise CommandError("В документе не найдены заголовки уроков вида 'Модуль N. Урок N. ...'.")

    lessons: list[ParsedLesson] = []
    for position, (start, _) in enumerate(starts):
        end = starts[position + 1][0] if position + 1 < len(starts) else len(paragraphs)
        lessons.append(parse_lesson_block(paragraphs[start], paragraphs[start + 1 : end]))
    return lessons


def content_with_supplemental_note(content: str, global_order: int) -> str:
    note = SUPPLEMENTAL_LESSON_NOTES.get(global_order)
    if not note:
        return content
    return "\n\n".join([content, "Дополнительно", note])


class Command(BaseCommand):
    help = "Imports CyberSafe course lessons from a prepared DOCX file."

    def add_arguments(self, parser):
        parser.add_argument("docx_path", help="Path to CyberSafe lessons .docx file")
        parser.add_argument(
            "--slug",
            default="digital-safety-basics",
            help="Course slug to create/update",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        path = Path(options["docx_path"]).expanduser()
        if not path.exists():
            raise CommandError(f"Файл не найден: {path}")

        lessons = parse_lessons(extract_docx_paragraphs(path))
        lessons_by_global_order = {
            order: lesson for order, lesson in enumerate(lessons, start=1)
        }

        Course.objects.filter(slug=options["slug"]).update(is_published=False)

        imported_count = 0
        for level_config in COURSE_LEVELS:
            selected_orders = list(level_config["orders"])
            selected_lessons = [
                lessons_by_global_order[order]
                for order in selected_orders
                if order in lessons_by_global_order
            ]
            course, _ = Course.objects.update_or_create(
                slug=level_config["slug"],
                defaults={
                    "title_ru": level_config["title_ru"],
                    "title_uz": level_config["title_uz"],
                    "description_ru": level_config["description_ru"],
                    "description_uz": level_config["description_uz"],
                    "level": level_config["level"],
                    "duration_minutes": sum(
                        lesson.duration_minutes for lesson in selected_lessons
                    ),
                    "is_published": True,
                    "order": level_config["order"],
                },
            )

            for local_order, global_order in enumerate(selected_orders, start=1):
                parsed = lessons_by_global_order.get(global_order)
                if not parsed:
                    continue
                module_title = (
                    f"Модуль {parsed.module_number}. "
                    f"{CLEAN_MODULE_TITLES.get(parsed.module_number, 'Цифровая безопасность')}"
                )
                content = content_with_supplemental_note(parsed.content, global_order)
                lesson, _ = Lesson.objects.update_or_create(
                    course=course,
                    order=local_order,
                    defaults={
                        "title_ru": parsed.title,
                        "title_uz": parsed.title,
                        "summary_ru": parsed.summary,
                        "summary_uz": parsed.summary,
                        "module_title_ru": module_title,
                        "module_title_uz": module_title,
                        "content_ru": content,
                        "content_uz": content,
                        "duration_minutes": parsed.duration_minutes,
                        "is_published": True,
                    },
                )
                lesson.questions.all().delete()
                question = LessonQuestion.objects.create(
                    lesson=lesson,
                    text_ru=parsed.question.text,
                    text_uz=parsed.question.text,
                    explanation_ru=parsed.question.explanation,
                    explanation_uz=parsed.question.explanation,
                )
                for choice_order, (letter, text) in enumerate(
                    parsed.question.choices, start=1
                ):
                    LessonChoice.objects.update_or_create(
                        question=question,
                        order=choice_order,
                        defaults={
                            "text_ru": text,
                            "text_uz": text,
                            "is_correct": letter == parsed.question.correct_letter,
                        },
                    )
                imported_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Imported {imported_count} lessons into {len(COURSE_LEVELS)} course levels."
            )
        )
