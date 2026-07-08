"""PPT generation orchestration service."""
import asyncio
from typing import AsyncIterator
from app.models.schemas import (
    PPTOutline,
    PPTRequest,
    SlideContent,
    GenerateOutlineRequest,
    GenerateSlidesRequest,
    StyleType,
    LayoutType,
)
from app.services.llm_service import get_llm_service


async def _passthrough(slide: SlideContent) -> SlideContent:
    """Return slide unchanged (for batching with gather)."""
    return slide


async def _empty_prompts(slide: SlideContent) -> list:
    """Return empty prompts list."""
    return []


class PPTService:
    """Orchestrates the multi-step PPT generation pipeline."""

    def __init__(self):
        self.llm = get_llm_service()

    async def generate_full_ppt(self, req: PPTRequest) -> PPTOutline:
        """Complete PPT generation pipeline (outline → detail → images)."""
        # Step 1: Generate outline
        outline_req = GenerateOutlineRequest(
            topic=req.topic,
            style=req.style,
            audience=req.audience,
            slide_count=req.slide_count,
            language=req.language,
            additional_requirements=req.additional_requirements,
            tone=req.tone,
        )
        outline = await self.llm.generate_outline(outline_req)

        # Set theme if specified
        if req.theme:
            outline.theme = req.theme

        # Step 2: Enhance each slide with details (in parallel batches)
        slides = await self._enhance_slides(outline.slides, outline.style)

        # Step 3: Generate image prompts if requested
        if req.include_images:
            slides = await self._add_image_prompts(slides)

        outline.slides = slides
        return outline

    async def generate_from_outline(self, req: GenerateSlidesRequest) -> PPTOutline:
        """Enhance an existing outline with detailed content."""
        slides = await self._enhance_slides(req.outline.slides, req.outline.style)
        if req.include_images:
            slides = await self._add_image_prompts(slides)
        req.outline.slides = slides
        return req.outline

    async def _enhance_slides(
        self, slides: list[SlideContent], style: StyleType
    ) -> list[SlideContent]:
        """Enhance slides with detailed content in parallel batches."""
        batch_size = 5
        enhanced = []

        for i in range(0, len(slides), batch_size):
            batch = slides[i : i + batch_size]
            tasks = []
            for slide in batch:
                # Only enhance content slides, skip structural slides
                if slide.layout in (
                    LayoutType.COVER,
                    LayoutType.SECTION,
                    LayoutType.DIVIDER,
                    LayoutType.CLOSING,
                ):
                    tasks.append(_passthrough(slide))
                else:
                    tasks.append(self.llm.generate_slide_details(slide, style))

            batch_results = await asyncio.gather(*tasks)
            enhanced.extend(batch_results)

        return enhanced

    async def _add_image_prompts(
        self, slides: list[SlideContent]
    ) -> list[SlideContent]:
        """Add AI image generation prompts to visual slides."""
        visual_layouts = (
            LayoutType.IMAGE_FULL,
            LayoutType.IMAGE_LEFT,
            LayoutType.IMAGE_RIGHT,
            LayoutType.COVER,
            LayoutType.GRID_CARDS,
        )

        tasks = []
        for slide in slides:
            if slide.layout in visual_layouts and not slide.image_url:
                tasks.append(self.llm.generate_image_prompts(slide))
            else:
                tasks.append(_empty_prompts(slide))

        all_prompts = await asyncio.gather(*tasks)

        for slide, prompts in zip(slides, all_prompts):
            if prompts:
                slide.image_placeholder = prompts[0] if prompts else None

        return slides

    async def stream_generate(self, req: PPTRequest) -> AsyncIterator[dict]:
        """Stream the generation process step by step."""
        # Step 1
        yield {"step": "analyzing", "message": "正在分析主题需求..."}

        outline_req = GenerateOutlineRequest(
            topic=req.topic,
            style=req.style,
            audience=req.audience,
            slide_count=req.slide_count,
            language=req.language,
            additional_requirements=req.additional_requirements,
            tone=req.tone,
        )

        # Step 2
        yield {"step": "outline", "message": "正在生成PPT大纲结构..."}
        outline = await self.llm.generate_outline(outline_req)
        if req.theme:
            outline.theme = req.theme

        yield {"step": "outline_done", "outline": outline.model_dump(), "message": f"大纲生成完成，共{len(outline.slides)}页"}

        # Step 3: Enhance slides
        for i, slide in enumerate(outline.slides):
            yield {
                "step": "enhancing",
                "current": i + 1,
                "total": len(outline.slides),
                "message": f"正在丰富第{i+1}/{len(outline.slides)}页内容: {slide.title}",
            }

        slides = await self._enhance_slides(outline.slides, outline.style)
        outline.slides = slides

        # Step 4: Images (if requested)
        if req.include_images:
            yield {"step": "images", "message": "正在生成配图描述..."}
            slides = await self._add_image_prompts(slides)
            outline.slides = slides

        yield {"step": "done", "outline": outline.model_dump(), "message": "PPT生成完成!"}


_ppt_service: PPTService | None = None


def get_ppt_service() -> PPTService:
    global _ppt_service
    if _ppt_service is None:
        _ppt_service = PPTService()
    return _ppt_service
