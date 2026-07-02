from django.core.management.base import BaseCommand

from apps.game.models import GameChoice, GameScenario, GameStep

SCENARIOS = [
    {
        "slug": "fake-bank-security-call",
        "title_ru": "Звонок из «службы безопасности банка»",
        "title_uz": "«Bank xavfsizlik xizmati» qo‘ng‘irog‘i",
        "description_ru": (
            "Мошенник сообщает о подозрительной операции и пытается получить "
            "SMS-код или заставить перевести деньги."
        ),
        "description_uz": (
            "Firibgar shubhali operatsiya haqida aytib, SMS kodini olish yoki "
            "pul o‘tkazishga majburlashga urinadi."
        ),
        "scam_type": "bank_call",
        "interface_type": "call",
        "difficulty": "easy",
        "order": 1,
        "steps": [
            {
                "message_ru": (
                    "Здравствуйте. Я сотрудник службы безопасности банка. "
                    "С вашей карты пытаются перевести 4 800 000 сум. Это вы?"
                ),
                "message_uz": (
                    "Assalomu alaykum. Men bank xavfsizlik xizmati xodimiman. "
                    "Kartangizdan 4 800 000 so‘m o‘tkazishga urinishmoqda. Bu sizmi?"
                ),
                "tactic_ru": "Страх и авторитет",
                "tactic_uz": "Qo‘rquv va obro‘",
                "choices": [
                    (
                        "Нет! Что мне делать?",
                        "Yo‘q! Nima qilishim kerak?",
                        "Вы подтвердили тревогу и позволили звонящему вести разговор.",
                        "Siz xavotirni tasdiqlab, suhbatni firibgar boshqarishiga yo‘l berdingiz.",
                        0,
                    ),
                    (
                        "Я завершу звонок и сам позвоню в банк.",
                        "Qo‘ng‘iroqni tugatib, bankka o‘zim qo‘ng‘iroq qilaman.",
                        "Правильно. Независимая проверка обрывает сценарий мошенника.",
                        "To‘g‘ri. Mustaqil tekshiruv firibgar ssenariysini buzadi.",
                        10,
                    ),
                    (
                        "Назовите номер карты, чтобы я проверил.",
                        "Tekshirishim uchun karta raqamini ayting.",
                        "Не продолжайте проверку личности внутри подозрительного звонка.",
                        "Shubhali qo‘ng‘iroq ichida shaxsni tekshirishni davom ettirmang.",
                        3,
                    ),
                ],
            },
            {
                "message_ru": (
                    "Не кладите трубку — перевод произойдёт через две минуты. "
                    "Я отправил код отмены, продиктуйте его."
                ),
                "message_uz": (
                    "Telefonni qo‘ymang — pul ikki daqiqada o‘tkaziladi. "
                    "Bekor qilish kodini yubordim, uni ayting."
                ),
                "tactic_ru": "Срочность и запрос SMS-кода",
                "tactic_uz": "Shoshirish va SMS kodini so‘rash",
                "choices": [
                    (
                        "Продиктовать код, чтобы отменить перевод.",
                        "O‘tkazmani bekor qilish uchun kodni aytish.",
                        "SMS-код подтверждает действие от вашего имени. Его нельзя сообщать.",
                        "SMS kodi sizning nomingizdan amalni tasdiqlaydi. Uni aytib bo‘lmaydi.",
                        -5,
                    ),
                    (
                        "Ничего не сообщать и завершить звонок.",
                        "Hech narsa aytmasdan qo‘ng‘iroqni tugatish.",
                        "Правильно. Настоящий банк не запрашивает одноразовые коды.",
                        "To‘g‘ri. Haqiqiy bank bir martalik kodlarni so‘ramaydi.",
                        10,
                    ),
                    (
                        "Сообщить только первые три цифры.",
                        "Faqat dastlabki uch raqamni aytish.",
                        "Нельзя сообщать даже часть секретного кода.",
                        "Maxfiy kodning bir qismini ham aytib bo‘lmaydi.",
                        0,
                    ),
                ],
            },
            {
                "message_ru": (
                    "Тогда срочно переведите деньги на резервный безопасный счёт. "
                    "После проверки они вернутся автоматически."
                ),
                "message_uz": (
                    "Unda pulni zudlik bilan zaxira xavfsiz hisobga o‘tkazing. "
                    "Tekshiruvdan keyin avtomatik qaytariladi."
                ),
                "tactic_ru": "Вымышленный безопасный счёт",
                "tactic_uz": "Soxta xavfsiz hisob",
                "choices": [
                    (
                        "Перевести небольшую сумму для проверки.",
                        "Tekshirish uchun kichik summa o‘tkazish.",
                        "Безопасных счетов для спасения денег не существует.",
                        "Pulni qutqarish uchun xavfsiz hisob mavjud emas.",
                        -5,
                    ),
                    (
                        "Открыть приложение банка и выполнить перевод.",
                        "Bank ilovasini ochib, pul o‘tkazish.",
                        "Вы выполняете финансовую операцию по указанию неизвестного лица.",
                        "Siz notanish shaxs ko‘rsatmasi bilan moliyaviy amal bajaryapsiz.",
                        -5,
                    ),
                    (
                        "Отказаться, заблокировать звонящего и связаться с банком.",
                        "Rad etish, raqamni bloklash va bank bilan bog‘lanish.",
                        "Это безопасная последовательность действий.",
                        "Bu xavfsiz harakatlar ketma-ketligi.",
                        10,
                    ),
                ],
            },
        ],
    },
    {
        "slug": "telegram-apk-delivery",
        "title_ru": "«Посылка» и APK-файл в Telegram",
        "title_uz": "Telegram’dagi «posilka» va APK fayl",
        "description_ru": (
            "Лжекурьер присылает приложение для подтверждения доставки и "
            "пытается получить доступ к телефону."
        ),
        "description_uz": (
            "Soxta kuryer yetkazib berishni tasdiqlash uchun ilova yuborib, "
            "telefonga kirishga urinadi."
        ),
        "scam_type": "malware",
        "interface_type": "chat",
        "difficulty": "medium",
        "order": 2,
        "steps": [
            {
                "message_ru": (
                    "Вам пришла посылка. Установите приложение delivery.apk, "
                    "чтобы выбрать время доставки."
                ),
                "message_uz": (
                    "Sizga posilka keldi. Yetkazib berish vaqtini tanlash uchun "
                    "delivery.apk ilovasini o‘rnating."
                ),
                "tactic_ru": "Любопытство и вредоносный файл",
                "tactic_uz": "Qiziqish va zararli fayl",
                "choices": [
                    (
                        "Установить приложение.",
                        "Ilovani o‘rnatish.",
                        "APK из сообщения может перехватывать SMS и банковские данные.",
                        "Xabardagi APK SMS va bank ma’lumotlarini o‘g‘irlashi mumkin.",
                        -5,
                    ),
                    (
                        "Удалить файл и проверить доставку через официальный сервис.",
                        "Faylni o‘chirib, rasmiy xizmat orqali tekshirish.",
                        "Правильно. Используйте только официальный сайт или приложение.",
                        "To‘g‘ri. Faqat rasmiy sayt yoki ilovadan foydalaning.",
                        10,
                    ),
                    (
                        "Переслать файл знакомому для проверки.",
                        "Faylni tekshirish uchun tanishga yuborish.",
                        "Так вы подвергаете риску другого человека.",
                        "Bu bilan boshqa odamni xavf ostiga qo‘yasiz.",
                        0,
                    ),
                ],
            },
            {
                "message_ru": (
                    "Без приложения посылку вернут отправителю через 15 минут. "
                    "Разрешите приложению доступ к SMS."
                ),
                "message_uz": (
                    "Ilovasiz posilka 15 daqiqada qaytariladi. "
                    "Ilovaga SMSga kirishga ruxsat bering."
                ),
                "tactic_ru": "Дефицит времени и опасные разрешения",
                "tactic_uz": "Vaqt bosimi va xavfli ruxsatlar",
                "choices": [
                    (
                        "Разрешить доступ только на время.",
                        "Faqat vaqtincha ruxsat berish.",
                        "Даже временного доступа достаточно для перехвата кода.",
                        "Vaqtinchalik ruxsat ham kodni tutib olish uchun yetarli.",
                        -5,
                    ),
                    (
                        "Отказаться и прекратить переписку.",
                        "Rad etib, yozishmani tugatish.",
                        "Правильно. Срочность используется, чтобы отключить критическое мышление.",
                        "To‘g‘ri. Shoshirish tanqidiy fikrlashni susaytirish uchun ishlatiladi.",
                        10,
                    ),
                    (
                        "Спросить, почему нужен доступ к SMS.",
                        "Nega SMSga kirish kerakligini so‘rash.",
                        "Объяснение мошенника не сделает опасное разрешение безопасным.",
                        "Firibgarning izohi xavfli ruxsatni xavfsiz qilmaydi.",
                        3,
                    ),
                ],
            },
        ],
    },
    {
        "slug": "telegram-account-vote",
        "title_ru": "Захват Telegram через «голосование»",
        "title_uz": "«Ovoz berish» orqali Telegramni egallash",
        "description_ru": "Сообщение от взломанного знакомого ведёт на поддельный вход в Telegram.",
        "description_uz": "Buzilgan tanish akkauntidan kelgan xabar Telegramning soxta kirish sahifasiga olib boradi.",
        "scam_type": "account_takeover",
        "interface_type": "chat",
        "difficulty": "medium",
        "order": 3,
        "steps": [
            {
                "message_ru": "Привет! Проголосуй за мою племянницу. Нужно войти через Telegram по ссылке.",
                "message_uz": "Salom! Jiyanimga ovoz ber. Havola orqali Telegram bilan kirish kerak.",
                "tactic_ru": "Доверие к знакомому аккаунту",
                "tactic_uz": "Tanish akkauntiga ishonch",
                "choices": [
                    (
                        "Открыть ссылку и войти.",
                        "Havolani ochib kirish.",
                        "Аккаунт знакомого мог быть взломан, а форма входа — поддельной.",
                        "Tanish akkaunti buzilgan, kirish shakli esa soxta bo‘lishi mumkin.",
                        -5,
                    ),
                    (
                        "Позвонить знакомому и проверить просьбу.",
                        "Tanishga qo‘ng‘iroq qilib so‘rovni tekshirish.",
                        "Правильно. Второй канал помогает обнаружить захват аккаунта.",
                        "To‘g‘ri. Ikkinchi kanal akkaunt buzilganini aniqlashga yordam beradi.",
                        10,
                    ),
                    (
                        "Переслать ссылку другим.",
                        "Havolani boshqalarga yuborish.",
                        "Так фишинговая ссылка распространяется дальше.",
                        "Bu fishing havolasini yanada tarqatadi.",
                        -2,
                    ),
                ],
            },
            {
                "message_ru": "Telegram прислал код. Пришли его мне — сайт плохо работает.",
                "message_uz": "Telegram kod yubordi. Uni menga jo‘nat — sayt yaxshi ishlamayapti.",
                "tactic_ru": "Запрос кода входа",
                "tactic_uz": "Kirish kodini so‘rash",
                "choices": [
                    (
                        "Отправить код.",
                        "Kodni yuborish.",
                        "Это даст мошеннику доступ к вашему Telegram.",
                        "Bu firibgarga Telegram akkauntingizga kirish imkonini beradi.",
                        -5,
                    ),
                    (
                        "Не сообщать код и проверить активные сеансы.",
                        "Kodni bermasdan faol seanslarni tekshirish.",
                        "Правильно. Также включите двухэтапную проверку.",
                        "To‘g‘ri. Ikki bosqichli himoyani ham yoqing.",
                        10,
                    ),
                    (
                        "Отправить только первые цифры.",
                        "Faqat birinchi raqamlarni yuborish.",
                        "Нельзя передавать никакую часть секретного кода.",
                        "Maxfiy kodning hech bir qismini berib bo‘lmaydi.",
                        0,
                    ),
                ],
            },
        ],
    },
    {
        "slug": "marketplace-fake-payment",
        "title_ru": "Покупатель и поддельная оплата",
        "title_uz": "Xaridor va soxta to‘lov",
        "description_ru": "Покупатель уводит продавца из маркетплейса и присылает фальшивый чек.",
        "description_uz": "Xaridor sotuvchini marketpleysdan tashqariga olib chiqib, soxta chek yuboradi.",
        "scam_type": "marketplace",
        "interface_type": "website",
        "difficulty": "medium",
        "order": 4,
        "steps": [
            {
                "message_ru": "Я оплатил товар через курьера. Откройте ссылку и введите карту, чтобы получить деньги.",
                "message_uz": "Tovarni kuryer orqali to‘ladim. Pulni olish uchun havolani ochib karta kiriting.",
                "tactic_ru": "Поддельная доставка и платёжная форма",
                "tactic_uz": "Soxta yetkazib berish va to‘lov shakli",
                "choices": [
                    (
                        "Ввести данные карты.",
                        "Karta ma’lumotlarini kiritish.",
                        "Для получения денег не нужны CVV и SMS-код.",
                        "Pul olish uchun CVV va SMS kodi kerak emas.",
                        -5,
                    ),
                    (
                        "Продолжить только внутри официальной площадки.",
                        "Faqat rasmiy platforma ichida davom etish.",
                        "Правильно. Не переходите на платёжные страницы покупателя.",
                        "To‘g‘ri. Xaridor yuborgan to‘lov sahifalariga o‘tmang.",
                        10,
                    ),
                    (
                        "Открыть ссылку в инкогнито.",
                        "Havolani inkognito rejimida ochish.",
                        "Инкогнито не защищает от фишинга.",
                        "Inkognito fishingdan himoya qilmaydi.",
                        0,
                    ),
                ],
            },
            {
                "message_ru": "Вот чек. Деньги уже отправлены, отдайте товар курьеру.",
                "message_uz": "Mana chek. Pul yuborildi, tovarni kuryerga bering.",
                "tactic_ru": "Поддельное доказательство оплаты",
                "tactic_uz": "Soxta to‘lov dalili",
                "choices": [
                    (
                        "Передать товар по скриншоту.",
                        "Skrinshot bo‘yicha tovarni berish.",
                        "Изображение чека легко подделать.",
                        "Chek rasmini oson soxtalashtirish mumkin.",
                        -5,
                    ),
                    (
                        "Проверить фактическое зачисление в своём банке.",
                        "O‘z bankingizda haqiqiy tushumni tekshirish.",
                        "Правильно. Только ваш банк подтверждает получение денег.",
                        "To‘g‘ri. Pul tushganini faqat bankingiz tasdiqlaydi.",
                        10,
                    ),
                    (
                        "Попросить фото чека получше.",
                        "Chekning yaxshiroq rasmini so‘rash.",
                        "Качество изображения не подтверждает платёж.",
                        "Rasm sifati to‘lovni tasdiqlamaydi.",
                        2,
                    ),
                ],
            },
        ],
    },
    {
        "slug": "ai-family-emergency",
        "title_ru": "Звонок родственника с поддельным голосом",
        "title_uz": "Qarindoshning soxta ovozli qo‘ng‘irog‘i",
        "description_ru": "Знакомый голос сообщает об аварии и требует срочный перевод.",
        "description_uz": "Tanish ovoz avariya haqida aytib, zudlik bilan pul o‘tkazishni talab qiladi.",
        "scam_type": "ai_impersonation",
        "interface_type": "call",
        "difficulty": "hard",
        "order": 5,
        "steps": [
            {
                "message_ru": "Мама, я попал в аварию. Телефон разбит, звоню с чужого. Срочно нужны деньги.",
                "message_uz": "Ona, avariyaga tushdim. Telefonim buzildi, begona raqamdan qo‘ng‘iroq qilyapman. Tez pul kerak.",
                "tactic_ru": "Поддельный голос и семейная тревога",
                "tactic_uz": "Soxta ovoz va oilaviy xavotir",
                "choices": [
                    (
                        "Сразу спросить номер карты.",
                        "Darhol karta raqamini so‘rash.",
                        "Вы продолжаете действовать внутри навязанного сценария.",
                        "Siz firibgar yaratgan ssenariy ichida harakatni davom ettiryapsiz.",
                        -3,
                    ),
                    (
                        "Завершить звонок и перезвонить на сохранённый номер.",
                        "Qo‘ng‘iroqni tugatib, saqlangan raqamga qayta qo‘ng‘iroq qilish.",
                        "Правильно. Знакомый голос больше не является достаточным доказательством.",
                        "To‘g‘ri. Tanish ovoz endi yetarli dalil emas.",
                        10,
                    ),
                    (
                        "Поверить, потому что голос похож.",
                        "Ovoz o‘xshagani uchun ishonish.",
                        "ИИ может реалистично имитировать голос.",
                        "Sun’iy intellekt ovozni realistik taqlid qilishi mumkin.",
                        -5,
                    ),
                ],
            },
            {
                "message_ru": "Не звони никому: полиция запретила. Переведи деньги сейчас на карту друга.",
                "message_uz": "Hech kimga qo‘ng‘iroq qilma: politsiya taqiqladi. Pulni hozir do‘stim kartasiga o‘tkaz.",
                "tactic_ru": "Изоляция и срочность",
                "tactic_uz": "Yakkalash va shoshirish",
                "choices": [
                    (
                        "Выполнить просьбу.",
                        "So‘rovni bajarish.",
                        "Запрет на проверку — сильный признак мошенничества.",
                        "Tekshirishni taqiqlash — firibgarlikning kuchli belgisi.",
                        -5,
                    ),
                    (
                        "Связаться с родственником и другим членом семьи.",
                        "Qarindosh va boshqa oila a’zosi bilan bog‘lanish.",
                        "Правильно. Независимая проверка важнее срочности.",
                        "To‘g‘ri. Mustaqil tekshiruv shoshilinchlikdan muhimroq.",
                        10,
                    ),
                    (
                        "Перевести небольшую сумму.",
                        "Kichik summa o‘tkazish.",
                        "Проверочный перевод всё равно отправляет деньги мошеннику.",
                        "Sinov o‘tkazmasi ham pulni firibgarga yuboradi.",
                        -2,
                    ),
                ],
            },
        ],
    },
]


class Command(BaseCommand):
    help = "Create or update CyberSafe fraud simulation scenarios."

    def handle(self, *args, **options):
        for scenario_data in SCENARIOS:
            steps = scenario_data["steps"]
            scenario, _ = GameScenario.objects.update_or_create(
                slug=scenario_data["slug"],
                defaults={
                    key: value
                    for key, value in scenario_data.items()
                    if key not in {"slug", "steps"}
                }
                | {"is_published": True},
            )
            for step_order, step_data in enumerate(steps, start=1):
                choices = step_data["choices"]
                step, _ = GameStep.objects.update_or_create(
                    scenario=scenario,
                    order=step_order,
                    defaults={
                        key: value for key, value in step_data.items() if key != "choices"
                    },
                )
                for choice_order, choice_data in enumerate(choices, start=1):
                    text_ru, text_uz, feedback_ru, feedback_uz, points = choice_data
                    GameChoice.objects.update_or_create(
                        step=step,
                        order=choice_order,
                        defaults={
                            "text_ru": text_ru,
                            "text_uz": text_uz,
                            "feedback_ru": feedback_ru,
                            "feedback_uz": feedback_uz,
                            "points": points,
                        },
                    )
        self.stdout.write(self.style.SUCCESS("Seeded game scenarios."))
