from django.core.management.base import BaseCommand

from apps.webgame.models import GameCharacter, GameMission, GameScenario3D


CHARACTERS = [
    {
        "name_ru": "Амина",
        "name_uz": "Amina",
        "role": "analyst",
        "gender": "female",
        "description_ru": "Аналитик угроз: быстро замечает подозрительные детали в письмах и ссылках.",
        "description_uz": "Tahdidlar tahlilchisi: xatlar va havolalardagi shubhali belgilarni tez topadi.",
        "model_key": "amina",
        "color_primary": "#60a5fa",
        "order": 1,
    },
    {
        "name_ru": "Дилноза",
        "name_uz": "Dilnoza",
        "role": "mentor",
        "gender": "female",
        "description_ru": "Наставник: объясняет безопасные решения и даёт понятные подсказки.",
        "description_uz": "Mentor: xavfsiz qarorlarni tushuntiradi va aniq maslahatlar beradi.",
        "model_key": "dilnoza",
        "color_primary": "#a78bfa",
        "order": 2,
    },
    {
        "name_ru": "Тимур",
        "name_uz": "Timur",
        "role": "defender",
        "gender": "male",
        "description_ru": "Защитник аккаунтов: фокусируется на паролях, 2FA и блокировке угроз.",
        "description_uz": "Akkaunt himoyachisi: parol, 2FA va tahdidlarni bloklashga e’tibor beradi.",
        "model_key": "timur",
        "color_primary": "#34d399",
        "order": 3,
    },
    {
        "name_ru": "Жасур",
        "name_uz": "Jasur",
        "role": "investigator",
        "gender": "male",
        "description_ru": "Расследователь: проверяет следы атаки, входы в аккаунт и цифровые улики.",
        "description_uz": "Tergovchi: hujum izlari, akkaunt kirishlari va raqamli dalillarni tekshiradi.",
        "model_key": "jasur",
        "color_primary": "#f59e0b",
        "order": 4,
    },
]


OPTIONS_SAFE_CLICK = [
    {"value": "fake-link", "label_ru": "bonus-payme.secure-login", "label_uz": "bonus-payme.secure-login", "kind": "danger", "color": "#fca5a5", "position": [-2.35, 0.55, 0]},
    {"value": "official-site", "label_ru": "Официальный сайт банка", "label_uz": "Bankning rasmiy sayti", "kind": "safe", "color": "#93c5fd", "position": [0, 0.55, -0.35]},
    {"value": "unknown-file", "label_ru": "delivery.apk", "label_uz": "delivery.apk", "kind": "warning", "color": "#fde68a", "position": [2.35, 0.55, 0]},
]

OPTIONS_INBOX = [
    {"value": "password-reset", "label_ru": "Срочно подтвердите пароль", "label_uz": "Parolni zudlik bilan tasdiqlang", "kind": "danger", "color": "#fca5a5", "position": [-2.35, 0.55, 0]},
    {"value": "team-news", "label_ru": "Новости команды", "label_uz": "Jamoa yangiliklari", "kind": "safe", "color": "#bfdbfe", "position": [0, 0.55, -0.35]},
    {"value": "invoice-pdf", "label_ru": "Счёт от партнёра", "label_uz": "Hamkordan hisob", "kind": "warning", "color": "#fde68a", "position": [2.35, 0.55, 0]},
]

OPTIONS_ACCOUNT = [
    {"value": "enable-2fa", "label_ru": "Включить 2FA", "label_uz": "2FA ni yoqish", "kind": "safe", "color": "#86efac", "position": [-2.35, 0.55, 0]},
    {"value": "reuse-password", "label_ru": "Оставить старый пароль", "label_uz": "Eski parolni qoldirish", "kind": "danger", "color": "#fca5a5", "position": [0, 0.55, -0.35]},
    {"value": "ignore-login", "label_ru": "Игнорировать вход", "label_uz": "Kirishni e’tiborsiz qoldirish", "kind": "warning", "color": "#fde68a", "position": [2.35, 0.55, 0]},
]

OPTIONS_SOCIAL = [
    {"value": "share-code", "label_ru": "Назвать SMS-код", "label_uz": "SMS kodni aytish", "kind": "danger", "color": "#fca5a5", "position": [-2.35, 0.55, 0]},
    {"value": "call-bank", "label_ru": "Позвонить в банк самому", "label_uz": "Bankka o‘zim qo‘ng‘iroq qilish", "kind": "safe", "color": "#86efac", "position": [0, 0.55, -0.35]},
    {"value": "install-app", "label_ru": "Установить приложение", "label_uz": "Ilovani o‘rnatish", "kind": "warning", "color": "#fde68a", "position": [2.35, 0.55, 0]},
]


def step(
    *,
    prompt_ru,
    prompt_uz,
    correct_value,
    options,
    points,
    penalty,
    feedback_correct_ru,
    feedback_correct_uz,
    feedback_wrong_ru,
    feedback_wrong_uz,
    task_type="select_object",
):
    return {
        "task_type": task_type,
        "prompt_ru": prompt_ru,
        "prompt_uz": prompt_uz,
        "options": options,
        "correct_value": correct_value,
        "points": points,
        "penalty": penalty,
        "feedback_correct_ru": feedback_correct_ru,
        "feedback_correct_uz": feedback_correct_uz,
        "feedback_wrong_ru": feedback_wrong_ru,
        "feedback_wrong_uz": feedback_wrong_uz,
    }


SAFE_CLICK_STEPS = {
    "easy": [
        step(
            prompt_ru="Осмотрите рабочий стол. Какая ссылка выглядит фишинговой?",
            prompt_uz="Ish stolini tekshiring. Qaysi havola fishingga o‘xshaydi?",
            correct_value="fake-link",
            options=OPTIONS_SAFE_CLICK,
            points=20,
            penalty=-5,
            feedback_correct_ru="Верно: похожий домен и срочный призыв — типичные признаки фишинга.",
            feedback_correct_uz="To‘g‘ri: o‘xshash domen va shoshiltirish fishing belgilaridir.",
            feedback_wrong_ru="Проверьте домен внимательнее: мошенники часто меняют одну букву.",
            feedback_wrong_uz="Domenni diqqat bilan tekshiring: firibgarlar ko‘pincha bitta harfni almashtiradi.",
        ),
        step(
            prompt_ru="Что безопаснее сделать перед вводом пароля?",
            prompt_uz="Parol kiritishdan oldin nima xavfsizroq?",
            correct_value="official-site",
            options=OPTIONS_SAFE_CLICK,
            points=20,
            penalty=-5,
            feedback_correct_ru="Правильно: открывать сервис вручную или через закладку безопаснее.",
            feedback_correct_uz="To‘g‘ri: xizmatni qo‘lda yoki saqlangan havola orqali ochish xavfsizroq.",
            feedback_wrong_ru="Не переходите по ссылке из сообщения, если просят срочно войти.",
            feedback_wrong_uz="Agar xabarda shoshilinch kirish so‘ralsa, havolaga bosmang.",
        ),
    ],
    "medium": [],
    "hard": [],
}
SAFE_CLICK_STEPS["medium"] = [
    {**item, "points": 25, "penalty": -8} for item in SAFE_CLICK_STEPS["easy"]
]
SAFE_CLICK_STEPS["hard"] = [
    {**item, "points": 35, "penalty": -12} for item in SAFE_CLICK_STEPS["easy"]
]

SCENARIOS = [
    {
        "slug": "safe-click-training",
        "title_ru": "Тренировка безопасного клика",
        "title_uz": "Xavfsiz bosish mashqi",
        "description_ru": "Найдите опасные ссылки и выберите безопасное действие в спокойной 3D-сцене.",
        "description_uz": "3D sahnada xavfli havolalarni toping va xavfsiz harakatni tanlang.",
        "category": "safe_clicking",
        "scene_key": "cyber_office",
        "is_default": True,
        "order": 1,
        "missions": SAFE_CLICK_STEPS,
    },
    {
        "slug": "phishing-inbox",
        "title_ru": "Фишинговая почта",
        "title_uz": "Fishing pochta",
        "description_ru": "В 3D-офисе найдите письмо, которое крадёт доступ к аккаунту.",
        "description_uz": "3D ofisda akkauntga kirishni o‘g‘irlaydigan xatni toping.",
        "category": "phishing",
        "scene_key": "inbox_room",
        "is_default": False,
        "order": 2,
        "missions": {
            difficulty: [
                step(
                    prompt_ru="Какое письмо выглядит как попытка украсть пароль?",
                    prompt_uz="Qaysi xat parolni o‘g‘irlashga urinishga o‘xshaydi?",
                    correct_value="password-reset",
                    options=OPTIONS_INBOX,
                    points=points,
                    penalty=penalty,
                    feedback_correct_ru="Верно: срочность и просьба подтвердить пароль — высокий риск.",
                    feedback_correct_uz="To‘g‘ri: shoshiltirish va parolni tasdiqlash so‘rovi yuqori xavf.",
                    feedback_wrong_ru="Фишинговые письма часто давят срочностью и ведут на форму входа.",
                    feedback_wrong_uz="Fishing xatlar ko‘pincha shoshiltiradi va kirish formasiga olib boradi.",
                )
            ]
            for difficulty, points, penalty in [("easy", 20, -5), ("medium", 28, -8), ("hard", 38, -12)]
        },
    },
    {
        "slug": "account-shield",
        "title_ru": "Щит аккаунта",
        "title_uz": "Akkaunt qalqoni",
        "description_ru": "Настройте 2FA, найдите слабый пароль и заблокируйте подозрительную сессию.",
        "description_uz": "2FA ni yoqing, zaif parolni toping va shubhali sessiyani bloklang.",
        "category": "account_security",
        "scene_key": "account_lab",
        "is_default": False,
        "order": 3,
        "missions": {
            difficulty: [
                step(
                    prompt_ru="Какое действие лучше всего защищает аккаунт прямо сейчас?",
                    prompt_uz="Hozir akkauntni eng yaxshi himoya qiladigan harakat qaysi?",
                    correct_value="enable-2fa",
                    options=OPTIONS_ACCOUNT,
                    points=points,
                    penalty=penalty,
                    feedback_correct_ru="Верно: 2FA сильно снижает риск захвата аккаунта.",
                    feedback_correct_uz="To‘g‘ri: 2FA akkaunt egallanishi xavfini keskin kamaytiradi.",
                    feedback_wrong_ru="Если есть подозрительный вход, нельзя оставлять защиту без изменений.",
                    feedback_wrong_uz="Shubhali kirish bo‘lsa, himoyani o‘zgarishsiz qoldirmang.",
                )
            ]
            for difficulty, points, penalty in [("easy", 20, -5), ("medium", 28, -8), ("hard", 38, -12)]
        },
    },
    {
        "slug": "social-trap",
        "title_ru": "Социальная ловушка",
        "title_uz": "Ijtimoiy tuzoq",
        "description_ru": "Поговорите с NPC и распознайте давление, срочность и просьбу о коде.",
        "description_uz": "NPC bilan suhbatda bosim, shoshiltirish va kod so‘rovini aniqlang.",
        "category": "social_engineering",
        "scene_key": "call_room",
        "is_default": False,
        "order": 4,
        "missions": {
            difficulty: [
                step(
                    prompt_ru="NPC просит SMS-код и торопит. Что безопаснее?",
                    prompt_uz="NPC SMS kod so‘rayapti va shoshiltiryapti. Nima xavfsizroq?",
                    correct_value="call-bank",
                    options=OPTIONS_SOCIAL,
                    points=points,
                    penalty=penalty,
                    feedback_correct_ru="Верно: код никому не сообщаем, банк проверяем только по официальному номеру.",
                    feedback_correct_uz="To‘g‘ri: kodni hech kimga aytmaymiz, bankni faqat rasmiy raqam orqali tekshiramiz.",
                    feedback_wrong_ru="SMS-код и установка приложения по просьбе звонящего — типичный сценарий кражи денег.",
                    feedback_wrong_uz="Qo‘ng‘iroq qilgan odam so‘ragan SMS kod yoki ilova o‘rnatish — pul o‘g‘irlash sxemasi.",
                )
            ]
            for difficulty, points, penalty in [("easy", 20, -5), ("medium", 28, -8), ("hard", 38, -12)]
        },
    },
]


class Command(BaseCommand):
    help = "Seed 3D web game characters, scenarios and missions."

    def handle(self, *args, **options):
        for item in CHARACTERS:
            GameCharacter.objects.update_or_create(
                model_key=item["model_key"],
                defaults=item,
            )

        for item in SCENARIOS:
            mission_map = item["missions"]
            scene_key = item["scene_key"]
            scenario, _ = GameScenario3D.objects.update_or_create(
                slug=item["slug"],
                defaults={
                    key: value
                    for key, value in {**item, "is_published": True}.items()
                    if key not in {"missions", "scene_key"}
                },
            )
            for difficulty, steps in mission_map.items():
                mission, _ = GameMission.objects.update_or_create(
                    scenario=scenario,
                    difficulty=difficulty,
                    defaults={
                        "title_ru": f"{scenario.title_ru}: {difficulty}",
                        "title_uz": f"{scenario.title_uz}: {difficulty}",
                        "scene_key": scene_key,
                        "max_score": sum(max(item["points"], 0) for item in steps),
                    },
                )
                for order, item in enumerate(steps, start=1):
                    mission.steps.update_or_create(order=order, defaults=item)
        self.stdout.write(self.style.SUCCESS("3D web game content seeded."))
