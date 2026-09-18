"""
Translation route: /translate.
"""

from fastapi import APIRouter

from ..schemas import TranslationRequest, TranslationResponse
from ..services import translation_service

router = APIRouter(tags=["Translation"])


@router.post(
    "/translate",
    response_model=TranslationResponse,
    summary="Translate detected sign text",
    description="Translate detected sign language text to Hindi, Kannada, or Malayalam. "
    "Uses Google Translate API.",
)
async def translate(request: TranslationRequest):
    """Translate text to the specified language."""
    success, result, original = translation_service.translate_text(
        request.text, request.language
    )

    if success:
        return TranslationResponse(
            success=True,
            translated_text=result,
            original_text=original,
        )
    else:
        return TranslationResponse(
            success=False,
            message=result,
        )
