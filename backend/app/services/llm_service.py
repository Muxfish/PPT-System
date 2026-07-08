"""LangChain + DeepSeek service for PPT content generation."""
import json
import re
import httpx
from typing import AsyncIterator
from langchain_deepseek import ChatDeepSeek
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from app.core.config import get_settings
from app.models.schemas import (
    PPTOutline,
    SlideContent,
    LayoutType,
    StyleType,
    GenerateOutlineRequest,
)


class LLMService:
    """Service for LLM-powered PPT content generation."""

    def __init__(self):
        settings = get_settings()
        # httpx on Windows needs explicit local_address to avoid IPv6 issues
        transport = httpx.HTTPTransport(local_address="0.0.0.0", retries=1)
        async_transport = httpx.AsyncHTTPTransport(local_address="0.0.0.0", retries=1)
        http_client = httpx.Client(
            transport=transport,
            timeout=60.0,
            trust_env=True,
            follow_redirects=True,
        )
        async_http_client = httpx.AsyncClient(
            transport=async_transport,
            timeout=60.0,
            trust_env=True,
            follow_redirects=True,
        )
        self.llm = ChatDeepSeek(
            model=settings.deepseek_model,
            api_key=settings.deepseek_api_key,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
            http_client=http_client,
            http_async_client=async_http_client,
        )

    def _get_outline_system_prompt(self) -> str:
        return """你是一位顶尖的演示设计专家，精通信息架构、叙事设计和视觉传达。
你的任务是根据用户提供的主题，生成一份专业的PPT大纲。

## 设计原则
1. **叙事弧线**: 每份PPT都应该有清晰的故事线 — 引入 → 展开 → 高潮 → 收尾
2. **金字塔原理**: 核心观点先行，再用论据支撑
3. **一页一事**: 每页只传达一个核心信息
4. **节奏控制**: 在信息密集页之间穿插呼吸页（引言、引用、图片）
5. **视觉丰富性**: 善用图片布局增强表现力，每3-5页应出现一个图片页

## 可用布局类型
基础布局：
- cover: 封面页（标题+副标题）
- section: 章节分隔页（大标题，用于章节过渡）
- title-body: 标题+正文（最常用的内容页）
- two-column: 双栏布局（对比/并列信息）
- comparison: 对比页（左右对比，适合优劣分析）
- quote: 引用页（大号引用文字，适合金句/名言）
- big-number: 大数据展示（关键数字+说明，适合成果展示）
- timeline: 时间线（进程/发展历程）
- grid-cards: 卡片网格（多个要点卡片，适合特性罗列）
- closing: 结束页（总结+感谢）

图片增强布局（推荐使用以增加视觉冲击力）：
- image-full: 全屏图片+标题叠加（适合封面、章节开场、情感渲染）
- image-left: 左侧图片+右侧文字（适合产品展示、案例介绍）
- image-right: 右侧图片+左侧文字（同上，交替使用）

## 输出格式
你必须返回一个严格的JSON对象，格式如下：
{
  "title": "PPT标题",
  "subtitle": "副标题（可选）",
  "estimated_duration": 20,
  "slides": [
    {
      "slide_number": 1,
      "layout": "cover",
      "title": "页标题",
      "subtitle": "副标题（可选）",
      "body": "正文内容（markdown格式）",
      "bullet_points": ["要点1", "要点2"],
      "quote": null,
      "quote_author": null,
      "big_number": null,
      "big_number_label": null,
      "image_placeholder": "配图关键词描述（如：科技感的蓝色数据流）"
    }
  ]
}

## 注意事项
- 必须严格使用上述JSON格式，不要添加额外的文字说明
- bullet_points 用于列表类内容，每项简短有力（不超过20字）
- body 字段支持markdown格式
- 每页内容精炼，不要堆砌文字
- 封面页和结束页必须包含
- 对于image-full/image-left/image-right布局，必须填写image_placeholder字段，用简短的中文描述配图内容
- 在合适的位置使用图片布局：封面之后、章节开场、案例展示、数据可视化等"""

    def _get_outline_user_prompt(self, req: GenerateOutlineRequest) -> str:
        style_name = "电子杂志 × 电子墨水风格" if req.style == StyleType.A else "瑞士国际主义风格"
        prompt = f"""请为主题「{req.topic}」生成一份PPT大纲。

## 要求
- 视觉风格: {style_name}
- 幻灯片数量: 约{req.slide_count}页"""
        if req.audience:
            prompt += f"\n- 目标受众: {req.audience}"
        if req.tone:
            prompt += f"\n- 语调: {req.tone}"
        if req.language == "zh-CN":
            prompt += "\n- 语言: 中文"
        else:
            prompt += f"\n- 语言: {req.language}"
        if req.additional_requirements:
            prompt += f"\n- 额外要求: {req.additional_requirements}"

        prompt += """

请按照叙事弧线结构组织内容：
- 第1页: 封面
- 第2页: 目录/议程
- 中间页: 核心内容（根据主题展开）
- 倒数第2页: 总结
- 最后1页: 结束页/感谢

请直接返回JSON，不要包含任何其他文字。"""
        return prompt

    async def generate_outline(self, req: GenerateOutlineRequest) -> PPTOutline:
        """Generate a complete PPT outline based on topic."""
        messages = [
            SystemMessage(content=self._get_outline_system_prompt()),
            HumanMessage(content=self._get_outline_user_prompt(req)),
        ]

        response = await self.llm.ainvoke(messages)
        content = response.content.strip()

        # Extract JSON from response (handle markdown code blocks)
        json_str = self._extract_json(content)
        data = json.loads(json_str)

        # Convert to PPTOutline with proper enums
        slides = []
        for i, slide_data in enumerate(data.get("slides", [])):
            slide_data["slide_number"] = slide_data.get("slide_number", i + 1)
            slide_data["layout"] = self._validate_layout(slide_data.get("layout", "title-body"))
            slides.append(SlideContent(**slide_data))

        theme = "ink-classic" if req.style == StyleType.A else "ikb-blue"

        return PPTOutline(
            title=data.get("title", req.topic),
            subtitle=data.get("subtitle"),
            style=req.style,
            theme=theme,
            slides=slides,
            estimated_duration=data.get("estimated_duration"),
        )

    async def generate_slide_details(self, slide: SlideContent, style: StyleType) -> SlideContent:
        """Enrich a single slide with more detailed content."""
        system_prompt = """你是一位PPT内容优化专家。请为给定的幻灯片内容补充和优化细节。
保持原有结构，只增强内容的深度和表现力。返回JSON格式的幻灯片内容。"""

        user_prompt = f"""优化以下幻灯片内容：
- 布局: {slide.layout.value}
- 标题: {slide.title}
- 正文: {slide.body[:200] if slide.body else "无"}

请补充更丰富的细节、数据、案例或金句。保持简洁原则。返回JSON。"""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
        response = await self.llm.ainvoke(messages)
        json_str = self._extract_json(response.content)
        data = json.loads(json_str)

        # Merge with original, preferring original structure
        updated = slide.model_copy()
        if data.get("body"):
            updated.body = data["body"]
        if data.get("bullet_points"):
            updated.bullet_points = data["bullet_points"]
        if data.get("speaker_notes"):
            updated.speaker_notes = data["speaker_notes"]
        return updated

    async def generate_image_prompts(self, slide: SlideContent) -> list[str]:
        """Generate detailed image description prompts for a slide."""
        system_prompt = """你是一位顶级视觉设计师。为幻灯片内容生成高质量的配图描述关键词。
每个描述应该像Unsplash/Pexels的搜索关键词一样精准具体，适合搜索高质量图片。
返回JSON格式: {"prompts": ["描述1", "描述2"]}

关键词格式示例（中英文混合最佳）：
- "modern office workspace minimal desk"
- "抽象科技蓝色数据流线条"
- "山间日出自然风光大气磅礴 landscape sunrise"
- "business team meeting collaboration diverse"
- "极简白色建筑几何线条 architecture minimal"
"""

        user_prompt = f"""为以下幻灯片生成2个配图搜索关键词：
标题: {slide.title or '无'}
内容: {slide.body[:200] if slide.body else (slide.bullet_points or ['无'])}
布局类型: {slide.layout.value if slide.layout else 'title-body'}

请生成适合{slide.layout.value if slide.layout else '通用'}布局的配图关键词。返回JSON。"""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
        response = await self.llm.ainvoke(messages)
        json_str = self._extract_json(response.content)
        data = json.loads(json_str)
        return data.get("prompts", [])

    async def chat_iterate(
        self, messages: list, current_outline: PPTOutline
    ) -> dict:
        """Interactive chat for iterative PPT editing."""
        system_prompt = f"""你是一位PPT设计顾问。用户正在编辑一份PPT大纲，你需要根据用户的反馈修改内容。

当前大纲：
- 标题: {current_outline.title}
- 幻灯片数: {len(current_outline.slides)}
- 风格: {current_outline.style.value}

你可以：
1. 修改特定页的内容
2. 调整页面顺序
3. 增加或删除页面
4. 改变布局
5. 优化文字表达

当用户要求修改时，返回JSON：
{{
  "action": "update_slides" | "reorder" | "add_slide" | "delete_slide" | "chat",
  "message": "你的回复文字",
  "slides": [...]  // 修改后的幻灯片数据（如果是update/reorder/add）
}}

如果用户只是聊天提问，action设为"chat"，message回复即可。"""

        chat_messages = [SystemMessage(content=system_prompt)]
        for msg in messages:
            if msg.role == "user":
                chat_messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                chat_messages.append(AIMessage(content=msg.content))

        response = await self.llm.ainvoke(chat_messages)
        json_str = self._extract_json(response.content)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return {"action": "chat", "message": response.content}

    def _extract_json(self, text: str) -> str:
        """Extract JSON string from LLM response (may contain markdown code blocks)."""
        # Remove markdown code blocks
        text = re.sub(r"```(?:json)?\s*", "", text)
        text = re.sub(r"```\s*$", "", text)
        # Find the first { and last }
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            return text[start:end]
        return text

    def _validate_layout(self, layout_str: str) -> LayoutType:
        """Validate and normalize layout string to LayoutType enum."""
        try:
            return LayoutType(layout_str)
        except ValueError:
            # Fallback mappings
            mapping = {
                "title": LayoutType.TITLE_BODY,
                "body": LayoutType.TITLE_BODY,
                "full-image": LayoutType.IMAGE_FULL,
                "image": LayoutType.IMAGE_FULL,
                "ending": LayoutType.CLOSING,
                "end": LayoutType.CLOSING,
                "thanks": LayoutType.CLOSING,
                "toc": LayoutType.LIST_ICON,
                "agenda": LayoutType.LIST_ICON,
                "stat": LayoutType.BIG_NUMBER,
                "stats": LayoutType.BIG_NUMBER,
            }
            return mapping.get(layout_str.lower(), LayoutType.TITLE_BODY)


# Singleton
_llm_service: LLMService | None = None


def get_llm_service() -> LLMService:
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
