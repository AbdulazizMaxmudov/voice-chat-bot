"""
Savollarga javob topish moduli.
Tartib: FAQ → ChromaDB → Gemini 2.5 Flash
"""

import os
import logging
from pathlib import Path

import chromadb
import google.generativeai as genai

from scripts.faq import FAQ

BASE_DIR = Path(__file__).resolve().parent.parent
CHROMA_DIR = BASE_DIR / "chroma_db"
COLLECTION_NAME = "documents"

# ChromaDB cosine distance chegarasi: bu qiymatdan yuqori = mos emas
DISTANCE_THRESHOLD = 0.75

# FAQ yoki RAG dan topilmasa qaytariladigan standart javob
NO_ANSWER = (
    "Kechirasiz, men bu savolga javob bera olmayman. "
    "Iltimos, operatorlar bilan bog'laning:\n"
    "📞 Tel: +998(71) 203-03-04\n"
    "📧 Pochta: info@ecoekspertiza.uz\n"
    "💬 Telegram: @eco_service_support"
)

SYSTEM_PROMPT = """Sen "Davlat Ekologik Ekspertizasi Markazi"ning raqamli yordamchisisisan.

MARKAZ HAQIDA:
Davlat ekologik ekspertizasi markazi — O'zbekiston Respublikasi Ekologiya, atrof-muhitni muhofaza qilish va iqlim o'zgarishi vazirligi tizimida faoliyat yurituvchi davlat muassasasi. Markaz atrof-muhitga ta'sir ko'rsatadigan loyiha va hujjatlarni ekspertizadan o'tkazadi, ekologik talablarning bajarilishini nazorat qiladi.

Manzil: Toshkent sh., M.Ulug'bek tumani, Sayram 5-tor ko'chasi, 15 uy
📞 Tel: +998(71) 203-03-04
📧 Pochta: info@ecoekspertiza.uz
💬 Telegram: @eco_service_support

JAVOB BERISH QOIDALARI:
1. Berilgan kontekst asosida TO'LIQ va ANIQ javob ber. Hech narsani qisqartirma yoki o'tkazib yubOrma.
2. Agar savol toifalar, turlar, bosqichlar yoki ro'yxat so'rasa — BARCHASINI sanab ber, birortasini qoldirma.
3. Savol qaysi tilda bo'lsa — javob ham o'sha tilda bo'lsin (O'zbek → O'zbekcha, Rus → Ruscha, Ingliz → Inglizcha).
4. Raqamlar, muddatlar, miqdorlar, nomlar — aniq ko'rsat, taxminiy yozma.
5. Agar kontekstda savol uchun yetarli ma'lumot bo'lmasa — faqat 'BILMAYMAN' so'zini yoz. Boshqa hech narsa yozma."""

logger = logging.getLogger(__name__)


def _setup_gemini() -> None:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY .env faylida topilmadi")
    genai.configure(api_key=api_key)


def _check_faq(question: str) -> str | None:
    """
    Savol FAQ kalit so'zlariga mos kelishini tekshiradi.
    Kichik harfga o'tkazib taqqoslaydi.
    """
    q_lower = question.lower()
    for item in FAQ:
        for keyword in item["questions"]:
            if keyword.lower() in q_lower:
                return item["answer"]
    return None


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
        return NO_ANSWER

    # 3-qadam: Vektorli qidiruv
    try:
        query_embedding = _embed_query(question)
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=5,
            include=["documents", "distances"],
        )
    except Exception as e:
        logger.error(f"ChromaDB qidiruvda xato: {e}")
        return NO_ANSWER

    docs: list[str] = results.get("documents", [[]])[0]
    distances: list[float] = results.get("distances", [[]])[0]

    # Faqat DISTANCE_THRESHOLD dan past (yaqin) natijalarni olish
    relevant_docs = [
        doc for doc, dist in zip(docs, distances) if dist < DISTANCE_THRESHOLD
    ]

    if not relevant_docs:
        logger.info("ChromaDB dan mos kontekst topilmadi")
        return NO_ANSWER

    # 4-qadam: Gemini ga yuborish
    context = "\n\n---\n\n".join(relevant_docs)
    prompt = f"Kontekst:\n{context}\n\nSavol: {question}"

    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=SYSTEM_PROMPT,
        )
        response = model.generate_content(prompt)
        answer = response.text.strip()

        # Gemini javob bera olmaganini aniqlash
        if answer.strip().upper() == "BILMAYMAN":
            logger.info("Gemini kontekst asosida javob topa olmadi")
            return NO_ANSWER

        return answer

    except Exception as e:
        logger.error(f"Gemini xatosi: {e}")
        return NO_ANSWER
