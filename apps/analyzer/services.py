import hashlib
import hmac
import ipaddress
import re
from dataclasses import dataclass
from urllib.parse import urlsplit

from django.conf import settings
from django.core.cache import cache
from django.db import models
from django.utils import timezone
from rest_framework.exceptions import Throttled

from .models import AnalysisLog, ThreatDomain

SHORTENER_DOMAINS = {
    "bit.ly",
    "cutt.ly",
    "goo.gl",
    "is.gd",
    "rebrand.ly",
    "t.co",
    "tinyurl.com",
}

SUSPICIOUS_TLDS = {
    "click",
    "country",
    "download",
    "gq",
    "kim",
    "link",
    "loan",
    "men",
    "ml",
    "mom",
    "rest",
    "support",
    "top",
    "work",
    "zip",
}

URL_BAIT_WORDS = {
    "account",
    "bank",
    "bonus",
    "click",
    "compensation",
    "confirm",
    "delivery",
    "invest",
    "login",
    "mygov",
    "payme",
    "secure",
    "soliq",
    "subsidy",
    "update",
    "uzum",
    "verify",
    "wallet",
}

IMPERSONATED_BRANDS = {
    "click": {"click.uz"},
    "mygov": {"my.gov.uz"},
    "payme": {"payme.uz"},
    "soliq": {"soliq.uz"},
    "uzum": {"uzum.uz", "uzumbank.uz"},
}

MESSAGES = {
    "ru": {
        "urgency": "Сообщение создаёт искусственную срочность или угрожает блокировкой.",
        "secret_request": "Запрашиваются секретные данные или одноразовый код.",
        "money": "Есть просьба перевести деньги или оплатить вымышленную комиссию.",
        "prize": "Обещается неожиданный приз, компенсация или возврат денег.",
        "apk": "Предлагается установить приложение или APK-файл.",
        "remote_access": "Запрашивается удалённый доступ или демонстрация экрана.",
        "messenger_takeover": "Запрашивается код входа или QR-код, с помощью которого могут захватить аккаунт.",
        "government_impersonation": "Сообщение использует тему государственной выплаты, налога, штрафа или субсидии.",
        "investment": "Обещается гарантированная прибыль или инвестиция без риска.",
        "job_deposit": "Предлагается лёгкий заработок или работа с предварительным платежом.",
        "family_emergency": "Используется сообщение о чрезвычайной ситуации с родственником; голос и аккаунт могут быть подделаны.",
        "invalid_host": "Не удалось определить домен ссылки.",
        "known_threat": "Домен находится в локальной базе угроз CyberSafe ({category}).",
        "no_https": "Ссылка использует незашифрованный HTTP.",
        "userinfo": "Адрес скрывает реальный домен после символа @.",
        "ip_host": "Вместо доменного имени используется IP-адрес.",
        "punycode": "Домен использует Punycode и может имитировать знакомое название.",
        "shortener": "Сокращённая ссылка скрывает конечный адрес.",
        "risky_tld": "Доменная зона часто используется в одноразовых мошеннических сайтах.",
        "many_subdomains": "Адрес содержит необычно много поддоменов.",
        "bait_words": "В адресе сочетаются слова, типичные для фишинговых страниц.",
        "brand_impersonation": "Домен содержит название «{brand}», но не относится к известному официальному домену.",
        "very_long": "Ссылка необычно длинная и может скрывать значимые части адреса.",
        "safe_url": "Явных технических признаков мошенничества не найдено. Это не гарантирует безопасность сайта.",
        "contains_link": "Сообщение содержит ссылку — проверяйте домен отдельно.",
        "safe_sms": "Явных манипулятивных признаков не найдено. Не передавайте коды и данные неизвестным отправителям.",
    },
    "uz": {
        "urgency": "Xabarda sun’iy shoshilinch vaziyat yaratilgan yoki bloklash bilan tahdid qilinmoqda.",
        "secret_request": "Maxfiy ma’lumot yoki bir martalik kod so‘ralmoqda.",
        "money": "Pul o‘tkazish yoki soxta komissiyani to‘lash so‘ralmoqda.",
        "prize": "Kutilmagan yutuq, kompensatsiya yoki pul qaytarish va’da qilinmoqda.",
        "apk": "Ilova yoki APK faylini o‘rnatish taklif qilinmoqda.",
        "remote_access": "Masofaviy kirish yoki ekranni ko‘rsatish so‘ralmoqda.",
        "messenger_takeover": "Akkauntni egallash uchun ishlatilishi mumkin bo‘lgan kirish kodi yoki QR-kod so‘ralmoqda.",
        "government_impersonation": "Xabarda davlat to‘lovi, soliq, jarima yoki subsidiya mavzusidan foydalanilgan.",
        "investment": "Kafolatlangan foyda yoki xavfsiz investitsiya va’da qilinmoqda.",
        "job_deposit": "Oson daromad yoki oldindan to‘lov talab qiladigan ish taklif qilinmoqda.",
        "family_emergency": "Qarindosh bilan bog‘liq favqulodda vaziyat ishlatilmoqda; ovoz yoki akkaunt soxtalashtirilgan bo‘lishi mumkin.",
        "invalid_host": "Havola domenini aniqlab bo‘lmadi.",
        "known_threat": "Domen CyberSafe mahalliy tahdidlar bazasida mavjud ({category}).",
        "no_https": "Havola shifrlanmagan HTTP protokolidan foydalanadi.",
        "userinfo": "Manzilda @ belgisidan keyingi haqiqiy domen yashirilgan.",
        "ip_host": "Domen nomi o‘rniga IP-manzil ishlatilgan.",
        "punycode": "Domen Punycode ishlatadi va tanish nomga taqlid qilishi mumkin.",
        "shortener": "Qisqartirilgan havola yakuniy manzilni yashiradi.",
        "risky_tld": "Bu domen zonasi bir martalik firibgar saytlarda ko‘p ishlatiladi.",
        "many_subdomains": "Manzilda noodatiy darajada ko‘p subdomen bor.",
        "bait_words": "Manzilda fishing sahifalariga xos bir nechta so‘z birlashgan.",
        "brand_impersonation": "Domen «{brand}» nomini o‘z ichiga oladi, ammo ma’lum rasmiy domenga tegishli emas.",
        "very_long": "Havola noodatiy uzun va muhim qismlarni yashirishi mumkin.",
        "safe_url": "Firibgarlikning aniq texnik belgisi topilmadi. Bu sayt xavfsizligini kafolatlamaydi.",
        "contains_link": "Xabarda havola bor — domenni alohida tekshiring.",
        "safe_sms": "Aniq manipulyatsiya belgisi topilmadi. Noma’lum jo‘natuvchiga kod va ma’lumot bermang.",
    },
}


def message(language, key, **values):
    return MESSAGES.get(language, MESSAGES["ru"])[key].format(**values)


SMS_RULES = [
    (
        30,
        "urgency",
        re.compile(
            r"\b(срочно|немедленно|последн\w+\s+шанс|блокир\w+|"
            r"zudlik|tezda|bloklan\w+|oxirgi\s+imkon)\b",
            re.IGNORECASE,
        ),
        "urgency",
    ),
    (
        35,
        "secret_request",
        re.compile(
            r"\b(sms[\s-]?код|код\s+подтверждения|одноразов\w+\s+код|"
            r"парол\w+|cvv|pin|tasdiqlash\s+kodi|sms\s*kod\w*|parol)\b",
            re.IGNORECASE,
        ),
        "secret_request",
    ),
    (
        25,
        "money",
        re.compile(
            r"\b(перевед\w+\s+деньг|безопасн\w+\s+сч[её]т|оплат\w+\s+комисси|"
            r"pul\s+o['‘’`]tkaz|xavfsiz\s+hisob|komissiya)\b",
            re.IGNORECASE,
        ),
        "money",
    ),
    (
        20,
        "prize",
        re.compile(
            r"\b(выиграл\w+|приз|компенсаци|возврат\s+денег|"
            r"yutuq|sovrin|kompensatsiya)\b",
            re.IGNORECASE,
        ),
        "prize",
    ),
    (
        30,
        "apk",
        re.compile(
            r"\b(apk|установ\w+\s+приложен|скача\w+\s+приложен|"
            r"ilovani\s+(?:yukla|o['‘’`]rnat))\b",
            re.IGNORECASE,
        ),
        "apk",
    ),
    (
        35,
        "remote_access",
        re.compile(
            r"\b(anydesk|teamviewer|rustdesk|quicksupport|удал[её]нн\w+\s+доступ|"
            r"демонстраци\w+\s+экрана|экран\w+\s+покаж|masofaviy\s+kirish|"
            r"ekran\w+\s+ko['‘’`]rsat)\b",
            re.IGNORECASE,
        ),
        "remote_access",
    ),
    (
        30,
        "messenger_takeover",
        re.compile(
            r"\b(код\s+(?:входа|из\s+telegram)|telegram\s+код|qr[\s-]?код\w*\s+"
            r"(?:сканир|отсканир)|login\s+code|telegram\s+kodi|"
            r"qr[\s-]?kod\w*\s+skaner)\b",
            re.IGNORECASE,
        ),
        "messenger_takeover",
    ),
    (
        25,
        "government_impersonation",
        re.compile(
            r"\b(госуслуг|налогов\w+\s+возврат|субсиди|пособи|штраф\w+\s+оплат|"
            r"davlat\s+xizmat|soliq\s+qaytar|subsidiya|nafaqa|jarima)\b",
            re.IGNORECASE,
        ),
        "government_impersonation",
    ),
    (
        30,
        "investment",
        re.compile(
            r"\b(гарантированн\w+\s+доход|без\s+риска|удво\w+\s+(?:деньг|вклад)|"
            r"крипт\w+|инвестиц\w+|kafolatlangan\s+daromad|xavfsiz\s+sarmoya|"
            r"kripto|investitsiya)\b",
            re.IGNORECASE,
        ),
        "investment",
    ),
    (
        25,
        "job_deposit",
        re.compile(
            r"\b(работ\w+\s+из\s+дома|л[её]гк\w+\s+заработ|выкуп\w+\s+товар|"
            r"внес\w+\s+(?:депозит|залог)|uydan\s+ish|oson\s+daromad|"
            r"depozit\s+to['‘’`]la|tovar\w*\s+sotib\s+ol)\b",
            re.IGNORECASE,
        ),
        "job_deposit",
    ),
    (
        20,
        "family_emergency",
        re.compile(
            r"\b(мама|папа|сын|дочь|брат|сестра|ona|ota|o['‘’`]g['‘’`]il|qiz|aka|uka)"
            r".{0,45}\b(авари|полици|больниц|срочно\s+деньги|"
            r"avariya|politsiya|kasalxona|tez\s+pul)\b",
            re.IGNORECASE,
        ),
        "family_emergency",
    ),
]

URL_PATTERN = re.compile(r"https?://[^\s]+|www\.[^\s]+", re.IGNORECASE)


@dataclass
class AnalysisResult:
    verdict: str
    risk_score: int
    reasons: list[str]
    signals: list[str]


def stable_hash(value):
    return hmac.new(
        settings.ANALYZER_HASH_SECRET.encode(),
        value.encode(),
        hashlib.sha256,
    ).hexdigest()


def enforce_rate_limit(ip_hash):
    key = f"analyzer-rate:{ip_hash}"
    try:
        count = cache.incr(key)
    except ValueError:
        cache.set(key, 1, timeout=settings.ANALYZER_REQUEST_WINDOW_SECONDS)
        count = 1
    if count > settings.ANALYZER_REQUEST_LIMIT:
        raise Throttled(
            detail="Analyzer request limit reached. Try again later.",
            wait=settings.ANALYZER_REQUEST_WINDOW_SECONDS,
        )


def verdict_for_score(score):
    if score >= 60:
        return AnalysisLog.Verdict.DANGEROUS
    if score >= 25:
        return AnalysisLog.Verdict.SUSPICIOUS
    return AnalysisLog.Verdict.SAFE


def analyze_url_value(value, language="ru"):
    raw = value.strip()
    candidate = raw if "://" in raw else f"https://{raw}"
    parsed = urlsplit(candidate)
    hostname = (parsed.hostname or "").lower().rstrip(".")
    reasons = []
    signals = []
    score = 0

    if not hostname:
        return AnalysisResult(
            AnalysisLog.Verdict.SUSPICIOUS,
            40,
            [message(language, "invalid_host")],
            ["invalid_host"],
        )

    threat = ThreatDomain.objects.filter(
        domain=hostname,
        is_active=True,
    ).filter(models.Q(expires_at__isnull=True) | models.Q(expires_at__gt=timezone.now())).first()
    if threat:
        score += 100
        signals.append("known_threat")
        reasons.append(message(language, "known_threat", category=threat.category))

    if parsed.scheme.lower() == "http":
        score += 20
        signals.append("no_https")
        reasons.append(message(language, "no_https"))

    if parsed.username or parsed.password:
        score += 45
        signals.append("userinfo")
        reasons.append(message(language, "userinfo"))

    try:
        ipaddress.ip_address(hostname)
        score += 35
        signals.append("ip_host")
        reasons.append(message(language, "ip_host"))
    except ValueError:
        pass

    if hostname.startswith("xn--") or ".xn--" in hostname:
        score += 25
        signals.append("punycode")
        reasons.append(message(language, "punycode"))

    if hostname in SHORTENER_DOMAINS:
        score += 25
        signals.append("shortener")
        reasons.append(message(language, "shortener"))

    tld = hostname.rsplit(".", 1)[-1] if "." in hostname else ""
    if tld in SUSPICIOUS_TLDS:
        score += 20
        signals.append("risky_tld")
        reasons.append(message(language, "risky_tld"))

    labels = hostname.split(".")
    if len(labels) >= 5:
        score += 15
        signals.append("many_subdomains")
        reasons.append(message(language, "many_subdomains"))

    bait_count = sum(
        1 for word in URL_BAIT_WORDS if word in f"{hostname}{parsed.path}".lower()
    )
    if bait_count >= 2:
        score += min(30, bait_count * 8)
        signals.append("bait_words")
        reasons.append(message(language, "bait_words"))

    for brand, official_domains in IMPERSONATED_BRANDS.items():
        if brand not in hostname:
            continue
        is_official = any(
            hostname == domain or hostname.endswith(f".{domain}")
            for domain in official_domains
        )
        if not is_official:
            score += 35
            signals.append("brand_impersonation")
            reasons.append(message(language, "brand_impersonation", brand=brand))
            break

    if len(raw) > 160:
        score += 15
        signals.append("very_long")
        reasons.append(message(language, "very_long"))

    score = min(score, 100)
    if not reasons:
        reasons.append(message(language, "safe_url"))
    return AnalysisResult(verdict_for_score(score), score, reasons, signals)


def analyze_sms_value(value, language="ru"):
    text = value.strip()
    score = 0
    reasons = []
    signals = []
    for weight, signal, pattern, message_key in SMS_RULES:
        if pattern.search(text):
            score += weight
            signals.append(signal)
            reasons.append(message(language, message_key))

    links = URL_PATTERN.findall(text)
    if links:
        signals.append("contains_link")
        reasons.append(message(language, "contains_link"))
        score += 15
        for link in links[:2]:
            url_result = analyze_url_value(link, language=language)
            if url_result.risk_score >= 25:
                score += min(40, url_result.risk_score // 2)
                reasons.extend(url_result.reasons[:2])
                signals.extend(url_result.signals)

    if len(text) < 12:
        score += 5
    score = min(score, 100)
    if not reasons:
        reasons.append(message(language, "safe_sms"))
    return AnalysisResult(verdict_for_score(score), score, reasons, list(dict.fromkeys(signals)))


def save_analysis(*, content, content_type, ip_hash, result):
    return AnalysisLog.objects.create(
        content_hash=stable_hash(content.strip()),
        content_type=content_type,
        verdict=result.verdict,
        risk_score=result.risk_score,
        reasons=result.reasons,
        ip_hash=ip_hash,
    )
