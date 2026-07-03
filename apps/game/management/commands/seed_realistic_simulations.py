from django.core.management.base import BaseCommand

from apps.game.models import GameChoice, GameScenario, GameStep


SCENARIOS = [
    {
        "slug": "telegram-apk-delivery",
        "title_ru": "Симуляция: «Посылка» и APK-файл в Telegram",
        "title_uz": "Simulyatsiya: Telegram’da «posilka» va APK fayl",
        "description_ru": (
            "Реалистичная переписка с фальшивой доставкой: мошенник отвечает на "
            "вопросы, давит сроками и пытается убедить установить APK."
        ),
        "description_uz": (
            "Soxta yetkazib berish bo‘yicha realistik yozishma: firibgar savollarga "
            "javob beradi, vaqt bilan bosim qiladi va APK o‘rnatishga undaydi."
        ),
        "scam_type": "malware",
        "interface_type": GameScenario.InterfaceType.CHAT,
        "difficulty": GameScenario.Difficulty.MEDIUM,
        "order": 2,
        "steps": [
            {
                "message_ru": (
                    "Здравствуйте. Вам назначена доставка посылки на сегодня. "
                    "Для выбора времени установите приложение delivery.apk."
                ),
                "message_uz": (
                    "Assalomu alaykum. Bugun sizga posilka yetkaziladi. "
                    "Vaqtni tanlash uchun delivery.apk ilovasini o‘rnating."
                ),
                "tactic_ru": "Начальный контакт и файл вне официального магазина",
                "tactic_uz": "Boshlang‘ich aloqa va rasmiy do‘kondan tashqari fayl",
                "choices": [
                    (
                        "Установить APK или согласиться установить.",
                        "APKni o‘rnatish yoki o‘rnatishga rozi bo‘lish.",
                        "APK из чата может быть вредоносным. Его нельзя устанавливать.",
                        "Chatdagi APK zararli bo‘lishi mumkin. Uni o‘rnatmang.",
                        -5,
                    ),
                    (
                        "Спросить детали: откуда посылка, номер заказа, какая служба.",
                        "Tafsilotlarni so‘rash: posilka qayerdan, buyurtma raqami, qaysi xizmat.",
                        "Вопросы помогают замедлиться, но ответы мошенника всё равно нужно проверять только официально.",
                        "Savollar shoshilmaslikka yordam beradi, lekin javoblarni faqat rasmiy manbadan tekshirish kerak.",
                        4,
                    ),
                    (
                        "Не открывать файл и проверить доставку через официальный сайт/приложение.",
                        "Faylni ochmasdan yetkazib berishni rasmiy sayt/ilova orqali tekshirish.",
                        "Правильно: проверять доставку нужно только через официальный канал.",
                        "To‘g‘ri: yetkazib berishni faqat rasmiy kanal orqali tekshirish kerak.",
                        10,
                    ),
                ],
            },
            {
                "message_ru": (
                    "Посылка от интернет-магазина, в системе указан ваш номер. "
                    "Курьер уже выехал, но без приложения слот доставки не подтвердится."
                ),
                "message_uz": (
                    "Posilka internet-do‘kondan, tizimda raqamingiz ko‘rsatilgan. "
                    "Kuryer yo‘lga chiqqan, ilovasiz yetkazish vaqti tasdiqlanmaydi."
                ),
                "tactic_ru": "Правдоподобное, но непроверяемое объяснение",
                "tactic_uz": "Ishonarli, lekin tekshirilmagan izoh",
                "choices": [
                    (
                        "Поверить объяснению и продолжить установку.",
                        "Izohga ishonib o‘rnatishni davom ettirish.",
                        "Правдоподобная история не делает APK безопасным.",
                        "Ishonarli hikoya APKni xavfsiz qilmaydi.",
                        -5,
                    ),
                    (
                        "Попросить трек-номер и название официальной службы доставки.",
                        "Trek-raqam va rasmiy yetkazib berish xizmati nomini so‘rash.",
                        "Это лучше, чем устанавливать файл, но трек-номер тоже может быть выдуман.",
                        "Bu fayl o‘rnatishdan yaxshiroq, ammo trek-raqam ham soxta bo‘lishi mumkin.",
                        5,
                    ),
                    (
                        "Сказать, что проверите заказ самостоятельно в официальном приложении.",
                        "Buyurtmani rasmiy ilovada o‘zingiz tekshirishingizni aytish.",
                        "Верно: вы забираете контроль разговора у мошенника.",
                        "To‘g‘ri: suhbat nazoratini firibgardan qaytarib olasiz.",
                        10,
                    ),
                ],
            },
            {
                "message_ru": (
                    "Трек-номер сейчас не отображается из-за обновления базы. "
                    "Если не подтвердить в течение 15 минут, посылку вернут отправителю."
                ),
                "message_uz": (
                    "Baza yangilanayotgani sabab trek-raqam hozir ko‘rinmayapti. "
                    "15 daqiqada tasdiqlanmasa, posilka jo‘natuvchiga qaytariladi."
                ),
                "tactic_ru": "Срочность и снятие ответственности",
                "tactic_uz": "Shoshirish va mas’uliyatni foydalanuvchiga yuklash",
                "choices": [
                    (
                        "Поторопиться и открыть файл.",
                        "Shoshilib faylni ochish.",
                        "Искусственная срочность — частый признак мошенничества.",
                        "Sun’iy shoshirish — firibgarlikning keng tarqalgan belgisi.",
                        -5,
                    ),
                    (
                        "Ответить, что без трек-номера ничего устанавливать не будете.",
                        "Trek-raqamsiz hech narsa o‘rnatmasligingizni aytish.",
                        "Хорошее решение: не принимать риск без проверяемых данных.",
                        "Yaxshi qaror: tekshiriladigan ma’lumotsiz tavakkal qilmang.",
                        9,
                    ),
                    (
                        "Попросить прислать скриншот заказа.",
                        "Buyurtma skrinshotini so‘rash.",
                        "Скриншоты легко подделать, они не подтверждают безопасность файла.",
                        "Skrinshotlarni oson soxtalashtirish mumkin, ular fayl xavfsizligini tasdiqlamaydi.",
                        2,
                    ),
                ],
            },
            {
                "message_ru": (
                    "После установки разрешите доступ к SMS: туда придёт код доставки. "
                    "Это стандартная проверка, без неё курьер не увидит адрес."
                ),
                "message_uz": (
                    "O‘rnatgandan keyin SMSga ruxsat bering: yetkazish kodi keladi. "
                    "Bu standart tekshiruv, busiz kuryer manzilni ko‘rmaydi."
                ),
                "tactic_ru": "Опасное разрешение под видом стандартной проверки",
                "tactic_uz": "Standart tekshiruv niqobi ostida xavfli ruxsat",
                "choices": [
                    (
                        "Разрешить доступ к SMS.",
                        "SMSga kirishga ruxsat berish.",
                        "Доступ к SMS позволяет перехватывать банковские и Telegram-коды.",
                        "SMSga kirish bank va Telegram kodlarini tutib olish imkonini beradi.",
                        -5,
                    ),
                    (
                        "Спросить, зачем доставке нужен доступ к SMS.",
                        "Yetkazib berishga SMS ruxsati nega kerakligini so‘rash.",
                        "Вопрос правильный, но объяснение мошенника не делает разрешение безопасным.",
                        "Savol to‘g‘ri, lekin firibgarning izohi ruxsatni xavfsiz qilmaydi.",
                        4,
                    ),
                    (
                        "Отказаться от установки и завершить переписку.",
                        "O‘rnatishdan bosh tortib yozishmani tugatish.",
                        "Правильно: у доставки нет причины требовать доступ к SMS.",
                        "To‘g‘ri: yetkazib berish xizmatiga SMS ruxsati kerak emas.",
                        10,
                    ),
                ],
            },
            {
                "message_ru": (
                    "Вы слишком долго отвечаете. Я отмечу отказ от доставки, "
                    "повторная отправка будет платной."
                ),
                "message_uz": (
                    "Juda uzoq javob beryapsiz. Yetkazishdan voz kechdi deb belgilayman, "
                    "qayta yuborish pullik bo‘ladi."
                ),
                "tactic_ru": "Давление штрафом и потерей посылки",
                "tactic_uz": "Jarima va posilkani yo‘qotish bilan bosim",
                "choices": [
                    (
                        "Испугаться штрафа и согласиться.",
                        "Jarimadan qo‘rqib rozi bo‘lish.",
                        "Страх потери используют, чтобы заставить действовать без проверки.",
                        "Yo‘qotish qo‘rquvi tekshirmasdan harakat qildirish uchun ishlatiladi.",
                        -5,
                    ),
                    (
                        "Написать, что будете решать вопрос только через официальный сервис.",
                        "Masalani faqat rasmiy servis orqali hal qilishingizni yozish.",
                        "Отлично: вы не спорите, а переводите проверку в безопасный канал.",
                        "A’lo: bahslashmaysiz, tekshiruvni xavfsiz kanalga o‘tkazasiz.",
                        10,
                    ),
                    (
                        "Попросить номер курьера.",
                        "Kuryer raqamini so‘rash.",
                        "Номер может принадлежать сообщнику. Надёжнее — официальный канал.",
                        "Raqam sherikniki bo‘lishi mumkin. Ishonchli yo‘l — rasmiy kanal.",
                        3,
                    ),
                ],
            },
        ],
    },
    {
        "slug": "fake-bank-security-call",
        "title_ru": "Симуляция: звонок «службы безопасности банка»",
        "title_uz": "Simulyatsiya: «bank xavfsizlik xizmati» qo‘ng‘irog‘i",
        "description_ru": (
            "Длинный сценарий звонка: тревога, проверка личности, SMS-код, "
            "«безопасный счёт» и попытка изолировать пользователя."
        ),
        "description_uz": (
            "Uzun qo‘ng‘iroq ssenariysi: xavotir, shaxsni tekshirish, SMS-kod, "
            "«xavfsiz hisob» va foydalanuvchini yakkalash."
        ),
        "scam_type": "bank_call",
        "interface_type": GameScenario.InterfaceType.CALL,
        "difficulty": GameScenario.Difficulty.EASY,
        "order": 1,
        "steps": [
            {
                "message_ru": (
                    "Здравствуйте, служба безопасности банка. По вашей карте сейчас "
                    "пытаются провести перевод на 4 800 000 сум. Это вы?"
                ),
                "message_uz": (
                    "Assalomu alaykum, bank xavfsizlik xizmati. Kartangizdan hozir "
                    "4 800 000 so‘m o‘tkazishga urinish bor. Bu sizmi?"
                ),
                "tactic_ru": "Страх и авторитет банка",
                "tactic_uz": "Qo‘rquv va bank obro‘si",
                "choices": [
                    ("Паниковать и следовать инструкциям.", "Vahimaga tushib ko‘rsatmalarga amal qilish.", "Паника помогает мошеннику управлять разговором.", "Vahima firibgarga suhbatni boshqarishga yordam beradi.", -5),
                    ("Завершить звонок и самому позвонить в банк.", "Qo‘ng‘iroqni tugatib bankka o‘zingiz qo‘ng‘iroq qilish.", "Правильно: настоящий банк можно проверить по официальному номеру.", "To‘g‘ri: haqiqiy bankni rasmiy raqam orqali tekshirish mumkin.", 10),
                    ("Попросить назвать ваши данные.", "Ma’lumotlaringizni aytishni so‘rash.", "Мошенник может знать часть данных из утечек.", "Firibgar siz haqingizdagi ayrim ma’lumotlarni sizib chiqqan bazalardan bilishi mumkin.", 3),
                ],
            },
            {
                "message_ru": (
                    "Я понимаю ваши сомнения. Для идентификации назовите последние "
                    "4 цифры карты и код из SMS — это код отмены операции."
                ),
                "message_uz": (
                    "Shubhangizni tushunaman. Shaxsni aniqlash uchun kartaning oxirgi "
                    "4 raqami va SMS kodni ayting — bu operatsiyani bekor qilish kodi."
                ),
                "tactic_ru": "Подмена смысла SMS-кода",
                "tactic_uz": "SMS-kod ma’nosini almashtirish",
                "choices": [
                    ("Назвать SMS-код.", "SMS-kodni aytish.", "SMS-код нельзя сообщать никому, даже «банку».", "SMS-kodni hech kimga, hatto «bankka» ham aytmang.", -5),
                    ("Сказать, что коды не сообщаете, и завершить звонок.", "Kodlarni aytmasligingizni bildirib qo‘ng‘iroqni tugatish.", "Верно: это ключевое правило безопасности.", "To‘g‘ri: bu asosiy xavfsizlik qoidasi.", 10),
                    ("Назвать только часть кода.", "Kodning faqat bir qismini aytish.", "Даже часть кода передавать нельзя.", "Kodning bir qismini ham bermang.", 0),
                ],
            },
            {
                "message_ru": (
                    "Если не подтвердить отмену сейчас, карта заблокируется, а деньги "
                    "уйдут. Я соединю вас со старшим специалистом."
                ),
                "message_uz": (
                    "Hozir bekor qilish tasdiqlanmasa, karta bloklanadi va pul ketadi. "
                    "Sizni katta mutaxassisga ulayman."
                ),
                "tactic_ru": "Эскалация и давление должностью",
                "tactic_uz": "Lavozim bilan bosimni kuchaytirish",
                "choices": [
                    ("Ждать старшего специалиста.", "Katta mutaxassisni kutish.", "«Старший специалист» часто нужен, чтобы усилить доверие.", "«Katta mutaxassis» ko‘pincha ishonchni kuchaytirish uchun kerak.", -2),
                    ("Положить трубку.", "Telefonni qo‘yish.", "Правильно: вы прерываете сценарий давления.", "To‘g‘ri: bosim ssenariysini to‘xtatasiz.", 10),
                    ("Попросить официальный номер обращения.", "Rasmiy murojaat raqamini so‘rash.", "Это лучше паники, но звонок всё равно нужно завершить.", "Bu vahimadan yaxshiroq, lekin qo‘ng‘iroqni baribir tugatish kerak.", 5),
                ],
            },
            {
                "message_ru": (
                    "Чтобы сохранить деньги, переведите их на резервный безопасный счёт. "
                    "После проверки они вернутся автоматически."
                ),
                "message_uz": (
                    "Pulni saqlash uchun uni zaxira xavfsiz hisobga o‘tkazing. "
                    "Tekshiruvdan keyin avtomatik qaytadi."
                ),
                "tactic_ru": "Миф о безопасном счёте",
                "tactic_uz": "Xavfsiz hisob haqidagi yolg‘on",
                "choices": [
                    ("Перевести деньги.", "Pulni o‘tkazish.", "«Безопасных счетов» для спасения денег не существует.", "Pulni qutqarish uchun «xavfsiz hisob» mavjud emas.", -5),
                    ("Отказаться от любых переводов.", "Har qanday o‘tkazmadan bosh tortish.", "Правильно: банк не просит переводить деньги для защиты.", "To‘g‘ri: bank himoya uchun pul o‘tkazishni so‘ramaydi.", 10),
                    ("Перевести маленькую сумму для проверки.", "Tekshirish uchun kichik summa o‘tkazish.", "Даже маленький перевод уходит мошеннику.", "Kichik o‘tkazma ham firibgarga ketadi.", -2),
                ],
            },
            {
                "message_ru": (
                    "Никому не звоните, иначе заявка отмены сорвётся. Мы уже почти "
                    "завершили защиту счёта."
                ),
                "message_uz": (
                    "Hech kimga qo‘ng‘iroq qilmang, aks holda bekor qilish arizasi buziladi. "
                    "Hisob himoyasini deyarli tugatdik."
                ),
                "tactic_ru": "Изоляция от проверки",
                "tactic_uz": "Tekshiruvdan ajratish",
                "choices": [
                    ("Согласиться никому не звонить.", "Hech kimga qo‘ng‘iroq qilmaslikka rozi bo‘lish.", "Запрет на проверку — сильный признак мошенничества.", "Tekshiruvni taqiqlash — firibgarlikning kuchli belgisi.", -5),
                    ("Завершить звонок, заблокировать номер и проверить банк официально.", "Qo‘ng‘iroqni tugatib, raqamni bloklash va bankni rasmiy tekshirish.", "Отлично: это безопасное завершение сценария.", "A’lo: bu ssenariyni xavfsiz yakunlash.", 10),
                    ("Продолжать разговор, но ничего не говорить.", "Suhbatni davom ettirib, hech narsa aytmaslik.", "Длительный разговор повышает риск давления.", "Uzoq suhbat bosim xavfini oshiradi.", 2),
                ],
            },
        ],
    },
]


class Command(BaseCommand):
    help = "Create realistic longer scam simulation dialogs."

    def handle(self, *args, **options):
        for raw_scenario_data in SCENARIOS:
            scenario_data = dict(raw_scenario_data)
            steps = scenario_data.pop("steps")
            scenario, _ = GameScenario.objects.update_or_create(
                slug=scenario_data["slug"],
                defaults={
                    key: value
                    for key, value in scenario_data.items()
                    if key != "slug"
                }
                | {"is_published": True},
            )
            scenario.steps.filter(order__gt=len(steps)).delete()
            for step_order, raw_step_data in enumerate(steps, start=1):
                step_data = dict(raw_step_data)
                choices = step_data.pop("choices")
                step, _ = GameStep.objects.update_or_create(
                    scenario=scenario,
                    order=step_order,
                    defaults=step_data,
                )
                step.choices.filter(order__gt=len(choices)).delete()
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
        self.stdout.write(self.style.SUCCESS("Seeded realistic simulation dialogs."))
