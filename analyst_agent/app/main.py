import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.graph import analyst_graph
from app.llm import LLMOutputError
from app.schemas import (ChatRequest, ChatResponse, FeedbackResponse, InterviewData)
from app.stats import EmptyInterviewError

logger = logging.getLogger(__name__)

app = FastAPI(title="analyst_agent")


@app.exception_handler(EmptyInterviewError)
async def _empty(_: Request, exc: EmptyInterviewError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.exception_handler(LLMOutputError)
async def _llm_output(_: Request, exc: LLMOutputError) -> JSONResponse:
    return JSONResponse(status_code=502, content={"detail": str(exc)})


try:  # ошибки самого GigaChat: авторизация, сеть, рейт-лимит
    from gigachat.exceptions import GigaChatException

    @app.exception_handler(GigaChatException)
    async def _gigachat(_: Request, exc: GigaChatException) -> JSONResponse:
        logger.warning("GigaChat error: %s", type(exc).__name__)
        return JSONResponse(status_code=502, content={"detail": "Сбой при обращении к GigaChat"})
except ImportError:  # pragma: no cover
    pass


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "agent": "analyst_agent"}


@app.post("/v1/feedback", response_model=FeedbackResponse)
def feedback(data: InterviewData) -> FeedbackResponse:
    result = analyst_graph.invoke({"mode": "feedback", "interview": data})
    return FeedbackResponse(stats=result["stats"], feedback=result["feedback"])


@app.post("/v1/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    result = analyst_graph.invoke(
        {
            "mode": "chat",
            "interview": req.interview,
            "feedback": req.feedback,
            "history": req.history,
            "question": req.question,
        }
    )
    return ChatResponse(answer=result["answer"])
