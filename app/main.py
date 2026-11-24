
import os
import secrets
from pathlib import Path
from typing import List, Optional

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field


# =====================================
# DIRECTORY
# =====================================

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
STATIC_DIR = BASE_DIR / "static"


# =====================================
# ENVIRONMENT CONFIGURATION
# =====================================

load_dotenv(PROJECT_DIR / ".env", override=True)

USERNAME = os.getenv("USERNAME", "admin")
PASSWORD = os.getenv("PASSWORD", "change-this-password")

AI_BASE_URL = os.getenv(
    "AI_BASE_URL",
    "https://openrouter.ai/api/v1"
).rstrip("/")

AI_API_KEY = os.getenv("AI_API_KEY", "")

AI_MODEL = os.getenv(
    "AI_MODEL",
    "openrouter/free"
)


# =====================================
# FASTAPI APPLICATION
# =====================================

app = FastAPI(
    title="MXYZ AI",
    version="0.1.0"
)

security = HTTPBasic()


# =====================================
# AUTHENTICATION
# =====================================

def require_private_access(
    credentials: HTTPBasicCredentials = Depends(security)
):
    username_ok = secrets.compare_digest(
        credentials.username.encode("utf-8"),
        USERNAME.encode("utf-8")
    )

    password_ok = secrets.compare_digest(
        credentials.password.encode("utf-8"),
        PASSWORD.encode("utf-8")
    )

    if not (username_ok and password_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username atau password salah",
            headers={"WWW-Authenticate": "Basic"}
        )

    return credentials.username


# =====================================
# REQUEST MODELS
# =====================================

class ChatMessage(BaseModel):
    role: str = Field(
        regex="^(system|user|assistant)$"
    )

    content: str = Field(
        min_length=1,
        max_length=30000
    )


class ChatRequest(BaseModel):
    messages: List[ChatMessage]

    temperature: Optional[float] = Field(
        default=0.7,
        ge=0,
        le=2
    )

    max_tokens: Optional[int] = Field(
        default=2048,
        ge=1,
        le=8192
    )


class ChatResponse(BaseModel):
    reply: str
    response: str
    model: str


# =====================================
# HEALTH CHECK
# =====================================

@app.get("/api/health")
def health_check(
    username: str = Depends(require_private_access)
):
    configured = bool(
        AI_BASE_URL and AI_API_KEY and AI_MODEL
    )

    return {
        "status": "online",
        "app": "MXYZ AI",
        "ai_configured": configured,
        "provider": "OpenRouter",
        "model": AI_MODEL
    }


# =====================================
# CHAT API
# =====================================

@app.post("/api/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    username: str = Depends(require_private_access)
):

    if not AI_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="API key belum dikonfigurasi."
        )

    if not request.messages:
        raise HTTPException(
            status_code=400,
            detail="Pesan tidak boleh kosong."
        )

    url = f"{AI_BASE_URL}/chat/completions"

    headers = {
        "Authorization": f"Bearer {AI_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "MXYZ AI"
    }

    payload = {
        "model": AI_MODEL,
        "messages": [
            {
                "role": "system",
                "content": """Kamu adalah MXYZ, AI pribadi yang jenius, humoris, strategis, kreatif, dan ahli coding.

IDENTITAS:
Nama kamu adalah MXYZ. Pertahankan identitas ini dalam setiap percakapan.

KEPRIBADIAN:
- Suka bercanda dan humor cerdas.
- Santai, ramah, dan bersahabat.
- Tahu kapan harus serius.
- Memiliki pemikiran kritis, logis, dan strategis.
- Kreatif dalam mencari solusi.

KEMAMPUAN:
- Ahli coding, debugging, algoritma, dan pengembangan software.
- Mampu menganalisis masalah yang kompleks.
- Mampu membuat dan memperbaiki kode.
- Memahami berbagai bahasa pemrograman dan teknologi.
- Memberikan solusi praktis dan terstruktur.

CARA MENJAWAB:
- Gunakan bahasa yang natural dan mudah dipahami.
- Berikan penjelasan bertahap jika diperlukan.
- Jangan bertele-tele.
- Gunakan contoh kode jika membantu.
- Pertimbangkan beberapa kemungkinan sebelum menyimpulkan.

PRINSIP:
- Utamakan akurasi dan kejujuran.
- Jangan mengarang informasi.
- Akui jika tidak mengetahui sesuatu.
- Jangan mengorbankan ketepatan hanya demi humor.
- Selalu pertahankan karakter MXYZ."""
            }
        ] + [
            message.dict()
            for message in request.messages
        ],
        "temperature": request.temperature,
        "max_tokens": request.max_tokens
    }

    try:
        with httpx.Client(timeout=90) as client:
            response = client.post(
                url,
                headers=headers,
                json=payload
            )

            response.raise_for_status()

            result = response.json()

        choices = result.get("choices", [])

        if not choices:
            raise HTTPException(
                status_code=502,
                detail="AI tidak memberikan jawaban."
            )

        reply = (
            choices[0]
            .get("message", {})
            .get("content")
        )

        if not isinstance(reply, str) or not reply.strip():
            raise HTTPException(
                status_code=502,
                detail="Jawaban AI kosong atau tidak valid."
            )

        return {
            "reply": reply,
            "response": reply,
            "model": result.get("model", AI_MODEL)
        }

    except httpx.HTTPStatusError as exc:
        print(
            "OpenRouter HTTP ERROR:",
            exc.response.status_code,
            exc.response.text[:2000]
        )

        raise HTTPException(
            status_code=502,
            detail="OpenRouter menolak permintaan. Periksa log Termux."
        )

    except httpx.RequestError as exc:
        print(
            "AI CONNECTION ERROR:",
            type(exc).__name__,
            str(exc)
        )

        raise HTTPException(
            status_code=502,
            detail="Tidak dapat terhubung ke server AI."
        )

    except HTTPException:
        raise

    except Exception as exc:
        print(
            "AI INTERNAL ERROR:",
            type(exc).__name__,
            str(exc)
        )

        raise HTTPException(
            status_code=500,
            detail="Terjadi kesalahan internal MXYZ AI."
        )


# =====================================
# FRONTEND
# =====================================

@app.get("/")
def home(
    username: str = Depends(require_private_access)
):
    index_file = STATIC_DIR / "index.html"

    if not index_file.exists():
        raise HTTPException(
            status_code=404,
            detail="index.html tidak ditemukan."
        )

    return FileResponse(index_file)


# =====================================
# STATIC FILES
# =====================================

app.mount(
    "/static",
    StaticFiles(directory=str(STATIC_DIR)),
    name="static"
)

