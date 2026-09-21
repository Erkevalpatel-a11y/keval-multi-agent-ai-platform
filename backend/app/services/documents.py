from pathlib import Path
import uuid
from pypdf import PdfReader
from docx import Document as DocxDocument

SUPPORTED = {
    ".pdf": "application/pdf",
    ".txt": "text/plain",
    ".csv": "text/csv",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
}

def safe_name(name: str) -> str:
    cleaned = Path(name).name.replace("..", "_")
    return cleaned or "upload"

def extract_text(path: Path) -> tuple[str, int]:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        reader = PdfReader(str(path))
        parts = []
        for page in reader.pages:
            parts.append(page.extract_text() or "")
        return "\n".join(parts), len(reader.pages)
    if suffix == ".docx":
        doc = DocxDocument(str(path))
        return "\n".join(p.text for p in doc.paragraphs), 0
    if suffix in {".txt", ".csv"}:
        return path.read_text(encoding="utf-8", errors="replace"), 0
    return "", 0

def chunk_text(text: str, size: int = 1400, overlap: int = 200):
    text = text.strip()
    chunks = []
    start = 0
    while start < len(text):
        end = min(len(text), start + size)
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = max(end - overlap, start + 1)
    return chunks

def new_id() -> str:
    return uuid.uuid4().hex
