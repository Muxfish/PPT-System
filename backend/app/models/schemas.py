"""Pydantic models for the PPT generation system."""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal, Union
from enum import Enum


class StyleType(str, Enum):
    A = "style-a"  # Editorial Magazine
    B = "style-b"  # Swiss Internationalist


class ThemeA(str, Enum):
    INK_CLASSIC = "ink-classic"
    INDIGO_PORCELAIN = "indigo-porcelain"
    FOREST_INK = "forest-ink"
    KRAFT_PAPER = "kraft-paper"
    SAND_DUNE = "sand-dune"


class ThemeB(str, Enum):
    IKB_BLUE = "ikb-blue"
    LEMON_YELLOW = "lemon-yellow"
    LEMON_GREEN = "lemon-green"
    SAFETY_ORANGE = "safety-orange"


class LayoutType(str, Enum):
    """All available layout types across both styles."""
    COVER = "cover"
    SECTION = "section"
    TITLE_BODY = "title-body"
    TWO_COLUMN = "two-column"
    THREE_COLUMN = "three-column"
    IMAGE_FULL = "image-full"
    IMAGE_LEFT = "image-left"
    IMAGE_RIGHT = "image-right"
    QUOTE = "quote"
    BIG_NUMBER = "big-number"
    TIMELINE = "timeline"
    COMPARISON = "comparison"
    GRID_CARDS = "grid-cards"
    LIST_ICON = "list-icon"
    CODE_SNIPPET = "code-snippet"
    TABLE_DATA = "table-data"
    DIVIDER = "divider"
    CLOSING = "closing"


class SlideContent(BaseModel):
    """Content for a single slide."""
    slide_number: int = Field(..., description="Slide number (1-indexed)")
    layout: LayoutType = Field(..., description="Layout type for this slide")
    title: Optional[str] = Field(None, description="Slide title")
    subtitle: Optional[str] = Field(None, description="Slide subtitle")
    body: Optional[str] = Field(None, description="Main body text (markdown supported)")
    bullet_points: Optional[list[str]] = Field(None, description="Bullet point list")
    columns: Optional[list[dict]] = Field(None, description="Multi-column content")
    quote: Optional[str] = Field(None, description="Quote text")
    quote_author: Optional[str] = Field(None, description="Quote author")
    big_number: Optional[Union[str, int, float]] = Field(None, description="Large stat/number")
    big_number_label: Optional[str] = Field(None, description="Label for big number")
    image_placeholder: Optional[str] = Field(None, description="Image description for generation")
    image_url: Optional[str] = Field(None, description="Image URL if available")
    code_snippet: Optional[str] = Field(None, description="Code content")
    code_language: Optional[str] = Field(None, description="Programming language")
    table_data: Optional[list[list[str]]] = Field(None, description="Table rows")
    speaker_notes: Optional[str] = Field(None, description="Speaker notes")

    @field_validator('big_number', mode='before')
    @classmethod
    def coerce_big_number_to_str(cls, v):
        """Coerce numeric values to string for display."""
        if v is None:
            return None
        if isinstance(v, (int, float)):
            return str(v)
        return v


class PPTRequest(BaseModel):
    """Request to generate a PPT."""
    topic: str = Field(..., min_length=1, max_length=500, description="PPT topic/title")
    style: StyleType = Field(StyleType.B, description="Visual style")
    theme: Optional[str] = Field(None, description="Color theme (depends on style)")
    audience: Optional[str] = Field(None, description="Target audience description")
    slide_count: int = Field(10, ge=3, le=30, description="Approximate number of slides")
    language: str = Field("zh-CN", description="Content language")
    additional_requirements: Optional[str] = Field(None, description="Extra requirements")
    include_images: bool = Field(False, description="Whether to include image prompts")
    tone: Optional[str] = Field(None, description="Tone: professional, casual, academic, etc.")
    bg_type: str = Field("gradient", description="Background type: photo, gradient, pattern")


class PPTOutline(BaseModel):
    """Generated PPT outline."""
    title: str = Field(..., description="PPT title")
    subtitle: Optional[str] = Field(None, description="PPT subtitle")
    style: StyleType = Field(..., description="Visual style")
    theme: str = Field(..., description="Color theme")
    slides: list[SlideContent] = Field(..., description="Slide content list")
    estimated_duration: Optional[int] = Field(None, description="Estimated minutes")


class GenerateOutlineRequest(BaseModel):
    """Request to generate an outline."""
    topic: str = Field(..., min_length=1, max_length=500)
    style: StyleType = Field(StyleType.B)
    audience: Optional[str] = None
    slide_count: int = Field(10, ge=3, le=30)
    language: str = Field("zh-CN")
    additional_requirements: Optional[str] = None
    tone: Optional[str] = None


class GenerateSlidesRequest(BaseModel):
    """Request to generate full slide content from outline."""
    outline: PPTOutline
    include_images: bool = False
    language: str = Field("zh-CN")


class ChatMessage(BaseModel):
    """Chat message for iterative editing."""
    role: Literal["user", "assistant", "system"]
    content: str


class ChatRequest(BaseModel):
    """Chat request for slide iteration."""
    messages: list[ChatMessage]
    current_outline: PPTOutline
