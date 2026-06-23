from django.core.management.base import BaseCommand

from apps.courses.models import Course, Lesson, LessonChoice, LessonQuestion

COURSES = [
    {
        "slug": "digital-safety-basics",
        "title_ru": "Основы цифровой безопасности",
        "title_uz": "Raqamli xavfsizlik asoslari",
        "description_ru": (
            "Практический курс о защите банковских данных, аккаунтов и телефона "
            "от самых распространённых схем мошенничества."
        ),
        "description_uz": (
            "Bank ma’lumotlari, akkauntlar va telefonni keng tarqalgan "
            "firibgarlik usullaridan himoya qilish bo‘yicha amaliy kurs."
        ),
        "level": "basic",
        "duration_minutes": 65,
        "order": 1,
        "lessons": [
            {
                "title_ru": "Почему мошенничество работает",
                "title_uz": "Firibgarlik nega ishlaydi",
                "summary_ru": "Срочность, страх и авторитет как инструменты давления.",
                "summary_uz": "Shoshilish, qo‘rquv va obro‘ orqali bosim o‘tkazish.",
                "content_ru": (
                    "Мошенники редко начинают с технического взлома. Сначала они "
                    "пытаются управлять эмоциями: торопят, пугают блокировкой счёта "
                    "или представляются сотрудником банка. Главная защита — сделать "
                    "паузу, завершить разговор и проверить информацию самостоятельно.\n\n"
                    "Никогда не принимайте финансовое решение под давлением. "
                    "Настоящая организация позволит вам перезвонить по официальному номеру."
                ),
                "content_uz": (
                    "Firibgarlar ko‘pincha texnik buzishdan emas, hissiyotlarni "
                    "boshqarishdan boshlaydi: shoshiradi, hisob bloklanishi bilan "
                    "qo‘rqitadi yoki bank xodimi sifatida tanishtiradi.\n\n"
                    "Bosim ostida moliyaviy qaror qabul qilmang. Suhbatni tugatib, "
                    "rasmiy raqam orqali ma’lumotni tekshiring."
                ),
                "duration_minutes": 6,
                "question": {
                    "text_ru": "Что лучше всего сделать, если звонящий торопит вас?",
                    "text_uz": "Qo‘ng‘iroq qiluvchi sizni shoshirsa, nima qilish kerak?",
                    "explanation_ru": (
                        "Пауза разрушает сценарий давления. Завершите разговор и "
                        "свяжитесь с организацией самостоятельно."
                    ),
                    "explanation_uz": (
                        "Tanaffus bosim ssenariysini buzadi. Suhbatni tugatib, "
                        "tashkilot bilan o‘zingiz bog‘laning."
                    ),
                    "choices": [
                        ("Быстро выполнить инструкцию", "Ko‘rsatmani tez bajarish", False),
                        (
                            "Завершить разговор и проверить информацию",
                            "Suhbatni tugatib, ma’lumotni tekshirish",
                            True,
                        ),
                        ("Попросить ещё сильнее поторопить", "Yana tezroq gapirishni so‘rash", False),
                    ],
                },
            },
            {
                "title_ru": "SMS-коды и банковские данные",
                "title_uz": "SMS kodlar va bank ma’lumotlari",
                "summary_ru": "Какие данные нельзя сообщать даже сотруднику банка.",
                "summary_uz": "Hatto bank xodimiga ham aytib bo‘lmaydigan ma’lumotlar.",
                "content_ru": (
                    "SMS-код, PIN, CVV и пароль дают возможность подтвердить операцию "
                    "от вашего имени. Сотруднику банка эти данные не нужны. Если их "
                    "запрашивают, перед вами мошенник.\n\n"
                    "Не отправляйте скриншоты банковского приложения и не включайте "
                    "демонстрацию экрана по просьбе неизвестного человека."
                ),
                "content_uz": (
                    "SMS kodi, PIN, CVV va parol sizning nomingizdan operatsiyani "
                    "tasdiqlash imkonini beradi. Bank xodimiga bu ma’lumotlar kerak emas.\n\n"
                    "Bank ilovasi skrinshotlarini yubormang va notanish odam so‘rasa "
                    "ekran namoyishini yoqmang."
                ),
                "duration_minutes": 7,
                "question": {
                    "text_ru": "Какой код можно сообщить сотруднику банка по телефону?",
                    "text_uz": "Telefon orqali bank xodimiga qaysi kodni aytish mumkin?",
                    "explanation_ru": "Никакой одноразовый или секретный код сообщать нельзя.",
                    "explanation_uz": "Hech qanday bir martalik yoki maxfiy kodni aytish mumkin emas.",
                    "choices": [
                        ("Только SMS-код", "Faqat SMS kodi", False),
                        ("Только PIN-код", "Faqat PIN-kod", False),
                        ("Никакой", "Hech qaysi", True),
                    ],
                },
            },
            {
                "title_ru": "Опасные ссылки и приложения",
                "title_uz": "Xavfli havolalar va ilovalar",
                "summary_ru": "Фишинговые домены, APK-файлы и поддельные страницы входа.",
                "summary_uz": "Fishing domenlar, APK fayllar va soxta kirish sahifalari.",
                "content_ru": (
                    "Проверяйте точное доменное имя, а не только логотип и значок замка. "
                    "Мошеннический сайт тоже может использовать HTTPS.\n\n"
                    "Не устанавливайте APK-файлы из Telegram и сообщений. Приложения "
                    "банков загружаются только из официальных магазинов."
                ),
                "content_uz": (
                    "Faqat logotip va qulf belgisini emas, aniq domen nomini tekshiring. "
                    "Firibgar sayt ham HTTPS ishlatishi mumkin.\n\n"
                    "Telegram va xabarlardan APK fayllarni o‘rnatmang. Bank ilovalari "
                    "faqat rasmiy do‘konlardan yuklanadi."
                ),
                "duration_minutes": 8,
                "question": {
                    "text_ru": "Гарантирует ли HTTPS, что сайт принадлежит банку?",
                    "text_uz": "HTTPS sayt bankka tegishli ekanini kafolatlaydimi?",
                    "explanation_ru": (
                        "HTTPS шифрует соединение, но не подтверждает честность владельца сайта."
                    ),
                    "explanation_uz": (
                        "HTTPS ulanishni shifrlaydi, ammo sayt egasining halolligini tasdiqlamaydi."
                    ),
                    "choices": [
                        ("Да, всегда", "Ha, har doim", False),
                        ("Нет, нужно проверить точный домен", "Yo‘q, aniq domenni tekshirish kerak", True),
                        ("Только на телефоне", "Faqat telefonda", False),
                    ],
                },
            },
            {
                "title_ru": "Если вы уже стали жертвой",
                "title_uz": "Agar siz jabrlangan bo‘lsangiz",
                "summary_ru": "Первые действия для ограничения ущерба.",
                "summary_uz": "Zararni cheklash uchun birinchi harakatlar.",
                "content_ru": (
                    "Сразу заблокируйте карту через приложение или горячую линию банка. "
                    "Сообщите банку о мошенничестве, сохраните переписку, номера и чеки, "
                    "затем обратитесь в правоохранительные органы.\n\n"
                    "Если вы установили подозрительное приложение, отключите устройство "
                    "от сети и меняйте пароли с другого доверенного устройства."
                ),
                "content_uz": (
                    "Kartani bank ilovasi yoki ishonch telefoni orqali darhol bloklang. "
                    "Bankka firibgarlik haqida xabar bering, yozishmalar va cheklarni saqlang.\n\n"
                    "Shubhali ilova o‘rnatilgan bo‘lsa, qurilmani tarmoqdan uzing va "
                    "parollarni boshqa ishonchli qurilmadan almashtiring."
                ),
                "duration_minutes": 7,
                "question": {
                    "text_ru": "Какое действие должно быть первым после кражи денег с карты?",
                    "text_uz": "Kartadan pul o‘g‘irlangandan keyin birinchi harakat nima?",
                    "explanation_ru": "Сначала ограничьте дальнейший ущерб — заблокируйте карту.",
                    "explanation_uz": "Avval keyingi zararni cheklang — kartani bloklang.",
                    "choices": [
                        ("Удалить переписку", "Yozishmani o‘chirish", False),
                        ("Заблокировать карту", "Kartani bloklash", True),
                        ("Подождать один день", "Bir kun kutish", False),
                    ],
                },
            },
            {
                "title_ru": "Telegram и захват аккаунта",
                "title_uz": "Telegram va akkauntni egallash",
                "summary_ru": "Коды входа, QR-авторизация и просьбы от взломанных знакомых.",
                "summary_uz": "Kirish kodlari, QR avtorizatsiya va buzilgan tanishlar so‘rovlari.",
                "content_ru": (
                    "Мошенник может написать от имени знакомого и попросить код для "
                    "голосования, конкурса или получения подарка. На самом деле это может "
                    "быть код входа в ваш Telegram. QR-код авторизации опасен по той же причине.\n\n"
                    "Никому не сообщайте коды входа и не сканируйте чужие QR-коды. "
                    "Проверяйте активные сеансы Telegram, включите двухэтапную проверку, "
                    "а необычную просьбу знакомого подтвердите звонком."
                ),
                "content_uz": (
                    "Firibgar tanishingiz nomidan yozib, ovoz berish, tanlov yoki sovg‘a "
                    "uchun kod so‘rashi mumkin. Aslida bu Telegram akkauntingizga kirish "
                    "kodi bo‘lishi mumkin. QR avtorizatsiya ham xuddi shunday xavfli.\n\n"
                    "Kirish kodlarini bermang va begona QR kodlarni skanerlamang. Telegram "
                    "faol seanslarini tekshiring, ikki bosqichli himoyani yoqing va noodatiy "
                    "so‘rovni qo‘ng‘iroq orqali tasdiqlang."
                ),
                "duration_minutes": 8,
                "question": {
                    "text_ru": "Что делать с неожиданным QR-кодом для входа в Telegram?",
                    "text_uz": "Telegramga kirish uchun kutilmagan QR kod bilan nima qilish kerak?",
                    "explanation_ru": "Сканирование может открыть мошеннику сеанс вашего аккаунта.",
                    "explanation_uz": "Skanerlash firibgarga akkauntingiz seansini ochishi mumkin.",
                    "choices": [
                        ("Отсканировать для проверки", "Tekshirish uchun skanerlash", False),
                        ("Не сканировать и проверить активные сеансы", "Skanerlamasdan faol seanslarni tekshirish", True),
                        ("Переслать друзьям", "Do‘stlarga yuborish", False),
                    ],
                },
            },
            {
                "title_ru": "Маркетплейсы, доставка и поддельные чеки",
                "title_uz": "Marketpleys, yetkazib berish va soxta cheklar",
                "summary_ru": "Фальшивые покупатели, курьерские ссылки и изображения оплаты.",
                "summary_uz": "Soxta xaridorlar, kuryer havolalari va to‘lov rasmlari.",
                "content_ru": (
                    "Покупатель может прислать ссылку «получить деньги», попросить данные "
                    "карты или показать поддельный чек. Изображение чека не подтверждает "
                    "зачисление: проверяйте баланс только в своём банковском приложении.\n\n"
                    "Не уходите из официального чата площадки, не вводите CVV и SMS-код "
                    "для получения оплаты и не передавайте товар до реального зачисления."
                ),
                "content_uz": (
                    "Xaridor «pulni olish» havolasini yuborishi, karta ma’lumotlarini "
                    "so‘rashi yoki soxta chek ko‘rsatishi mumkin. Chek rasmi pul tushganini "
                    "tasdiqlamaydi: balansni faqat bank ilovangizda tekshiring.\n\n"
                    "Rasmiy platforma chatidan chiqmang, pul olish uchun CVV yoki SMS kodini "
                    "kiritmang va haqiqiy tushumdan oldin tovarni bermang."
                ),
                "duration_minutes": 8,
                "question": {
                    "text_ru": "Что подтверждает оплату товара?",
                    "text_uz": "Tovar to‘langanini nima tasdiqlaydi?",
                    "explanation_ru": "Только реальное зачисление в вашем банке, а не присланный чек.",
                    "explanation_uz": "Yuborilgan chek emas, faqat bankingizdagi haqiqiy tushum.",
                    "choices": [
                        ("Скриншот чека", "Chek skrinshoti", False),
                        ("Сообщение покупателя", "Xaridor xabari", False),
                        ("Зачисление в банковском приложении", "Bank ilovasidagi tushum", True),
                    ],
                },
            },
            {
                "title_ru": "Фальшивые выплаты, работа и инвестиции",
                "title_uz": "Soxta to‘lovlar, ish va investitsiyalar",
                "summary_ru": "Субсидии по ссылке, задания с депозитом и гарантированная прибыль.",
                "summary_uz": "Havoladagi subsidiya, depozitli topshiriq va kafolatlangan foyda.",
                "content_ru": (
                    "Мошенники используют темы субсидий, налоговых возвратов, штрафов и "
                    "государственных услуг, чтобы привести на поддельную форму оплаты. "
                    "Проверяйте такие сообщения на официальном портале, открытом вручную.\n\n"
                    "Другая схема — удалённая работа или инвестиции: сначала показывают "
                    "небольшую прибыль, затем требуют депозит, налог или комиссию. "
                    "Гарантированной высокой доходности без риска не существует."
                ),
                "content_uz": (
                    "Firibgarlar subsidiya, soliq qaytarish, jarima va davlat xizmatlari "
                    "mavzusidan foydalanib, soxta to‘lov shakliga olib boradi. Bunday "
                    "xabarlarni mustaqil ochilgan rasmiy portalda tekshiring.\n\n"
                    "Boshqa sxema — masofaviy ish yoki investitsiya: avval kichik foyda "
                    "ko‘rsatiladi, keyin depozit, soliq yoki komissiya so‘raladi. "
                    "Xavfsiz kafolatlangan yuqori daromad mavjud emas."
                ),
                "duration_minutes": 9,
                "question": {
                    "text_ru": "Какой признак характерен для мошеннической инвестиции?",
                    "text_uz": "Firibgar investitsiyaning odatiy belgisi qaysi?",
                    "explanation_ru": "Обещание высокой гарантированной прибыли скрывает реальный риск.",
                    "explanation_uz": "Yuqori kafolatlangan foyda va’dasi haqiqiy xavfni yashiradi.",
                    "choices": [
                        ("Гарантированная прибыль без риска", "Xavfsiz kafolatlangan foyda", True),
                        ("Описание возможных убытков", "Mumkin bo‘lgan zarar tavsifi", False),
                        ("Проверяемая лицензия", "Tekshiriladigan litsenziya", False),
                    ],
                },
            },
            {
                "title_ru": "ИИ, поддельный голос и удалённый доступ",
                "title_uz": "SI, soxta ovoz va masofaviy kirish",
                "summary_ru": "Почему знакомого голоса уже недостаточно и чем опасен AnyDesk.",
                "summary_uz": "Nega tanish ovoz yetarli emas va AnyDesk nimasi bilan xavfli.",
                "content_ru": (
                    "ИИ позволяет имитировать голос родственника или руководителя по "
                    "короткому образцу. Если вас просят срочно перевести деньги, завершите "
                    "разговор и перезвоните по сохранённому номеру. Используйте семейный "
                    "проверочный вопрос, ответ на который нельзя найти в соцсетях.\n\n"
                    "AnyDesk, TeamViewer и демонстрация экрана дают постороннему возможность "
                    "видеть коды и управлять действиями. Банку не нужен удалённый доступ "
                    "к вашему телефону."
                ),
                "content_uz": (
                    "Sun’iy intellekt qisqa namunadan qarindosh yoki rahbar ovozini taqlid "
                    "qilishi mumkin. Zudlik bilan pul so‘ralsa, suhbatni tugatib, saqlangan "
                    "raqamga qayta qo‘ng‘iroq qiling. Ijtimoiy tarmoqdan topib bo‘lmaydigan "
                    "oilaviy tekshiruv savolidan foydalaning.\n\n"
                    "AnyDesk, TeamViewer va ekran namoyishi begona shaxsga kodlarni ko‘rish "
                    "va harakatlarni boshqarish imkonini beradi. Bankka telefoningizga "
                    "masofaviy kirish kerak emas."
                ),
                "duration_minutes": 8,
                "question": {
                    "text_ru": "Как проверить срочную просьбу знакомым голосом?",
                    "text_uz": "Tanish ovozdagi shoshilinch so‘rovni qanday tekshirish kerak?",
                    "explanation_ru": "Нужен независимый канал: сохранённый номер и личный вопрос.",
                    "explanation_uz": "Mustaqil kanal kerak: saqlangan raqam va shaxsiy savol.",
                    "choices": [
                        ("Поверить голосу", "Ovozga ishonish", False),
                        ("Перезвонить по сохранённому номеру", "Saqlangan raqamga qayta qo‘ng‘iroq qilish", True),
                        ("Попросить повторить просьбу", "So‘rovni takrorlashni so‘rash", False),
                    ],
                },
            },
        ],
    }
]


class Command(BaseCommand):
    help = "Create or update the initial CyberSafe training courses."

    def handle(self, *args, **options):
        for course_data in COURSES:
            lessons = course_data["lessons"]
            defaults = {
                key: value
                for key, value in course_data.items()
                if key not in {"slug", "lessons"}
            }
            course, _ = Course.objects.update_or_create(
                slug=course_data["slug"],
                defaults={**defaults, "is_published": True},
            )
            for order, lesson_data in enumerate(lessons, start=1):
                question_data = lesson_data["question"]
                lesson_defaults = {
                    key: value for key, value in lesson_data.items() if key != "question"
                }
                lesson, _ = Lesson.objects.update_or_create(
                    course=course,
                    order=order,
                    defaults={**lesson_defaults, "is_published": True},
                )
                question, _ = LessonQuestion.objects.update_or_create(
                    lesson=lesson,
                    defaults={
                        key: value
                        for key, value in question_data.items()
                        if key != "choices"
                    },
                )
                for choice_order, (text_ru, text_uz, is_correct) in enumerate(
                    question_data["choices"],
                    start=1,
                ):
                    LessonChoice.objects.update_or_create(
                        question=question,
                        order=choice_order,
                        defaults={
                            "text_ru": text_ru,
                            "text_uz": text_uz,
                            "is_correct": is_correct,
                        },
                    )
        self.stdout.write(self.style.SUCCESS("Seeded CyberSafe courses."))
