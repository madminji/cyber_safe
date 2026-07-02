import json
from pathlib import Path

from django.core.management.base import BaseCommand

from apps.courses.models import Lesson, LessonBlock, LessonChoice, LessonQuestion, LessonTask


TOPICS = {
    "test": {
        "keywords": ("тестовый", "json"),
        "title": "JSON orqali test darsi",
        "summary": "Ushbu dars JSON import funksiyasini tekshirish uchun qo‘shilgan.",
        "content": "Bu dars platformaga darslarni JSON fayl orqali yuklash va qayta yuklashda dublikat yaratmasdan yangilashni tekshiradi.",
    },
    "phishing": {
        "keywords": ("фишинг", "ссылка", "поддельный сайт"),
        "title": "Fishing havolalari va soxta saytlarni aniqlash",
        "summary": "Havola, domen va xabar matnidagi xavf belgilarini tekshirishni o‘rganasiz.",
        "content": "Fishing havolalari bank, marketplace yoki davlat xizmati ko‘rinishida bo‘lishi mumkin. Xavfsiz yo‘l — havolani bosmasdan, xizmatni rasmiy ilova yoki qo‘lda kiritilgan manzil orqali ochish.",
    },
    "personal_data": {
        "keywords": ("личные данные", "деньги", "аккаунты"),
        "title": "Shaxsiy ma’lumotlar, pul va akkauntlarni himoya qilish",
        "summary": "Qaysi ma’lumotlarni ochiq aytish mumkin emasligini va akkauntlarni qanday himoyalashni bilib olasiz.",
        "content": "Telefon raqami, pasport rasmi, karta ma’lumotlari, parol va SMS-kodlar yuqori xavfli ma’lumotlar hisoblanadi. Ularni faqat ishonchli va rasmiy servislar orqali ishlatish kerak.",
    },
    "url_practice": {
        "keywords": ("url", "анализ сообщения"),
        "title": "Xabar va URL manzilini xavfsiz tahlil qilish",
        "summary": "Shubhali xabar va havolani bosmasdan tekshirish algoritmini mashq qilasiz.",
        "content": "URL tahlilida domen, yozuvdagi xatolar, qisqartirilgan havola, shoshirish va maxfiy ma’lumot so‘rash belgilariga e’tibor beriladi.",
    },
    "bank_call": {
        "keywords": ("звонок", "банка", "банк"),
        "title": "Bank nomidan qo‘ng‘iroq: xavfsiz javob berish",
        "summary": "Telefon orqali ijtimoiy muhandislik usullarini tanish va xavfsiz harakat qilishni o‘rganasiz.",
        "content": "Bank xodimi hech qachon SMS-kod, PIN-kod yoki parol so‘ramaydi. Shubhali qo‘ng‘iroqda suhbatni tugatib, bankka rasmiy raqam orqali o‘zingiz qo‘ng‘iroq qiling.",
    },
    "sms_codes": {
        "keywords": ("sms-код", "одноразовые", "пароли"),
        "title": "SMS-kodlar va bir martalik parollar xavfsizligi",
        "summary": "Nega tasdiqlash kodlarini hech kimga bermaslik kerakligini tushunasiz.",
        "content": "SMS-kod va OTP parol operatsiyani tasdiqlash kalitidir. Kodni aytish pul o‘tkazmasi, akkauntga kirish yoki parolni almashtirishga ruxsat berishi mumkin.",
    },
    "apk": {
        "keywords": ("apk", "telegram"),
        "title": "Telegram orqali yuborilgan APK fayllar xavfi",
        "summary": "Noma’lum ilovalarni o‘rnatish qanday xavf tug‘dirishini bilib olasiz.",
        "content": "APK fayl zararli dastur bo‘lishi mumkin. Ilovalarni faqat rasmiy do‘konlardan yoki rasmiy sayt orqali o‘rnating va telefon himoyasini o‘chirmang.",
    },
    "phone_settings": {
        "keywords": ("настройки телефона", "телефона"),
        "title": "Telefonning asosiy xavfsizlik sozlamalari",
        "summary": "Telefonni bloklash, yangilash va ilova ruxsatlarini tekshirishni o‘rganasiz.",
        "content": "Telefon xavfsizligi ekran qulfi, tizim yangilanishlari, ilova ruxsatlari, zaxira nusxa va noma’lum manbalardan o‘rnatishni cheklashdan boshlanadi.",
    },
    "online_shopping": {
        "keywords": ("покупки", "предоплата", "доставка", "продавцы"),
        "title": "Onlayn xaridlar: oldindan to‘lov va soxta sotuvchilar",
        "summary": "Xarid paytida sotuvchi, to‘lov va yetkazib berish xavflarini tekshirishni o‘rganasiz.",
        "content": "Soxta sotuvchilar arzon narx, shoshirish va oldindan to‘lov bilan aldaydi. Platforma ichidagi xavfsiz to‘lov, sharhlar va rasmiy yetkazib berish kanalini tekshiring.",
    },
    "fake_buyer": {
        "keywords": ("поддельный покупатель", "продавцов"),
        "title": "Soxta xaridor va sotuvchilar uchun fishing",
        "summary": "Sotuvchi bo‘lganingizda keladigan shubhali to‘lov havolalarini aniqlaysiz.",
        "content": "Soxta xaridor to‘lovni qabul qilish uchun havola yuborishi va karta ma’lumotlarini so‘rashi mumkin. Pul kelganini faqat bank ilovasida tekshiring.",
    },
    "fake_payments": {
        "keywords": ("фейковые выплаты", "государства", "помощь"),
        "title": "Soxta to‘lovlar va davlat yordami haqidagi xabarlar",
        "summary": "Yordam, subsidiya yoki yutuq haqidagi yolg‘on xabarlarni tekshirishni o‘rganasiz.",
        "content": "Firibgarlar davlat yordami, bonus yoki yutuq bahonasida havola, karta ma’lumoti yoki pasport rasmini so‘rashi mumkin. Ma’lumotni faqat rasmiy manbadan tekshiring.",
    },
    "loans": {
        "keywords": ("онлайн-займ", "займы", "документы"),
        "title": "Boshqa odam nomiga onlayn qarz: hujjatlarni himoya qilish",
        "summary": "Pasport rasmi va shaxsiy ma’lumotlarni qanday himoyalash kerakligini bilib olasiz.",
        "content": "Pasport fotosi va shaxsiy ma’lumotlar kredit yoki akkaunt ochishda ishlatilishi mumkin. Hujjatlarni begonalarga yubormang va servislarni rasmiy kanal orqali tekshiring.",
    },
    "pyramid": {
        "keywords": ("прибыль", "пирамид"),
        "title": "Yuqori foyda va moliyaviy piramidalarni aniqlash",
        "summary": "Tez boyish va kafolatlangan daromad va’dalaridagi xavfni ko‘rasiz.",
        "content": "Moliyaviy piramidalar yuqori daromad, tez qaror va yangi odam olib kelish talabi bilan ishlaydi. Investitsiyani hujjatlar, litsenziya va real risklar orqali tekshiring.",
    },
    "crypto": {
        "keywords": ("крипто", "романтические", "инвестиционные"),
        "title": "Kripto firibgarlik va romantik investitsiya sxemalari",
        "summary": "Ishonch munosabatlari orqali investitsiyaga jalb qilish xavfini tushunasiz.",
        "content": "Firibgar avval ishonch qozonadi, keyin kripto yoki investitsiya platformasiga pul kiritishni taklif qiladi. Pul chiqarish imkoni va platforma haqiqiyligini mustaqil tekshiring.",
    },
    "passwords": {
        "keywords": ("парол", "менеджер"),
        "title": "Ishonchli parollar va parol menejeri",
        "summary": "Har bir akkaunt uchun alohida kuchli parol ishlatish sababini bilasiz.",
        "content": "Kuchli parol uzun, takrorlanmagan va taxmin qilish qiyin bo‘ladi. Parol menejeri har bir servis uchun alohida parol saqlashga yordam beradi.",
    },
    "telegram_2fa": {
        "keywords": ("двухфактор", "аутентификация", "telegram"),
        "title": "Ikki bosqichli himoya va Telegram xavfsizligi",
        "summary": "Telegram akkauntini qo‘shimcha parol, sessiyalar va maxfiylik sozlamalari bilan himoyalashni o‘rganasiz.",
        "content": "Telegram’da ikki bosqichli parolni yoqing, faol sessiyalarni tekshiring va telefon raqami ko‘rinishini cheklang. Begona qurilmalarni darhol o‘chiring.",
    },
    "analyzer": {
        "keywords": ("анализатор", "sms", "писем"),
        "title": "Havola, SMS va xabar analizatoridan foydalanish",
        "summary": "Shubhali matn yoki havolani xavfsiz tekshirish usulini o‘rganasiz.",
        "content": "Analizator xavf belgilarini ko‘rsatadi, lekin yakuniy qaror uchun rasmiy manbani ham tekshirish kerak. Maxfiy kod va parollarni analizatorga ham kiritmang.",
    },
    "report_number": {
        "keywords": ("проверять номер", "репорт"),
        "title": "Raqamni tekshirish va xabar yuborish",
        "summary": "Shubhali raqam bo‘yicha ma’lumotni tekshirish va moderatsiyaga xabar yuborishni o‘rganasiz.",
        "content": "Raqam bazada yo‘q bo‘lsa, bu uning xavfsizligini isbotlamaydi. Dalillarni saqlang, suhbatni davom ettirmang va aniq ma’lumot bilan xabar yuboring.",
    },
    "incident": {
        "keywords": ("уже перешли", "потеряли деньги"),
        "title": "Havolaga o‘tib qo‘ygan yoki pul yo‘qotgan bo‘lsangiz nima qilish kerak",
        "summary": "Hodisa yuz bergandan keyingi birinchi xavfsiz qadamlarni bilib olasiz.",
        "content": "Agar havolaga o‘tgan, kod bergan yoki pul yo‘qotgan bo‘lsangiz, kartani bloklang, parollarni almashtiring, sessiyalarni o‘chiring va dalillarni saqlang.",
    },
    "final": {
        "keywords": ("итоговый", "план кибербезопасности"),
        "title": "Yakuniy amaliyot: shaxsiy kiberxavfsizlik rejasi",
        "summary": "O‘zingiz va oilangiz uchun kundalik xavfsizlik qoidalarini tuzasiz.",
        "content": "Shaxsiy reja parollar, ikki bosqichli himoya, rasmiy manbalarni tekshirish, telefon sozlamalari va firibgarlikda tezkor harakat qilish qoidalaridan iborat bo‘ladi.",
    },
    "general": {
        "keywords": (),
        "title": "Kiberxavfsizlik asoslari",
        "summary": "Raqamli xavfsizlik bo‘yicha asosiy qoidalarni o‘rganasiz.",
        "content": "Kiberxavfsizlik shoshmaslik, manbani tekshirish, maxfiy kodlarni bermaslik va rasmiy kanallardan foydalanish odatlaridan boshlanadi.",
    },
}


BLOCK_TITLES = {
    "theory": "Nazariya",
    "definition": "Ta’rif",
    "example": "Misol",
    "warning": "Xavf belgilari",
    "checklist": "Xavfsiz algoritm",
    "note": "Eslatma",
    "code": "Kod",
    "materials": "Qo‘shimcha materiallar",
}


MODULE_TITLES = {
    "1": "1-modul. Raqamli xavfsizlik asoslari",
    "2": "2-modul. Fishing: havolalar, saytlar va soxta sahifalar",
    "3": "3-modul. Telefon, SMS-kodlar va messenjerlar xavfsizligi",
    "4": "4-modul. Onlayn savdo va moliyaviy firibgarliklar",
    "5": "5-modul. Akkauntlar, parollar va ikki bosqichli himoya",
    "6": "6-modul. Hodisaga javob berish va shaxsiy xavfsizlik rejasi",
    "safe-clicking": "Xavfsiz bosish",
    "phishing": "Fishing",
    "admin-import-test": "Import testi",
}


def module_title_uz(module_slug: str, module_title_ru: str, topic: dict[str, str]) -> str:
    if module_slug in MODULE_TITLES:
        return MODULE_TITLES[module_slug]
    title = (module_title_ru or "").lower()
    if "фишинг" in title:
        return "Fishing: havolalar, saytlar va soxta sahifalar"
    if "sms" in title or "телефон" in title or "telegram" in title:
        return "Telefon, SMS-kodlar va messenjerlar xavfsizligi"
    if "покуп" in title or "финанс" in title or "деньг" in title:
        return "Onlayn savdo va moliyaviy xavfsizlik"
    if "парол" in title or "аккаунт" in title:
        return "Akkauntlar va parollar xavfsizligi"
    if module_title_ru:
        return topic["title"]
    return ""


def topic_for_title(title_ru: str) -> dict[str, str]:
    title = title_ru.lower()
    for topic in TOPICS.values():
        if any(keyword in title for keyword in topic["keywords"]):
            return topic
    return TOPICS["general"]


def topic_for(lesson: Lesson) -> dict[str, str]:
    return topic_for_title(lesson.title_ru)


def topic_key_for(lesson: Lesson) -> str:
    title = lesson.title_ru.lower()
    for key, topic in TOPICS.items():
        if any(keyword in title for keyword in topic["keywords"]):
            return key
    return "general"


def block_body(block: LessonBlock, topic: dict[str, str]) -> str:
    if block.type == "definition":
        return f"{topic['title']} — foydalanuvchi pul, ma’lumot yoki akkaunt xavfsizligiga ta’sir qiladigan holatlarni to‘g‘ri baholash mavzusidir."
    if block.type == "example":
        return "Masalan, xabarda shoshilinch havola, kod so‘rovi yoki kutilmagan yutuq bo‘lsa, uni avval rasmiy kanal orqali tekshirish kerak."
    if block.type == "warning":
        return "Quyidagi belgilar xavfni bildiradi: shoshirish, qo‘rqitish, maxfiy kod so‘rash, noma’lum havola yoki ilova yuborish."
    if block.type == "checklist":
        return "Harakat qilishdan oldin to‘xtang, manbani tekshiring va maxfiy ma’lumotlarni hech kimga bermang."
    if block.type == "note":
        return "Asosiy qoida: muhim amallarni faqat rasmiy ilova, rasmiy sayt yoki ishonchli aloqa kanali orqali bajaring."
    return topic["content"]


def localized_items(block_type: str) -> list[dict[str, str]]:
    if block_type == "warning":
        uz_items = [
            "Sizdan SMS-kod, parol yoki karta ma’lumotlari so‘raladi.",
            "Xabarda shoshilish yoki qo‘rqitish bor.",
            "Havola yoki ilova norasmiy manbadan yuborilgan.",
            "Yutuq, yordam yoki katta foyda va’da qilinadi.",
        ]
    else:
        uz_items = [
            "To‘xtang va darhol javob bermang.",
            "Manbani rasmiy kanal orqali tekshiring.",
            "SMS-kod, parol va karta ma’lumotlarini bermang.",
            "Dalillarni saqlang va kerak bo‘lsa xabar yuboring.",
        ]
    return [{"ru": item["ru"], "uz": uz} for item, uz in zip([], uz_items)]


def update_json_items(data: dict, block_type: str) -> dict:
    data = dict(data or {})
    old_items = data.get("items")
    if isinstance(old_items, list) and old_items:
        default_uz = [
            "To‘xtang va vaziyatni tekshiring.",
            "Rasmiy manba orqali tasdiqlang.",
            "Maxfiy kod va parollarni bermang.",
            "Dalillarni saqlang.",
            "Zarurat bo‘lsa bank yoki qo‘llab-quvvatlash xizmatiga murojaat qiling.",
        ]
        if block_type == "warning":
            default_uz = [
                "Shoshilinch havola yoki kod so‘rovi bor.",
                "Qo‘rqitish, yutuq yoki katta foyda va’da qilinadi.",
                "Noma’lum ilova yoki fayl yuborilgan.",
                "Pasport, karta yoki parol ma’lumotlari so‘raladi.",
                "Manba rasmiy kanal orqali tasdiqlanmagan.",
            ]
        data["items"] = [
            {
                "ru": item if isinstance(item, str) else item.get("ru") or item.get("text") or "",
                "uz": default_uz[index % len(default_uz)],
            }
            for index, item in enumerate(old_items)
        ]
    return data


def update_task_data(data: dict, task_type: str) -> dict:
    data = dict(data or {})
    old_items = data.get("items")
    if isinstance(old_items, list) and old_items:
        uz_texts = [
            "Xabarda havola va shoshirish bor. Uni rasmiy kanal orqali tekshiring.",
            "Maxfiy kod yoki karta ma’lumotlarini so‘rash xavf belgisidir.",
            "Rasmiy ilova yoki sayt orqali mustaqil tekshirish xavfsizroq.",
            "Noma’lum fayl yoki APK o‘rnatmang.",
        ]
        new_items = []
        for index, item in enumerate(old_items):
            if isinstance(item, dict):
                next_item = dict(item)
                text = item.get("text")
                if isinstance(text, dict):
                    ru = text.get("ru") or text.get("text") or ""
                else:
                    ru = text or item.get("ru") or ""
                next_item["text"] = {"ru": ru, "uz": uz_texts[index % len(uz_texts)]}
                new_items.append(next_item)
            else:
                new_items.append({"text": {"ru": str(item), "uz": uz_texts[index % len(uz_texts)]}})
        data["items"] = new_items
    return data


class Command(BaseCommand):
    help = "Fill Uzbek lesson fields with Latin Uzbek baseline localization."

    def add_arguments(self, parser):
        parser.add_argument(
            "--json-dir",
            help="Also localize every lesson JSON file in this directory.",
        )

    def handle(self, *args, **options):
        lessons_updated = 0
        for lesson in Lesson.objects.select_related("course").prefetch_related(
            "blocks",
            "tasks",
            "questions__choices",
        ):
            topic = topic_for(lesson)
            lesson.module_title_uz = module_title_uz(
                lesson.module_slug,
                lesson.module_title_ru,
                topic,
            )
            lesson.title_uz = topic["title"]
            lesson.summary_uz = topic["summary"]
            lesson.content_uz = (
                f"Maqsad\n\n{topic['summary']}\n\n"
                f"Nazariya\n\n{topic['content']}\n\n"
                "Xavfsiz algoritm\n\n"
                "Shoshilmang, manbani tekshiring, maxfiy kodlarni bermang va muhim amallarni faqat rasmiy kanal orqali bajaring."
            )
            lesson.save(
                update_fields=(
                    "module_title_uz",
                    "title_uz",
                    "summary_uz",
                    "content_uz",
                )
            )
            lessons_updated += 1

            for block in lesson.blocks.all():
                block.title_uz = BLOCK_TITLES.get(block.type, "Bo‘lim")
                block.body_uz = block_body(block, topic)
                block.data = update_json_items(block.data, block.type)
                block.save(update_fields=("title_uz", "body_uz", "data"))

            for index, task in enumerate(lesson.tasks.all(), start=1):
                task.title_uz = f"Topshiriq {index}"
                if task.type == "checklist":
                    task.instruction_uz = "Darsdan keyin bajariladigan xavfsizlik qadamlarini belgilang."
                elif task.type == "scenario":
                    task.instruction_uz = "Vaziyatlarni o‘qing va xavfsiz javobni tanlang."
                elif task.type == "sorting":
                    task.instruction_uz = "Ma’lumot yoki xabarlarni xavf darajasi bo‘yicha ajrating."
                else:
                    task.instruction_uz = "O‘zingiz uchun qisqa va aniq xavfsizlik qoidasini yozing."
                task.data = update_task_data(task.data, task.type)
                task.save(update_fields=("title_uz", "instruction_uz", "data"))

            for question in lesson.questions.all():
                question.text_uz = "Ushbu vaziyatda eng xavfsiz harakat qaysi?"
                question.explanation_uz = (
                    "Eng xavfsiz yo‘l — rasmiy kanal orqali tekshirish va maxfiy kod, parol yoki karta ma’lumotlarini bermaslik."
                )
                question.save(update_fields=("text_uz", "explanation_uz"))
                incorrect_index = 1
                for choice in question.choices.all():
                    if choice.is_correct:
                        choice.text_uz = "Rasmiy kanal orqali tekshirish va maxfiy ma’lumotlarni bermaslik"
                    else:
                        variants = [
                            "Havolani darhol ochish",
                            "SMS-kodni suhbatdoshga aytish",
                            "Noma’lum ilovani o‘rnatish",
                        ]
                        choice.text_uz = variants[(incorrect_index - 1) % len(variants)]
                        incorrect_index += 1
                    choice.save(update_fields=("text_uz",))

        json_updated = 0
        if options.get("json_dir"):
            source = Path(options["json_dir"])
            for lesson_file in sorted(source.rglob("*.json")):
                payload = json.loads(lesson_file.read_text(encoding="utf-8"))
                title_ru = (payload.get("title") or {}).get("ru", "")
                topic = topic_for_title(title_ru)
                payload["title"]["uz"] = topic["title"]
                payload.setdefault("module", {}).setdefault("title", {})["uz"] = (
                    module_title_uz(
                        (payload.get("module") or {}).get("slug", ""),
                        (payload.get("module") or {}).get("title", {}).get("ru", ""),
                        topic,
                    )
                )
                payload["summary"]["uz"] = topic["summary"]
                payload["content"]["uz"] = (
                    f"Maqsad\n\n{topic['summary']}\n\n"
                    f"Nazariya\n\n{topic['content']}\n\n"
                    "Xavfsiz algoritm\n\n"
                    "Shoshilmang, manbani tekshiring, maxfiy kodlarni bermang va muhim amallarni faqat rasmiy kanal orqali bajaring."
                )
                for block in payload.get("blocks", []):
                    block_type = block.get("type", "note")
                    block.setdefault("title", {})["uz"] = BLOCK_TITLES.get(block_type, "Bo‘lim")
                    block.setdefault("body", {})["uz"] = block_body(
                        type("JsonBlock", (), {"type": block_type})(),
                        topic,
                    )
                    data = update_json_items(
                        {key: value for key, value in block.items() if key not in {"type", "order", "title", "body"}},
                        block_type,
                    )
                    if "items" in data:
                        block["items"] = data["items"]
                for index, task in enumerate(payload.get("tasks", []), start=1):
                    task_type = task.get("type", "text")
                    task.setdefault("title", {})["uz"] = f"Topshiriq {index}"
                    if task_type == "checklist":
                        instruction = "Darsdan keyin bajariladigan xavfsizlik qadamlarini belgilang."
                    elif task_type == "scenario":
                        instruction = "Vaziyatlarni o‘qing va xavfsiz javobni tanlang."
                    elif task_type == "sorting":
                        instruction = "Ma’lumot yoki xabarlarni xavf darajasi bo‘yicha ajrating."
                    else:
                        instruction = "O‘zingiz uchun qisqa va aniq xavfsizlik qoidasini yozing."
                    task.setdefault("instruction", {})["uz"] = instruction
                    task["data"] = update_task_data(task.get("data") or {}, task_type)
                for question in payload.get("quiz", []):
                    question.setdefault("text", {})["uz"] = (
                        "Ushbu vaziyatda eng xavfsiz harakat qaysi?"
                    )
                    question.setdefault("explanation", {})["uz"] = (
                        "Eng xavfsiz yo‘l — rasmiy kanal orqali tekshirish va maxfiy kod, parol yoki karta ma’lumotlarini bermaslik."
                    )
                    incorrect_index = 1
                    for choice in question.get("choices", []):
                        choice.setdefault("text", {})
                        if choice.get("is_correct"):
                            choice["text"]["uz"] = (
                                "Rasmiy kanal orqali tekshirish va maxfiy ma’lumotlarni bermaslik"
                            )
                        else:
                            variants = [
                                "Havolani darhol ochish",
                                "SMS-kodni suhbatdoshga aytish",
                                "Noma’lum ilovani o‘rnatish",
                            ]
                            choice["text"]["uz"] = variants[
                                (incorrect_index - 1) % len(variants)
                            ]
                            incorrect_index += 1
                lesson_file.write_text(
                    json.dumps(payload, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
                json_updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Localized Uzbek fields for {lessons_updated} lessons"
                + (f" and {json_updated} JSON files." if options.get("json_dir") else ".")
            )
        )
