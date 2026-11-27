from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.agent_service import send_message


router = APIRouter(prefix="/api", tags=["Stockline"])


class ChatRequest(BaseModel):
    user_id: str = Field(min_length=1, max_length=128)
    message: str = Field(min_length=1, max_length=10000)
    session_id: str | None = None


class ChatResponse(BaseModel):
    experience: str
    session_id: str
    response: str


@router.post("/chat/customer", response_model=ChatResponse)
async def customer_chat(request: ChatRequest):
    try:
        return await send_message(
            experience="customer",
            user_id=request.user_id,
            message=request.message,
            session_id=request.session_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="The customer assistant encountered an error.",
        )


@router.post("/chat/business", response_model=ChatResponse)
async def business_chat(request: ChatRequest):
    try:
        return await send_message(
            experience="business",
            user_id=request.user_id,
            message=request.message,
            session_id=request.session_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="The business assistant encountered an error.",
        )