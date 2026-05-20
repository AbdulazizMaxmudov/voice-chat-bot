# Tez-tez so'raladigan savollar (FAQ) ro'yxati.
# Tartib muhim: yuqoriroq entry birinchi tekshiriladi.
# Qoida: aniq/xususiy entrylar → umumiy entrylar.
# Matching: keyword savolning ichida substring sifatida qidiriladi (kichik harfga o'tkazib).
#
# MUHIM: "adres" keyword ishlatmang — "address" so'ziga ham mos keladi (substring bug).
# Individual filial entrylari FILIALLAR umumiy entrydan OLDIN turishi shart.
# Toshkent VILOYATI Toshkent SHAHAR dan OLDIN turishi shart.

FAQ = [

    # ── Bot haqida — O'zbek ────────────────────────────────────────────────────
    {
        "questions": [
            "bot haqida", "siz kimsiz", "bu nima", "kim siz", "nima qilasiz",
            "nimalar qilasiz", "nimalar qila", "nima qila ol",
            "yordamchi haqida", "qanday ishlatiladi",
            "ishlatish", "nimaga kerak", "maqsad",
        ],
        "answer": (
            "Men Davlat Ekologik Ekspertizasi Markazining raqamli yordamchisiman.\n\n"
            "Quyidagi savollarga javob bera olaman:\n"
            "- Markaz faoliyati va xizmatlari\n"
            "- Ekologik ekspertiza tartiblari va talablari\n"
            "- Filiallar, manzillar va telefon raqamlar\n"
            "- Hujjatlar, muddatlar va boshqa ma'lumotlar\n\n"
            "Ovozli yoki matnli savol berishingiz mumkin."
        ),
    },

    # ── Bot haqida — Rus ──────────────────────────────────────────────────────
    {
        "questions": [
            "кто вы", "что это", "что вы делаете", "о боте",
            "помощник", "как пользоваться", "чем можете помочь",
            "что умеете", "умеете делать", "зачем нужен", "что такое",
            "что вы умеете", "чем вы можете",
        ],
        "answer": (
            "Я цифровой ассистент Государственного центра экологической экспертизы.\n\n"
            "Могу ответить на вопросы о:\n"
            "- деятельности и услугах центра\n"
            "- порядке проведения экологической экспертизы\n"
            "- филиалах, адресах и контактах\n"
            "- документах и сроках\n\n"
            "Вы можете задавать вопросы голосом или текстом."
        ),
    },

    # ── Bot haqida — Ingliz ───────────────────────────────────────────────────
    {
        "questions": [
            "who are you", "what is this", "what can you do",
            "about bot", "how to use", "what do you do",
            "what are you", "your purpose", "help me understand",
        ],
        "answer": (
            "I am the digital assistant of the State Center for Environmental Expertise of Uzbekistan.\n\n"
            "I can answer questions about:\n"
            "- Center's activities and services\n"
            "- Environmental expertise procedures and requirements\n"
            "- Branches, addresses and contact information\n"
            "- Documents and deadlines\n\n"
            "You can ask questions by voice or text."
        ),
    },

    # ── Ma'lumot manbai ───────────────────────────────────────────────────────
    {
        "questions": [
            # O'zbek
            "ma'lumot qayerdan", "ma'lumotlarni qayerdan", "qayerdan olasan",
            "qayerdan olding", "qayerdan bilasan", "manba nima", "ma'lumot manbai",
            # Rus / kirill
            "откуда информацию", "откуда берёшь", "откуда данные", "источник данных",
            # Ingliz
            "where do you get", "data source", "information source",
        ],
        "answer": (
            "Men ma'lumotlarni O'zbekiston Respublikasi Vazirlar Mahkamasining "
            "541-sonli va 1036-sonli qarorlaridan olaman.\n\n"
            "Bu qarorlar Davlat ekologik ekspertizasining qoidalari, tartiblari "
            "va talablarini to'liq belgilaydi."
        ),
    },

    # ── Salomlashish ───────────────────────────────────────────────────────────
    {
        "questions": [
            "salom", "assalom", "assalomu alaykum", "salomlar",
            "привет", "здравствуйте", "здравствуй", "добрый день",
            "добрый утро", "добрый вечер", "доброе утро", "доброе",
            "hello", "hey", "good morning", "good afternoon", "good evening",
        ],
        "answer": (
            "Assalomu alaykum! Davlat Ekologik Ekspertizasi Markazining raqamli yordamchisiga xush kelibsiz.\n\n"
            "Filiallar, manzillar, telefon raqamlar yoki markaz xizmatlari haqida savol bersangiz, javob beraman."
        ),
    },

    # ── Xayrlashuv ─────────────────────────────────────────────────────────────
    {
        "questions": [
            "rahmat", "xayr", "sog' bo'l", "bye", "ko'rishguncha",
            "спасибо", "пока", "до свидания", "благодарю",
        ],
        "answer": "Xizmatdan mamnun bo'ldingiz! Yana murojaat qiling.",
    },

    # ══════════════════════════════════════════════════════════════════════════
    # FILIALLAR — individual
    # Har bir entry: o'zbek lotin + o'zbek kirill + rus + INGLIZ nomlari
    # Toshkent viloyati Toshkent shahar DAN OLDIN turishi shart.
    # ══════════════════════════════════════════════════════════════════════════

    {
        "questions": [
            # O'zbek (lotin + kirill)
            "qoraqalpog'iston", "qoraqalpogiston", "qoraqalpog",
            "nukus", "нукус", "қорақалпоғистон",
            # Rus
            "каракалпакстан", "каракалпак",
            # Ingliz
            "karakalpakstan", "karakalpak republic",
        ],
        "answer": (
            "Qoraqalpog'iston Respublikasi filiali:\n"
            "Manzil: Qoraqalpog'iston Respublikasi, Nukus shahri, Tong-nuri ko'chasi.\n"
            "Direktor: Jollibekov Murat Baxtiyarovich\n"
            "Telefon: +998 61 224 06 69\n"
            "Qabul vaqti: Dushanba 10:00 dan 12:00 gacha."
        ),
    },

    {
        "questions": [
            # O'zbek (lotin + kirill)
            "andijon", "андижон",
            # Rus
            "андижан",
            # Ingliz
            "andijan",
        ],
        "answer": (
            "Andijon viloyati filiali:\n"
            "Manzil: Andijon viloyati, Andijon shahri, Kunchilik ko'chasi, 75-uy.\n"
            "Direktor: Mamanazarov Abdumannob Abduraxmonovich\n"
            "Telefon: +998 74 237 07 00\n"
            "Qabul vaqti: Dushanba 10:00 dan 12:00 gacha."
        ),
    },

    {
        "questions": [
            # O'zbek (lotin + kirill)
            "buxoro", "бухоро",
            # Rus
            "бухара",
            # Ingliz
            "bukhara", "bukhoro",
        ],
        "answer": (
            "Buxoro viloyati filiali:\n"
            "Manzil: Buxoro viloyati, Buxoro shahri, Ibn Sino ko'chasi, 206-uy.\n"
            "Direktor: Ruziyev Erkin Xolboyevich\n"
            "Telefon: +998 55 304 07 42\n"
            "Qabul vaqti: Dushanba 10:00 dan 12:00 gacha."
        ),
    },

    {
        "questions": [
            # O'zbek (lotin + kirill)
            "jizzax", "жиззах",
            # Rus
            "джизак",
            # Ingliz
            "jizzakh", "jizzak",
        ],
        "answer": (
            "Jizzax viloyati filiali:\n"
            "Manzil: Jizzax viloyati, Jizzax shahri, Bog'ishamol MFY, Tog'ishamol ko'chasi, 5-uy.\n"
            "Direktor: Aglamov Ziyoviddin Maxmudovich\n"
            "Telefon: +998 55 151 57 20\n"
            "Qabul vaqti: Dushanba 10:00 dan 12:00 gacha."
        ),
    },

    {
        "questions": [
            # O'zbek (lotin + kirill)
            "qashqadaryo", "qarshi", "қашқадарё", "қарши",
            # Rus
            "кашкадарья", "карши",
            # Ingliz
            "kashkadarya", "kashkadaria", "karshi",
        ],
        "answer": (
            "Qashqadaryo viloyati filiali:\n"
            "Manzil: Qashqadaryo viloyati, Qarshi shahri, Jayxun ko'chasi, 5-uy.\n"
            "Direktor: Berdiyev Jaxongir Kamolovich\n"
            "Telefon: +998 75 221 00 68\n"
            "Qabul vaqti: Dushanba 10:00 dan 12:00 gacha."
        ),
    },

    {
        "questions": [
            # O'zbek (lotin + kirill)
            "navoiy", "навоий",
            # Rus
            "навои",
            # Ingliz
            "navoi", "navoiy city",
        ],
        "answer": (
            "Navoiy viloyati filiali:\n"
            "Manzil: Navoiy shahri, S. Ayniy ko'chasi, 27-uy.\n"
            "Direktor: Botirov Usmon Istamovich\n"
            "Telefon: +998 55 351 08 40\n"
            "Qabul vaqti: Dushanba 10:00 dan 12:00 gacha."
        ),
    },

    {
        "questions": [
            # O'zbek / Rus / Ingliz — barchasi bir xil yoziladi
            "namangan", "наманган",
        ],
        "answer": (
            "Namangan viloyati filiali:\n"
            "Manzil: Namangan viloyati, Namangan shahri, Xiva ko'chasi, 1-uy.\n"
            "Direktor: Xaydarov Akmal Sotvoldievich\n"
            "Telefon: +998 69 233 19 33\n"
            "Qabul vaqti: Dushanba 10:00 dan 12:00 gacha."
        ),
    },

    {
        "questions": [
            # O'zbek (lotin + kirill)
            "samarqand", "самарқанд",
            # Rus
            "самарканд",
            # Ingliz
            "samarkand", "samarqand city",
        ],
        "answer": (
            "Samarqand viloyati filiali:\n"
            "Manzil: Samarqand viloyati, Samarqand shahri, Gagarin ko'chasi, 27-uy.\n"
            "Direktor: Po'lotov Jaxongir Farxod o'g'li\n"
            "Telefon: +998 55 706 98 28\n"
            "Qabul vaqti: Dushanba 10:00 dan 12:00 gacha."
        ),
    },

    {
        "questions": [
            # O'zbek (lotin + kirill)
            "surxondaryo", "termiz", "сурхондарё", "термиз",
            # Rus
            "сурхандарья", "термез",
            # Ingliz
            "surkhandarya", "surkhondarya", "termez",
        ],
        "answer": (
            "Surxondaryo viloyati filiali:\n"
            "Manzil: Surxondaryo viloyati, Termiz shahri, Amir Temur ko'chasi, 69-uy.\n"
            "Direktor: Baxshikulov Abdukodir Majidovich\n"
            "Telefon: +998 76 221 47 75\n"
            "Qabul vaqti: Dushanba 10:00 dan 12:00 gacha."
        ),
    },

    {
        "questions": [
            # O'zbek (lotin + kirill)
            "sirdaryo", "guliston", "сирдарё", "гулистон",
            # Rus
            "сырдарья", "гулистан",
            # Ingliz
            "syrdarya", "sirdarya", "gulistan",
        ],
        "answer": (
            "Sirdaryo viloyati filiali:\n"
            "Manzil: Sirdaryo viloyati, Guliston shahri, Birlashgan ko'chasi, 10-uy.\n"
            "Direktor: Qorayev Elmurod Saydaxmatovich\n"
            "Telefon: +998 67 225 06 39\n"
            "Qabul vaqti: Dushanba 10:00 dan 12:00 gacha."
        ),
    },

    {
        "questions": [
            # O'zbek (lotin + kirill)
            "farg'ona", "fargona", "фарғона",
            # Rus
            "фергана",
            # Ingliz
            "fergana", "farghona",
        ],
        "answer": (
            "Farg'ona viloyati filiali:\n"
            "Manzil: Farg'ona viloyati, Farg'ona shahri, Ibrat MFY, B. Marg'iloniy ko'chasi, 119-uy.\n"
            "Direktor: Babaxodjaev Maxamatmuso Yakubovich\n"
            "Telefon: +998 73 244 64 94\n"
            "Qabul vaqti: Dushanba 10:00 dan 12:00 gacha."
        ),
    },

    # Toshkent VILOYATI — aniq keywordlar, shahar entrydan OLDIN
    {
        "questions": [
            # O'zbek
            "toshkent viloyati", "toshvil", "nurafshon",
            # Rus / kirill
            "тошкент вилояти", "нурафшон", "ташкентская область",
            # Ingliz — "tashkent region/oblast" shahar "tashkent" dan oldin ushlaydi
            "tashkent region", "tashkent oblast", "tashkent province",
        ],
        "answer": (
            "Toshkent viloyati filiali:\n"
            "Manzil: Nurafshon shahri, Birlik MFY, Toshkent yo'li ko'chasi, 32-uy.\n"
            "Direktor: Xolmurodov Abdumajid Abduraimovich\n"
            "Telefon: +998 71 225 06 39\n"
            "Qabul vaqti: Dushanba 10:00 dan 12:00 gacha."
        ),
    },

    {
        "questions": [
            # O'zbek (lotin + kirill)
            "xorazm", "urganch", "хоразм", "урганч",
            # Rus
            "хорезм", "ургенч",
            # Ingliz
            "khorezm", "khwarazm", "urgench",
        ],
        "answer": (
            "Xorazm viloyati filiali:\n"
            "Manzil: Xorazm viloyati, Urganch shahri, Yoshlik ko'chasi, 61-uy.\n"
            "Direktor: Xayitov Jonibek Xayitboyevich\n"
            "Telefon: +998 95 620 10 42\n"
            "Qabul vaqti: Dushanba 10:00 dan 12:00 gacha."
        ),
    },

    # Toshkent SHAHAR — bare "toshkent"/"tashkent" viloyat entrydan KEYIN
    {
        "questions": [
            # O'zbek
            "toshkent shahar", "toshkent sh", "toshsh",
            # Kirill
            "тошкент шаҳар", "тошкент", "ташкент",
            # Ingliz — bare "tashkent" shahar entryda, viloyat "tashkent region" deb ushlangan
            "tashkent city", "tashkent", "toshkent",
        ],
        "answer": (
            "Toshkent shahar filiali:\n"
            "Manzil: Toshkent shahri, Mirzo Ulug'bek tumani, Sayram ko'chasi, 15-uy.\n"
            "Direktor: Muminov Shaxboz Baxodirovich\n"
            "Telefon: +998 71 203 01 03\n"
            "Qabul vaqti: Dushanba 10:00 dan 12:00 gacha."
        ),
    },

    # ── Barcha filiallar ro'yxati (umumiy) ────────────────────────────────────
    {
        "questions": [
            # O'zbek
            "filiallar", "barcha filiallar", "hamma filiallar",
            "filial ro'yxati", "qaysi viloyat", "viloyatlar",
            "nechta filiali", "filiali bor", "nechta filial",
            # Rus / kirill
            "филиаллар", "все филиалы", "список филиалов",
            "какие филиалы", "сколько филиалов", "где есть филиал",
            # Ingliz
            "branch list", "all branches", "how many branch",
            "list of branch", "which region", "all offices",
        ],
        "answer": (
            "Ekoekspertiza filiallari ro'yxati (14 ta):\n\n"
            "1.  Qoraqalpog'iston — +998 61 224 06 69\n"
            "2.  Andijon — +998 74 237 07 00\n"
            "3.  Buxoro — +998 55 304 07 42\n"
            "4.  Jizzax — +998 55 151 57 20\n"
            "5.  Qashqadaryo (Qarshi) — +998 75 221 00 68\n"
            "6.  Navoiy — +998 55 351 08 40\n"
            "7.  Namangan — +998 69 233 19 33\n"
            "8.  Samarqand — +998 55 706 98 28\n"
            "9.  Surxondaryo (Termiz) — +998 76 221 47 75\n"
            "10. Sirdaryo (Guliston) — +998 67 225 06 39\n"
            "11. Farg'ona — +998 73 244 64 94\n"
            "12. Toshkent viloyati (Nurafshon) — +998 71 225 06 39\n"
            "13. Xorazm (Urganch) — +998 95 620 10 42\n"
            "14. Toshkent shahar — +998 71 203 01 03\n\n"
            "Qabul vaqti (barchasi): Dushanba 10:00 dan 12:00 gacha.\n"
            "Aniq viloyat nomini yozsangiz, batafsil ma'lumot beraman."
        ),
    },

    # ══════════════════════════════════════════════════════════════════════════
    # MARKAZ UMUMIY MA'LUMOTLARI
    # ══════════════════════════════════════════════════════════════════════════

    {
        "questions": [
            # O'zbek
            "telefon", "raqam", "kontakt", "bog'lanish",
            # Rus / kirill
            "телефон", "номер", "контакт", "связь",
            # Ingliz
            "phone", "contact", "call",
        ],
        "answer": (
            "Markaz telefoni: +998 71 203 03 04\n"
            "Telegram: @eco_service_support\n"
            "Manzil: Toshkent shahar, Mirzo-Ulug'bek tumani, Sayram 5-tor ko'chasi, 15-uy."
        ),
    },

    {
        "questions": [
            # O'zbek — "qayerda" YO'Q: "qayerdan" ga substring mos keladi (bug)
            "manzil", "qayerda joylash", "qayerda bor", "joylashuv",
            # Rus / kirill  — "adres" YO'Q: "address" ga substring mos keladi
            "адрес", "находится", "где находится", "расположен",
            # Ingliz
            "address", "location", "where is",
        ],
        "answer": (
            "Markaz manzili:\n"
            "Toshkent shahar, Mirzo-Ulug'bek tumani,\n"
            "Sayram 5-tor ko'chasi, 15-uy."
        ),
    },

    {
        "questions": [
            # O'zbek
            "ish vaqti", "ish kunlari", "qachon ishlaydi", "soat nechi",
            # Rus / kirill
            "часы работы", "время работы", "режим работы", "когда работает",
            # Ingliz
            "working hours", "opening hours", "work schedule",
        ],
        "answer": "Ish vaqti: Dushanba dan Jumagacha, soat 09:00 dan 18:00 gacha. Filiallar qabul vaqti: Dushanba soat 10:00 dan 12:00 gacha.",
    },
]
