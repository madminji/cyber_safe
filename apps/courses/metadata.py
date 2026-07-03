from .models import Course


COURSE_METADATA = {
    "cybersafe-basic": {
        "title_ru": "CyberSafe Basic: \u0431\u0430\u0437\u043e\u0432\u0430\u044f \u0446\u0438\u0444\u0440\u043e\u0432\u0430\u044f \u0431\u0435\u0437\u043e\u043f\u0430\u0441\u043d\u043e\u0441\u0442\u044c",
        "title_uz": "CyberSafe Basic: asosiy raqamli xavfsizlik",
        "description_ru": (
            "\u041f\u0435\u0440\u0432\u044b\u0439 \u0443\u0440\u043e\u0432\u0435\u043d\u044c \u0434\u043b\u044f \u0435\u0436\u0435\u0434\u043d\u0435\u0432\u043d\u043e\u0439 \u0437\u0430\u0449\u0438\u0442\u044b: "
            "\u043b\u0438\u0447\u043d\u044b\u0435 \u0434\u0430\u043d\u043d\u044b\u0435, \u0444\u0438\u0448\u0438\u043d\u0433\u043e\u0432\u044b\u0435 \u0441\u0441\u044b\u043b\u043a\u0438, "
            "\u0437\u0432\u043e\u043d\u043a\u0438 \u0438\u0437 \u0431\u0430\u043d\u043a\u0430, SMS-\u043a\u043e\u0434\u044b, APK-\u0444\u0430\u0439\u043b\u044b "
            "\u0438 \u0431\u0430\u0437\u043e\u0432\u044b\u0435 \u043d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438 \u0442\u0435\u043b\u0435\u0444\u043e\u043d\u0430."
        ),
        "description_uz": (
            "Kundalik himoya uchun birinchi bosqich: shaxsiy ma\u2019lumotlar, "
            "fishing havolalari, bank nomidan qo\u2018ng\u2018iroqlar, SMS-kodlar, "
            "APK fayllar va telefonning asosiy xavfsizlik sozlamalari."
        ),
        "level": Course.Level.BASIC,
        "orders": range(1, 9),
        "order": 1,
    },
    "cybersafe-advanced": {
        "title_ru": "CyberSafe Advanced: \u0440\u0435\u0430\u043b\u044c\u043d\u044b\u0435 \u0441\u0445\u0435\u043c\u044b \u043c\u043e\u0448\u0435\u043d\u043d\u0438\u0447\u0435\u0441\u0442\u0432\u0430",
        "title_uz": "CyberSafe Advanced: real firibgarlik sxemalari",
        "description_ru": (
            "\u0412\u0442\u043e\u0440\u043e\u0439 \u0443\u0440\u043e\u0432\u0435\u043d\u044c \u043f\u0440\u043e \u0431\u043e\u043b\u0435\u0435 \u0441\u043b\u043e\u0436\u043d\u044b\u0435 "
            "\u0441\u0446\u0435\u043d\u0430\u0440\u0438\u0438: \u043f\u043e\u043a\u0443\u043f\u043a\u0438 \u043e\u043d\u043b\u0430\u0439\u043d, "
            "\u043f\u043e\u0434\u0434\u0435\u043b\u044c\u043d\u044b\u0435 \u043f\u043e\u043a\u0443\u043f\u0430\u0442\u0435\u043b\u0438, "
            "\u0444\u0435\u0439\u043a\u043e\u0432\u044b\u0435 \u0432\u044b\u043f\u043b\u0430\u0442\u044b, \u043e\u043d\u043b\u0430\u0439\u043d-\u0437\u0430\u0439\u043c\u044b, "
            "\u043f\u0438\u0440\u0430\u043c\u0438\u0434\u044b, \u043a\u0440\u0438\u043f\u0442\u043e-\u0441\u0445\u0435\u043c\u044b, \u043f\u0430\u0440\u043e\u043b\u0438 "
            "\u0438 \u0434\u0432\u0443\u0445\u0444\u0430\u043a\u0442\u043e\u0440\u043d\u0430\u044f \u0437\u0430\u0449\u0438\u0442\u0430."
        ),
        "description_uz": (
            "Murakkabroq holatlar bo\u2018yicha ikkinchi bosqich: onlayn xaridlar, "
            "soxta xaridorlar, yolg\u2018on to\u2018lovlar, onlayn qarzlar, piramidalar, "
            "kripto-sxemalar, parollar va ikki bosqichli himoya."
        ),
        "level": Course.Level.ADVANCED,
        "orders": range(9, 17),
        "order": 2,
    },
    "cybersafe-expert": {
        "title_ru": "CyberSafe Expert: \u0438\u043d\u0441\u0442\u0440\u0443\u043c\u0435\u043d\u0442\u044b, \u0438\u043d\u0446\u0438\u0434\u0435\u043d\u0442\u044b \u0438 \u043b\u0438\u0447\u043d\u044b\u0439 \u043f\u043b\u0430\u043d",
        "title_uz": "CyberSafe Expert: vositalar, hodisalar va shaxsiy reja",
        "description_ru": (
            "\u0424\u0438\u043d\u0430\u043b\u044c\u043d\u044b\u0439 \u0443\u0440\u043e\u0432\u0435\u043d\u044c: \u0440\u0430\u0431\u043e\u0442\u0430 \u0441 "
            "\u0430\u043d\u0430\u043b\u0438\u0437\u0430\u0442\u043e\u0440\u043e\u043c, \u043f\u0440\u043e\u0432\u0435\u0440\u043a\u0430 \u043d\u043e\u043c\u0435\u0440\u0430, "
            "\u0440\u0435\u043f\u043e\u0440\u0442\u044b, \u0434\u0435\u0439\u0441\u0442\u0432\u0438\u044f \u043f\u043e\u0441\u043b\u0435 "
            "\u0438\u043d\u0446\u0438\u0434\u0435\u043d\u0442\u0430 \u0438 \u043b\u0438\u0447\u043d\u044b\u0439 \u043f\u043b\u0430\u043d "
            "\u043a\u0438\u0431\u0435\u0440\u0431\u0435\u0437\u043e\u043f\u0430\u0441\u043d\u043e\u0441\u0442\u0438."
        ),
        "description_uz": (
            "Yakuniy bosqich: analizator bilan ishlash, raqamni tekshirish, "
            "xabar yuborish, hodisadan keyingi harakatlar va shaxsiy "
            "kiberxavfsizlik rejasi."
        ),
        "level": Course.Level.EXPERT,
        "orders": range(17, 21),
        "order": 3,
    },
}


COURSE_LEVELS = tuple(
    {"slug": slug, **metadata} for slug, metadata in COURSE_METADATA.items()
)
