"""API routes for the PPT generation system."""
import json
import asyncio
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
from app.models.schemas import (
    PPTRequest,
    PPTOutline,
    GenerateOutlineRequest,
    GenerateSlidesRequest,
    ChatRequest,
    StyleType,
    ThemeA,
    ThemeB,
)
from app.services.llm_service import get_llm_service
from app.services.ppt_service import get_ppt_service
from app.services.template_service import get_template_service

router = APIRouter(prefix="/api", tags=["PPT Generation"])


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "PPT Generation System"}


@router.get("/themes")
async def get_themes():
    """Get available styles and themes."""
    return {
        "styles": {
            "style-a": {
                "name": "电子杂志 × 电子墨水",
                "description": "Monocle 杂志风、衬线字体、大片留白、叙事感强",
                "themes": [
                    {"id": "ink-classic", "name": "墨水经典", "colors": {"bg": "#faf8f5", "text": "#1a1a1a", "accent": "#c41e3a"}},
                    {"id": "indigo-porcelain", "name": "靛蓝瓷", "colors": {"bg": "#f5f7fa", "text": "#1e2a3a", "accent": "#3b5998"}},
                    {"id": "forest-ink", "name": "森林墨", "colors": {"bg": "#f6f8f4", "text": "#1a2e1a", "accent": "#4a7c59"}},
                    {"id": "kraft-paper", "name": "牛皮纸", "colors": {"bg": "#fdf8f0", "text": "#3d2b1f", "accent": "#c4732e"}},
                    {"id": "sand-dune", "name": "沙丘", "colors": {"bg": "#fbf9f6", "text": "#2e261e", "accent": "#c4945a"}},
                ],
                "layouts": ["cover", "section", "title-body", "two-column", "quote", "big-number", "timeline", "grid-cards", "closing"],
            },
            "style-b": {
                "name": "瑞士国际主义",
                "description": "16列网格、直角、1px发丝线、单一高饱和锚点色、无渐变无阴影",
                "themes": [
                    {"id": "ikb-blue", "name": "IKB 克莱因蓝", "colors": {"bg": "#ffffff", "text": "#1a1a1a", "accent": "#0015ff"}},
                    {"id": "lemon-yellow", "name": "柠檬黄", "colors": {"bg": "#ffffff", "text": "#1a1a1a", "accent": "#ffe600"}},
                    {"id": "lemon-green", "name": "柠檬绿", "colors": {"bg": "#ffffff", "text": "#1a1a1a", "accent": "#00ff62"}},
                    {"id": "safety-orange", "name": "安全橙", "colors": {"bg": "#ffffff", "text": "#1a1a1a", "accent": "#ff5f00"}},
                ],
                "layouts": ["cover", "section", "title-body", "two-column", "comparison", "quote", "big-number", "timeline", "grid-cards", "closing"],
            },
        }
    }


@router.post("/generate-outline", response_model=PPTOutline)
async def generate_outline(req: GenerateOutlineRequest):
    """Generate a PPT outline from a topic (fast, returns JSON structure)."""
    try:
        llm = get_llm_service()
        outline = await llm.generate_outline(req)
        return outline
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Outline generation failed: {str(e)}")


@router.post("/generate-full", response_model=PPTOutline)
async def generate_full_ppt(req: PPTRequest):
    """Generate a complete PPT with detailed content."""
    try:
        ppt_service = get_ppt_service()
        outline = await ppt_service.generate_full_ppt(req)
        return outline
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PPT generation failed: {str(e)}")


@router.post("/enhance-slides", response_model=PPTOutline)
async def enhance_slides(req: GenerateSlidesRequest):
    """Enhance an existing outline with detailed content."""
    try:
        ppt_service = get_ppt_service()
        outline = await ppt_service.generate_from_outline(req)
        return outline
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Slide enhancement failed: {str(e)}")


@router.post("/render-html")
async def render_html(outline: PPTOutline, bg_type: str = "gradient"):
    """Render a PPT outline to a single-file HTML presentation."""
    try:
        template_service = get_template_service()
        html = template_service.render_html(outline, bg_type)
        return HTMLResponse(content=html, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"HTML rendering failed: {str(e)}")


@router.post("/chat")
async def chat_iterate(req: ChatRequest):
    """Interactive chat for PPT iteration."""
    try:
        llm = get_llm_service()
        result = await llm.chat_iterate(req.messages, req.current_outline)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@router.post("/stream-generate")
async def stream_generate(req: PPTRequest):
    """Stream the PPT generation process via SSE."""
    ppt_service = get_ppt_service()

    async def event_generator():
        try:
            async for event in ppt_service.stream_generate(req):
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'step': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/export-html")
async def export_html(outline_json: str):
    """Export PPT as downloadable HTML file (GET with query param)."""
    try:
        outline_data = json.loads(outline_json)
        outline = PPTOutline(**outline_data)
        template_service = get_template_service()
        html = template_service.render_html(outline)
        return HTMLResponse(
            content=html,
            status_code=200,
            headers={
                "Content-Disposition": f'attachment; filename="{outline.title or "presentation"}.html"',
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")
