"""
Wealify Smart Finance — FastAPI Backend
Trợ lý AI soi sao kê: Quản lý chi tiêu & an toàn giao dịch
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import DEMO_MODE, DISCLAIMER_VI
from chat import ChatOrchestrator
from audit_log import audit_log

app = FastAPI(
    title="Wealify Smart Finance",
    description="AI Assistant for expense management & transaction safety",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global chat orchestrator (per-server session for demo)
orchestrator = ChatOrchestrator()


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    type: str
    lang: str
    disclaimer: str


@app.get("/health")
def health():
    return {
        "status": "ok",
        "app": "Wealify Smart Finance",
        "version": "2.0.0",
        "mode": "chatbot",
        "demo_mode": DEMO_MODE,
        "disclaimer": DISCLAIMER_VI,
    }


@app.post("/chat")
def chat(req: ChatRequest):
    """Main chat endpoint — process user message and return response."""
    result = orchestrator.process_message(req.message)
    return result


@app.get("/audit-log")
def get_audit_log():
    """Get all audit log entries."""
    return {
        "entries": audit_log.get_all_flags(),
        "summary": audit_log.get_summary(),
    }


@app.get("/audit-log/export")
def export_audit_log():
    """Export audit log to file and return path."""
    path = audit_log.export_flags()
    return {"exported_to": path, "total_entries": len(audit_log.get_all_flags())}


@app.post("/reset")
def reset_session():
    """Reset chat session (for demo purposes)."""
    global orchestrator
    orchestrator = ChatOrchestrator()
    audit_log.clear()
    return {"status": "reset", "message": "Session and audit log cleared."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
