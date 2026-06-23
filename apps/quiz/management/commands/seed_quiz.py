from django.core.management.base import BaseCommand

from apps.quiz.models import Choice, Question

QUESTIONS = [
    {
        "category": "malware",
        "difficulty": "easy",
        "text_ru": "В Telegram прислали APK-файл «обновление банка». Что делать?",
        "text_uz": "Telegram’da «bank yangilanishi» APK fayli keldi. Nima qilish kerak?",
        "explanation_ru": "Банки не распространяют приложения через личные сообщения. Устанавливайте их только из официального магазина.",
        "explanation_uz": "Banklar ilovalarni shaxsiy xabar orqali tarqatmaydi. Faqat rasmiy do‘kondan o‘rnating.",
        "choices": [
            ("Установить и проверить", "O‘rnatib tekshirish", False),
            ("Переслать знакомому", "Tanishga yuborish", False),
            ("Удалить файл и открыть официальный магазин", "Faylni o‘chirib, rasmiy do‘konni ochish", True),
            ("Отключить антивирус и установить", "Antivirusni o‘chirib o‘rnatish", False),
        ],
    },
    {
        "category": "social_engineering",
        "difficulty": "easy",
        "text_ru": "«Сотрудник банка» просит назвать код из SMS. Ваш ответ?",
        "text_uz": "«Bank xodimi» SMS kodini aytishni so‘radi. Javobingiz?",
        "explanation_ru": "Одноразовый код подтверждает операцию от вашего имени. Настоящий сотрудник банка его не запрашивает.",
        "explanation_uz": "Bir martalik kod sizning nomingizdan amalni tasdiqlaydi. Haqiqiy bank xodimi uni so‘ramaydi.",
        "choices": [
            ("Назвать код", "Kodni aytish", False),
            ("Назвать только три цифры", "Faqat uch raqamni aytish", False),
            ("Завершить звонок и самостоятельно позвонить в банк", "Qo‘ng‘iroqni tugatib, bankka o‘zingiz qo‘ng‘iroq qilish", True),
            ("Отправить код в мессенджере", "Kodni messenjerda yuborish", False),
        ],
    },
    {
        "category": "phishing",
        "difficulty": "medium",
        "text_ru": "Как безопаснее открыть сайт банка после подозрительного SMS?",
        "text_uz": "Shubhali SMSdan keyin bank saytini qanday xavfsiz ochish mumkin?",
        "explanation_ru": "Не используйте ссылку из сообщения. Введите известный адрес вручную или откройте официальное приложение.",
        "explanation_uz": "Xabardagi havoladan foydalanmang. Ma’lum manzilni qo‘lda kiriting yoki rasmiy ilovani oching.",
        "choices": [
            ("Нажать ссылку в SMS", "SMSdagi havolani bosish", False),
            ("Ввести официальный адрес вручную", "Rasmiy manzilni qo‘lda kiritish", True),
            ("Скопировать ссылку в другой браузер", "Havolani boshqa brauzerga ko‘chirish", False),
            ("Открыть ссылку в режиме инкогнито", "Havolani inkognito rejimida ochish", False),
        ],
    },
    {
        "category": "call",
        "difficulty": "easy",
        "text_ru": "Звонящий торопит перевести деньги на «безопасный счёт». Что это означает?",
        "text_uz": "Qo‘ng‘iroq qiluvchi pulni «xavfsiz hisob»ga o‘tkazishga shoshirmoqda. Bu nimani anglatadi?",
        "explanation_ru": "«Безопасных счетов» для спасения денег не существует. Срочность и давление — признаки мошенничества.",
        "explanation_uz": "Pulni qutqarish uchun «xavfsiz hisob» mavjud emas. Shoshirish va bosim — firibgarlik belgisi.",
        "choices": [
            ("Нужно быстро перевести", "Tez o‘tkazish kerak", False),
            ("Это стандартная процедура банка", "Bu bankning odatiy tartibi", False),
            ("Нужно завершить разговор и связаться с банком", "Suhbatni tugatib, bank bilan bog‘lanish kerak", True),
            ("Можно перевести небольшую сумму", "Kichik summa o‘tkazish mumkin", False),
        ],
    },
    {
        "category": "sms",
        "difficulty": "medium",
        "text_ru": "Какой признак особенно характерен для мошеннического SMS?",
        "text_uz": "Qaysi belgi firibgar SMS uchun ayniqsa xos?",
        "explanation_ru": "Мошенники создают срочность и требуют перейти по ссылке или сообщить секретные данные.",
        "explanation_uz": "Firibgarlar shoshilinch vaziyat yaratib, havolaga o‘tish yoki maxfiy ma’lumot berishni talab qiladi.",
        "choices": [
            ("Приветствие по имени", "Ism bilan salomlashish", False),
            ("Срочная угроза блокировки и ссылка", "Shoshilinch bloklash tahdidi va havola", True),
            ("Название банка", "Bank nomi", False),
            ("Короткий текст", "Qisqa matn", False),
        ],
    },
    {
        "category": "phishing",
        "difficulty": "medium",
        "text_ru": "Что проверить в адресе сайта перед вводом пароля?",
        "text_uz": "Parol kiritishdan oldin sayt manzilida nimani tekshirish kerak?",
        "explanation_ru": "Проверяйте точное доменное имя. HTTPS само по себе не доказывает, что сайт принадлежит банку.",
        "explanation_uz": "Domen nomini aniq tekshiring. HTTPSning o‘zi sayt bankka tegishli ekanini isbotlamaydi.",
        "choices": [
            ("Только наличие красивого логотипа", "Faqat chiroyli logotip borligini", False),
            ("Точное доменное имя организации", "Tashkilotning aniq domen nomini", True),
            ("Количество картинок", "Rasmlar sonini", False),
            ("Цвет кнопки входа", "Kirish tugmasi rangini", False),
        ],
    },
    {
        "category": "social_engineering",
        "difficulty": "medium",
        "text_ru": "Знакомый неожиданно просит деньги в мессенджере. Что сделать сначала?",
        "text_uz": "Tanish messenjerda kutilmaganda pul so‘radi. Avval nima qilish kerak?",
        "explanation_ru": "Аккаунт знакомого мог быть взломан. Подтвердите просьбу по другому известному каналу связи.",
        "explanation_uz": "Tanishning akkaunti buzilgan bo‘lishi mumkin. So‘rovni boshqa ma’lum aloqa kanali orqali tasdiqlang.",
        "choices": [
            ("Сразу перевести", "Darhol o‘tkazish", False),
            ("Попросить номер карты", "Karta raqamini so‘rash", False),
            ("Позвонить знакомому по сохранённому номеру", "Tanishga saqlangan raqam orqali qo‘ng‘iroq qilish", True),
            ("Переслать сообщение другим", "Xabarni boshqalarga yuborish", False),
        ],
    },
    {
        "category": "malware",
        "difficulty": "hard",
        "text_ru": "Что делать, если вы уже установили подозрительный APK?",
        "text_uz": "Shubhali APKni o‘rnatib bo‘lgan bo‘lsangiz nima qilish kerak?",
        "explanation_ru": "Отключите устройство от сети, свяжитесь с банком с другого устройства и смените важные пароли.",
        "explanation_uz": "Qurilmani tarmoqdan uzing, boshqa qurilmadan bank bilan bog‘laning va muhim parollarni almashtiring.",
        "choices": [
            ("Ничего, если приложение открылось", "Ilova ochilgan bo‘lsa hech narsa qilmaslik", False),
            ("Отключить сеть и срочно связаться с банком", "Tarmoqni uzib, zudlik bilan bank bilan bog‘lanish", True),
            ("Перезагрузить и продолжить работу", "Qayta yuklab ishlashni davom ettirish", False),
            ("Отправить APK на проверку другу", "APKni do‘stga tekshirish uchun yuborish", False),
        ],
    },
    {
        "category": "social_engineering",
        "difficulty": "medium",
        "text_ru": "Можно ли отправлять незнакомой организации фото паспорта?",
        "text_uz": "Notanish tashkilotga pasport rasmini yuborish mumkinmi?",
        "explanation_ru": "Паспортные данные могут использовать для кредитов и захвата аккаунтов. Сначала проверьте организацию и необходимость запроса.",
        "explanation_uz": "Pasport ma’lumotlari kredit va akkauntlarni egallash uchun ishlatilishi mumkin. Avval tashkilot va so‘rov zaruratini tekshiring.",
        "choices": [
            ("Да, если обещают работу", "Ha, ish va’da qilishsa", False),
            ("Да, если общение в Telegram", "Ha, Telegramda yozishsa", False),
            ("Нет, пока организация и цель не проверены", "Yo‘q, tashkilot va maqsad tekshirilmaguncha", True),
            ("Можно закрыть только фотографию", "Faqat suratni yopish mumkin", False),
        ],
    },
    {
        "category": "phishing",
        "difficulty": "hard",
        "text_ru": "Гарантирует ли значок замка в браузере безопасность сайта?",
        "text_uz": "Brauzerdagi qulf belgisi sayt xavfsizligini kafolatlaydimi?",
        "explanation_ru": "Замок означает шифрование соединения, но мошеннический сайт тоже может иметь TLS-сертификат.",
        "explanation_uz": "Qulf ulanish shifrlanganini bildiradi, ammo firibgar sayt ham TLS sertifikatiga ega bo‘lishi mumkin.",
        "choices": [
            ("Да, всегда", "Ha, har doim", False),
            ("Нет, нужно также проверить домен и содержание", "Yo‘q, domen va mazmunni ham tekshirish kerak", True),
            ("Да, если сайт открыт на телефоне", "Ha, sayt telefonda ochilsa", False),
            ("Только в режиме инкогнито", "Faqat inkognito rejimida", False),
        ],
    },
    {
        "category": "account_takeover",
        "difficulty": "medium",
        "text_ru": "Друг просит прислать код входа в Telegram, чтобы «проголосовать». Что делать?",
        "text_uz": "Do‘stingiz «ovoz berish» uchun Telegram kirish kodini yuborishni so‘radi. Nima qilish kerak?",
        "explanation_ru": "Код входа даёт доступ к вашему аккаунту. Просьба могла прийти со взломанного аккаунта друга.",
        "explanation_uz": "Kirish kodi akkauntingizga kirish imkonini beradi. So‘rov do‘stingizning buzilgan akkauntidan kelgan bo‘lishi mumkin.",
        "choices": [
            ("Отправить код другу", "Kodni do‘stga yuborish", False),
            ("Ввести код на присланном сайте", "Kodni yuborilgan saytda kiritish", False),
            ("Не сообщать код и проверить просьбу звонком", "Kodni bermasdan, so‘rovni qo‘ng‘iroq orqali tekshirish", True),
            ("Отправить только скриншот", "Faqat skrinshot yuborish", False),
        ],
    },
    {
        "category": "marketplace",
        "difficulty": "medium",
        "text_ru": "Покупатель прислал ссылку «получить оплату за товар». Как поступить?",
        "text_uz": "Xaridor «tovar pulini olish» uchun havola yubordi. Nima qilish kerak?",
        "explanation_ru": "На маркетплейсе получение денег не требует ввода CVV, SMS-кода или перехода на сайт покупателя.",
        "explanation_uz": "Marketpleysda pul olish uchun CVV, SMS kodi yoki xaridor yuborgan saytga kirish talab qilinmaydi.",
        "choices": [
            ("Ввести данные карты", "Karta ma’lumotlarini kiritish", False),
            ("Работать только внутри официального сервиса", "Faqat rasmiy servis ichida ishlash", True),
            ("Попросить другую ссылку", "Boshqa havola so‘rash", False),
            ("Открыть ссылку в инкогнито", "Havolani inkognito rejimida ochish", False),
        ],
    },
    {
        "category": "remote_access",
        "difficulty": "hard",
        "text_ru": "«Банк» просит установить AnyDesk и показать экран телефона. Почему это опасно?",
        "text_uz": "«Bank» AnyDesk o‘rnatib, telefon ekranini ko‘rsatishni so‘radi. Bu nega xavfli?",
        "explanation_ru": "Удалённый доступ и демонстрация экрана позволяют увидеть коды и управлять операциями. Банк этого не требует.",
        "explanation_uz": "Masofaviy kirish va ekran namoyishi kodlarni ko‘rish hamda amallarni boshqarish imkonini beradi. Bank buni talab qilmaydi.",
        "choices": [
            ("Это безопасно, если звонящий знает ваше имя", "Qo‘ng‘iroq qiluvchi ismingizni bilsa xavfsiz", False),
            ("Можно дать доступ на пять минут", "Besh daqiqaga ruxsat berish mumkin", False),
            ("Нужно отказаться и связаться с банком самостоятельно", "Rad etib, bank bilan mustaqil bog‘lanish kerak", True),
            ("Достаточно скрыть баланс", "Balansni yashirish yetarli", False),
        ],
    },
    {
        "category": "investment",
        "difficulty": "medium",
        "text_ru": "В Telegram обещают гарантированно удвоить вклад за неделю. Главный признак риска?",
        "text_uz": "Telegram’da sarmoyani bir haftada kafolatli ikki baravar qilishni va’da qilishmoqda. Asosiy xavf belgisi?",
        "explanation_ru": "Гарантированная высокая доходность без риска — типичный признак инвестиционного мошенничества.",
        "explanation_uz": "Xavfsiz va kafolatlangan yuqori daromad — investitsion firibgarlikning odatiy belgisi.",
        "choices": [
            ("Обещание гарантированной прибыли", "Kafolatlangan foyda va’dasi", True),
            ("Общение вечером", "Kechqurun yozishish", False),
            ("Использование графиков", "Grafiklardan foydalanish", False),
            ("Наличие Telegram-канала", "Telegram kanali borligi", False),
        ],
    },
    {
        "category": "government_impersonation",
        "difficulty": "medium",
        "text_ru": "Пришло сообщение о субсидии со ссылкой для ввода данных карты. Что безопаснее?",
        "text_uz": "Subsidiya haqida karta ma’lumotlarini kiritish havolasi bilan xabar keldi. Xavfsiz yo‘l qaysi?",
        "explanation_ru": "Проверяйте выплаты через самостоятельно открытый официальный государственный портал, а не по ссылке из сообщения.",
        "explanation_uz": "To‘lovni xabardagi havola orqali emas, mustaqil ochilgan rasmiy davlat portali orqali tekshiring.",
        "choices": [
            ("Заполнить форму по ссылке", "Havoladagi shaklni to‘ldirish", False),
            ("Переслать сообщение родственнику", "Xabarni qarindoshga yuborish", False),
            ("Открыть официальный портал самостоятельно", "Rasmiy portalni mustaqil ochish", True),
            ("Указать карту без CVV", "CVVsiz karta raqamini kiritish", False),
        ],
    },
    {
        "category": "ai_impersonation",
        "difficulty": "hard",
        "text_ru": "Родственник звонит с незнакомого номера и знакомым голосом просит срочно деньги. Что делать?",
        "text_uz": "Qarindoshingiz notanish raqamdan tanish ovozda zudlik bilan pul so‘radi. Nima qilish kerak?",
        "explanation_ru": "Голос можно подделать с помощью ИИ. Перезвоните на сохранённый номер и задайте личный проверочный вопрос.",
        "explanation_uz": "Ovozni sun’iy intellekt bilan soxtalashtirish mumkin. Saqlangan raqamga qayta qo‘ng‘iroq qiling va shaxsiy tekshiruv savolini bering.",
        "choices": [
            ("Сразу перевести деньги", "Darhol pul o‘tkazish", False),
            ("Проверить по известному номеру и второму каналу", "Ma’lum raqam va ikkinchi kanal orqali tekshirish", True),
            ("Поверить, если голос похож", "Ovoz o‘xshasa ishonish", False),
            ("Попросить прислать номер карты", "Karta raqamini yuborishni so‘rash", False),
        ],
    },
]


class Command(BaseCommand):
    help = "Create or update the initial bilingual CyberSafe question bank."

    def handle(self, *args, **options):
        for item in QUESTIONS:
            defaults = {key: value for key, value in item.items() if key != "choices"}
            question, _ = Question.objects.update_or_create(
                text_ru=item["text_ru"],
                defaults=defaults,
            )
            for order, (text_ru, text_uz, is_correct) in enumerate(
                item["choices"],
                start=1,
            ):
                Choice.objects.update_or_create(
                    question=question,
                    order=order,
                    defaults={
                        "text_ru": text_ru,
                        "text_uz": text_uz,
                        "is_correct": is_correct,
                    },
                )
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(QUESTIONS)} questions."))
