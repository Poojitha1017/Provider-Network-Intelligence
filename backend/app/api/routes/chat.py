from fastapi import APIRouter, HTTPException, status
from app.schemas.chat import ChatQueryRequest, ChatQueryResponse
from app.services.chat_service import chat_service

router = APIRouter()


@router.post("/query", response_model=ChatQueryResponse, summary="Natural Language Network Intelligence Chat")
async def chat_query(request: ChatQueryRequest):
    """
    Processes natural language queries against live healthcare access and decision intelligence models.
    """
    try:
        return chat_service.process_query(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing intelligence query: {str(e)}",
        )

@router.post("/summarize", summary="Generate Executive Network Summary")
async def chat_summarize():
    """
    Generates an executive summary of provider network gaps and recommendations using LLM / AI.
    """
    try:
        return chat_service.summarize_content()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating executive summary: {str(e)}",
        )
