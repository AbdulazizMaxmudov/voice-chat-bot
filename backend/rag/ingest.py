import logging
import os
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from llama_index.core import Document, Settings, StorageContext, VectorStoreIndex
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.readers.file import DocxReader, PDFReader
from llama_index.vector_stores.chroma import ChromaVectorStore
from rag.embedding import GeminiEmbedding

load_dotenv()

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.parent
DOCS_DIR = BASE_DIR / "documents"
CHROMA_DIR = str(BASE_DIR / "chroma_db")
COLLECTION_NAME = "rag_documents"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

SUPPORTED_EXTENSIONS = {".docx", ".pdf", ".txt", ".md"}


def _setup_embedding() -> None:
    Settings.embed_model = GeminiEmbedding(api_key=GEMINI_API_KEY)
    Settings.llm = None


def _load_file(file_path: Path) -> list[Document]:
    """Fayl kengaytmasiga qarab mos reader bilan yuklaydi."""
    ext = file_path.suffix.lower()

    if ext == ".docx":
        docs = DocxReader().load_data(file=file_path)
    elif ext == ".pdf":
        docs = PDFReader().load_data(file=file_path)
    elif ext in {".txt", ".md"}:
        text = file_path.read_text(encoding="utf-8", errors="replace")
        docs = [Document(text=text)]
    else:
        raise ValueError(f"Qo'llab-quvvatlanmaydigan format: {ext}")

    for doc in docs:
        doc.metadata["source"] = file_path.name
    return docs


def ingest_documents() -> dict:
    """
    /backend/documents/ papkasidagi hujjatlarni (.docx, .pdf, .txt, .md):
      1. O'qiydi
      2. 512 token / 50 overlap bo'laklarga ajratadi
      3. Collection ni tozalab, Gemini embedding bilan ChromaDB ga saqlaydi

    Returns:
        dict: {total_chunks, processed_files, failed_files, total_documents}
    """
    if not DOCS_DIR.exists():
        DOCS_DIR.mkdir(parents=True)
        raise FileNotFoundError(
            f"Hujjatlar papkasi yaratildi, lekin bo'sh: {DOCS_DIR}. "
            "Iltimos, hujjatlarni joylashtiring."
        )

    doc_files = [f for f in DOCS_DIR.iterdir() if f.suffix.lower() in SUPPORTED_EXTENSIONS]
    if not doc_files:
        raise ValueError(
            f"Hech qanday hujjat topilmadi: {DOCS_DIR}. "
            f"Qabul qilinadigan formatlar: {SUPPORTED_EXTENSIONS}"
        )

    logger.info(f"{len(doc_files)} ta hujjat topildi")

    _setup_embedding()

    all_documents: list[Document] = []
    processed: list[str] = []
    failed: list[dict] = []

    for file_path in doc_files:
        try:
            docs = _load_file(file_path)
            all_documents.extend(docs)
            processed.append(file_path.name)
            logger.info(f"O'qildi: {file_path.name} ({len(docs)} segment)")
        except Exception as e:
            failed.append({"file": file_path.name, "error": str(e)})
            logger.error(f"O'qishda xato [{file_path.name}]: {e}")

    if not all_documents:
        raise RuntimeError("Hech qanday hujjat muvaffaqiyatli o'qilmadi")

    splitter = TokenTextSplitter(chunk_size=512, chunk_overlap=50)
    nodes = splitter.get_nodes_from_documents(all_documents)
    logger.info(f"{len(nodes)} ta chunk yaratildi")

    # Eski ma'lumotlarni o'chirib qayta yozish — dublikatlar oldini oladi
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass  # Hali mavjud bo'lmasa ham muammo yo'q
    collection = client.create_collection(COLLECTION_NAME)
    logger.info("Collection tozalandi, yangi ma'lumotlar yozilmoqda")

    vector_store = ChromaVectorStore(chroma_collection=collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    VectorStoreIndex(nodes, storage_context=storage_context, show_progress=True)

    logger.info("Barcha chunklar ChromaDB ga saqlandi")

    return {
        "total_chunks": len(nodes),
        "processed_files": processed,
        "failed_files": failed,
        "total_documents": len(all_documents),
    }
