"""
Savollarga javob topish moduli.
Tartib: FAQ → ChromaDB → Gemini 2.5 Flash
"""

import os
import re
import logging
from pathlib import Path

import chromadb
import google.generativeai as genai

from scripts.faq import FAQ

BASE_DIR = Path(__file__).resolve().parent.parent
CHROMA_DIR = BASE_DIR / "chroma_db"
COLLECTION_NAME = "documents"

# ChromaDB cosine distance chegarasi: bu qiymatdan yuqori = mos emas
DISTANCE_THRESHOLD = 0.72

# ChromaDB dan olinadigan maksimal chunk soni
TOP_K = 8

# Til/alifbo aniqlash
_UZ_CYRILLIC = set('ўқғҳЎҚҒҲ')   # O'zbek kirilli uchun xos harflar
_RU_SPECIFIC  = set('ыёэщъЫЁЭЩЪ')  # Rus tiliga xos harflar


def _detect_lang(text: str) -> str:
    """Savol tilini aniqlaydi: 'latin' | 'cyrillic_uz' | 'russian'."""
    cyrillic = sum(1 for c in text if 'Ѐ' <= c <= 'ӿ')
    if cyrillic == 0:
        return 'latin'
    uz = sum(1 for c in text if c in _UZ_CYRILLIC)
    ru = sum(1 for c in text if c in _RU_SPECIFIC)
    return 'russian' if ru > uz else 'cyrillic_uz'


_NO_ANSWER = {
    'latin': (
        "Kechirasiz, men bu savolga javob bera olmayman.\n"
        "Men Vazirlar Mahkamasining 541 hamda 1036-qarorlariga muvofiq javob beraman.\n\n"
        "Hohlasangiz operatorlar bilan bog'laning:\n"
        "📞 Tel: +998 71 203 03 04"
    ),
    'cyrillic_uz': (
        "Кечирасиз, мен бу саволга жавоб бера олмайман.\n"
        "Мен Вазирлар Маҳкамасининг 541 ва 1036-қарорларига мувофиқ жавоб бераман.\n\n"
        "Хоҳласангиз операторлар билан боғланинг:\n"
        "📞 Тел: +998 71 203 03 04"
    ),
    'russian': (
        "Извините, я не могу ответить на этот вопрос.\n"
        "Я отвечаю в соответствии с постановлениями КМ РУз №541 и №1036.\n\n"
        "Если хотите, свяжитесь с операторами:\n"
        "📞 Тел: +998 71 203 03 04"
    ),
}


def _no_answer(question: str) -> str:
    return _NO_ANSWER[_detect_lang(question)]

SYSTEM_PROMPT = """Sen "Davlat Ekologik Ekspertizasi Markazi"ning raqamli yordamchisisisan.

MARKAZ HAQIDA:
Davlat ekologik ekspertizasi markazi — O'zbekiston Respublikasi Ekologiya, atrof-muhitni muhofaza qilish va iqlim o'zgarishi vazirligi tizimida faoliyat yurituvchi davlat muassasasi. Markaz atrof-muhitga ta'sir ko'rsatadigan loyiha va hujjatlarni ekspertizadan o'tkazadi, ekologik talablarning bajarilishini nazorat qiladi.

Manzil: Toshkent sh., M.Ulug'bek tumani, Sayram 5-tor ko'chasi, 15 uy
📞 Tel: +998(71) 203-03-04
📧 Pochta: info@ecoekspertiza.uz
💬 Telegram: @eco_service_support

JAVOB BERISH QOIDALARI:
1. Berilgan kontekst asosida TO'LIQ va ANIQ javob ber. Hech narsani qisqartirma yoki o'tkazib yuborma.
2. Agar savol toifalar, turlar, bosqichlar yoki ro'yxat so'rasa — BARCHASINI sanab ber, birortasini qoldirma.
3. Savol qaysi tilda bo'lsa — javob ham o'sha tilda bo'lsin (O'zbek → O'zbekcha, Rus → Ruscha, Ingliz → Inglizcha).
4. Savol qaysi alifboda bo'lsa — javob ham O'SHA ALIFBODA bo'lsin. Lotin alifbosidagi savolga FAQAT lotin harflari bilan javob ber, hech qanday kirill harfi qo'shma.
5. Raqamlar, muddatlar, miqdorlar, nomlar — kontekstdan aynan ko'chir, taxminiy yozma.
6. Kontekstda savol uchun TO'LIQ javob bo'lmasa ham — kontekstda BOR ma'lumot asosida qisman javob ber. Faqat kontekstda HECH QANDAY bog'liq ma'lumot bo'lmagan taqdirdagina 'BILMAYMAN' so'zini yoz.
7. MARKDOWN ISHLATMA: **, *, #, ` kabi belgilar yozma — faqat oddiy matn yoz.
8. Rim raqamlari (I, II, III) o'rniga arab raqamlari ishlat: "1-toifa", "2-toifa", "3-toifa" deb yoz."""

logger = logging.getLogger(__name__)


def _setup_gemini() -> None:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY .env faylida topilmadi")
    genai.configure(api_key=api_key)


def _check_faq(question: str) -> str | None:
    """
    Savol FAQ kalit so'zlariga mos kelishini tekshiradi.
    Qisqa (<=3 harf) keywordlar uchun word boundary ishlatadi.
    """
    q_lower = question.lower()
    for item in FAQ:
        for keyword in item["questions"]:
            kw = keyword.lower()
            if len(kw) <= 3:
                if re.search(r'\b' + re.escape(kw) + r'\b', q_lower):
                    return item["answer"]
            else:
                if kw in q_lower:
                    return item["answer"]
    return None


# Rim raqamlari → arab raqami + "toifa/тоифа" (uzunroqdan qisqaga qarab)
_ROMAN_TOIFA = [
    (r'\bXIII\s+(toifa|тоифа)',  r'13-\1'),
    (r'\bXII\s+(toifa|тоифа)',   r'12-\1'),
    (r'\bXI\s+(toifa|тоифа)',    r'11-\1'),
    (r'\bX\s+(toifa|тоифа)',     r'10-\1'),
    (r'\bIX\s+(toifa|тоифа)',    r'9-\1'),
    (r'\bVIII\s+(toifa|тоифа)',  r'8-\1'),
    (r'\bVII\s+(toifa|тоифа)',   r'7-\1'),
    (r'\bVI\s+(toifa|тоифа)',    r'6-\1'),
    (r'\bV\s+(toifa|тоифа)',     r'5-\1'),
    (r'\bIV\s+(toifa|тоифа)',    r'4-\1'),
    (r'\bIII\s+(toifa|тоифа)',   r'3-\1'),
    (r'\bII\s+(toifa|тоифа)',    r'2-\1'),
    (r'\bI\s+(toifa|тоифа)',     r'1-\1'),
]


def _clean_answer(text: str) -> str:
    """LLM javobidagi markdown va rim raqamlarini tozalaydi."""
    # **bold** / *italic* / ***both*** → oddiy matn
    text = re.sub(r'\*{1,3}([^*\n]+)\*{1,3}', r'\1', text)
    # __bold__ → oddiy matn
    text = re.sub(r'_{2}([^_\n]+)_{2}', r'\1', text)
    # ## Sarlavhalar → oddiy matn
    text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)
    # `kod` → oddiy matn
    text = re.sub(r'`+([^`]*)`+', r'\1', text)
    # Rim raqamlari + toifa → arab raqami (uzunroqdan qisqaga)
    for pattern, replacement in _ROMAN_TOIFA:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text.strip()


def _embed_query(text: str) -> list[float]:
    """Savolni retrieval_query vazifasi bilan vektorlashtiradi. 429 bo'lsa qayta urinadi."""
    import time

    for wait in (10, 20, 40):
        try:
            result = genai.embed_content(
                model="models/gemini-embedding-001",
                content=text,
                task_type="retrieval_query",
            )
            return result["embedding"]
        except Exception as e:
            if "429" in str(e):
                logger.warning(f"Embedding rate limit, {wait}s kutilmoqda...")
                time.sleep(wait)
            else:
                raise
    raise RuntimeError("Embedding: barcha urinishlar tugadi")


async def get_answer(question: str) -> str:
    """
    Savolga javob qaytaradi:
    1. FAQ tekshiradi (tez yo'l)
    2. ChromaDB dan top-3 chunk qidiradi
    3. Gemini 2.5 Flash orqali javob yaratadi
    """
    _setup_gemini()

    # 1-qadam: FAQ tekshirish
    faq_answer = _check_faq(question)
    if faq_answer:
        logger.info("FAQ dan javob topildi")
        return faq_answer

    # 2-qadam: ChromaDB ga ulanish
    try:
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        collection = client.get_collection(COLLECTION_NAME)
    except Exception as e:
        logger.warning(f"ChromaDB ulanish xatosi (hujjatlar yuklanmagandir): {e}")
        return _no_answer(question)

    # 3-qadam: Vektorli qidiruv
    try:
        query_embedding = _embed_query(question)
        # Collection hajmidan oshib ketmaslik uchun n_results ni cheklaymiz
        collection_size = collection.count()
        n_results = min(TOP_K, collection_size) if collection_size > 0 else TOP_K
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["documents", "distances", "metadatas"],
        )
    except Exception as e:
        logger.error(f"ChromaDB qidiruvda xato: {e}")
        return _no_answer(question)

    docs: list[str] = results.get("documents", [[]])[0]
    distances: list[float] = results.get("distances", [[]])[0]
    metadatas: list[dict] = results.get("metadatas", [[]])[0]

    # Faqat DISTANCE_THRESHOLD dan past (yaqin) natijalarni olish, distancega qarab saralash
    filtered = [
        (doc, dist, meta)
        for doc, dist, meta in zip(docs, distances, metadatas)
        if dist < DISTANCE_THRESHOLD
    ]
    filtered.sort(key=lambda x: x[1])  # eng yaqin (kichik distance) birinchi

    logger.info(f"ChromaDB: {len(docs)} ta natija, {len(filtered)} ta mos (threshold={DISTANCE_THRESHOLD})")

    if not filtered:
        logger.info("ChromaDB dan mos kontekst topilmadi")
        return _no_answer(question)

    # Takroriy chunklarni olib tashlash (overlap natijasida bir xil boshlanuvchilar)
    seen_prefixes: set[str] = set()
    deduped: list[tuple[str, float, dict]] = []
    for doc, dist, meta in filtered:
        prefix = doc[:120]
        if prefix not in seen_prefixes:
            seen_prefixes.add(prefix)
            deduped.append((doc, dist, meta))

    # 4-qadam: Gemini ga yuborish — har bir chunkga manbasini qo'shish
    context_parts: list[str] = []
    for doc, _dist, meta in deduped:
        source = meta.get("source", "")
        header = f"[Manba: {source}]\n" if source else ""
        context_parts.append(f"{header}{doc}")
    context = "\n\n---\n\n".join(context_parts)

    # Lotin alifbosida yozilgan savol → javob ham faqat lotinda bo'lsin
    lang = _detect_lang(question)
    script_note = ""
    if lang == 'latin':
        script_note = (
            "\n\n[MAJBURIY: Bu savol o'zbek lotin alifbosida yozilgan. "
            "Javobda BIRORTA ham kirill harfi ishlatma — faqat lotin harflari.]"
        )

    prompt = f"Kontekst:\n{context}\n\nSavol: {question}{script_note}"

    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            system_instruction=SYSTEM_PROMPT,
        )
        response = model.generate_content(prompt)
        raw_answer = response.text.strip()

        # Gemini javob bera olmaganini aniqlash (o'zbek, rus, ingliz variantlari)
        _no_info_markers = (
            "bilmayman", "bilmiman",           # o'zbek lotin
            "билмайман", "билмиман",            # o'zbek kirill
            "не знаю", "не могу ответить",      # rus
            "i don't know", "i cannot answer",  # ingliz
        )
        answer_lower = raw_answer.strip().lower()
        if any(marker in answer_lower for marker in _no_info_markers):
            logger.info("Gemini kontekst asosida javob topa olmadi")
            return _no_answer(question)

        return _clean_answer(raw_answer)

    except Exception as e:
        logger.error(f"Gemini xatosi: {e}")
        return _no_answer(question)
