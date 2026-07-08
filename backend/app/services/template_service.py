"""HTML template rendering service for PPT generation.

Renders slide decks into single-file HTML presentations using Jinja2.
Two visual systems:
- Style A: Editorial Magazine × E-Ink (衬线字体, 大片留白, 叙事感)
- Style B: Swiss Internationalist (16列网格, 直角, 1px发丝线, 单一高饱和锚点色)

Background types (per-slide):
- photo:    Keyword-themed photos from Picsum
- gradient: Curated CSS gradients matched to content mood
- pattern:  Subtle SVG geometric patterns
- none:     Clean background (default per-style behavior)
"""
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
from app.models.schemas import PPTOutline, SlideContent, LayoutType, StyleType
from app.services.bg_service import BackgroundService, BgType

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


class TemplateService:
    """Renders PPT data into single-file HTML slide decks."""

    def __init__(self):
        self.env = Environment(
            loader=FileSystemLoader(str(TEMPLATES_DIR)),
            autoescape=select_autoescape(["html"]),
        )
        self._bg_service: BackgroundService | None = None

    @property
    def bg_service(self) -> BackgroundService:
        if self._bg_service is None:
            self._bg_service = BackgroundService()
        return self._bg_service

    # Unsplash-like placeholder image service (free, no API key needed)
    PLACEHOLDER_BASE = "https://picsum.photos"

    def _placeholder_url(self, width: int, height: int, seed: int = 0) -> str:
        """Generate a placeholder image URL using picsum (free)."""
        sid = seed if seed > 0 else hash(str(width) + str(height)) % 1000
        return f"{self.PLACEHOLDER_BASE}/seed/{sid}/{width}/{height}"

    def _bg_pattern(self, accent_hex: str) -> str:
        """CSS background decorative patterns with geometric accents."""
        return (
            f"background-image:"
            f"radial-gradient(circle at 15% 20%, {accent_hex}08 0%, transparent 50%),"
            f"radial-gradient(circle at 85% 75%, {accent_hex}06 0%, transparent 50%),"
            f"radial-gradient(circle at 50% 50%, {accent_hex}04 0%, transparent 70%);"
        )

    def render_html(self, outline: PPTOutline, bg_type: str = "gradient") -> str:
        """Render a complete PPT outline to single-file HTML."""
        if outline.style == StyleType.A:
            return self._render_style_a(outline, bg_type)
        else:
            return self._render_style_b(outline, bg_type)

    def _slide_bg_style(self, slide: SlideContent, theme: str, bg_type: str,
                        slide_index: int = 0) -> str:
        """Generate inline background style for a single slide."""
        if bg_type == "none":
            return ""

        # Get accent color for the theme
        theme_colors = {
            "ink-classic": "#c41e3a", "indigo-porcelain": "#3b5998",
            "forest-ink": "#4a7c59", "kraft-paper": "#c4732e", "sand-dune": "#c4945a",
            "ikb-blue": "#0015ff", "lemon-yellow": "#ffe600",
            "lemon-green": "#00ff62", "safety-orange": "#ff5f00",
        }
        accent = theme_colors.get(theme, "#0015ff")

        # Build keyword from slide content
        keyword = self.bg_service.extract_keyword(
            title=slide.title or "",
            body=slide.body or "",
            bullet_points=slide.bullet_points,
        )
        if slide.image_placeholder and bg_type == "photo":
            keyword = slide.image_placeholder

        try:
            bg_enum = BgType(bg_type)
        except ValueError:
            bg_enum = BgType.GRADIENT

        result = self.bg_service.get_background(
            bg_enum, keyword=keyword, accent_hex=accent, slide_index=slide_index,
        )
        return result.css

    # ========== Style A: Editorial Magazine ==========

    def _render_style_a(self, outline: PPTOutline, bg_type: str = "gradient") -> str:
        """Render Editorial Magazine style HTML."""
        slides_html = ""
        for i, slide in enumerate(outline.slides):
            slides_html += self._render_slide_a(slide, outline.theme, bg_type, i)

        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{self._escape(outline.title)}</title>
{self._get_style_a_css(outline.theme)}
</head>
<body>
<div class="deck-container" id="deck">
  <div class="progress-bar"><div class="progress-fill" id="progress"></div></div>
  <button class="nav-dot-btn prev" onclick="navigate(-1)" aria-label="上一页">‹</button>
  <button class="nav-dot-btn next" onclick="navigate(1)" aria-label="下一页">›</button>
  <div class="dots-nav" id="dots"></div>
  <div class="slide-counter" id="counter">1 / {len(outline.slides)}</div>
{slides_html}
</div>
{self._get_shared_script(len(outline.slides))}
</body>
</html>"""

    def _get_style_a_css(self, theme: str) -> str:
        themes = {
            "ink-classic": {"bg": "#faf8f5", "text": "#1a1a1a", "accent": "#c41e3a", "meta": "#6b6b6b", "font": "'Noto Serif SC', 'Source Han Serif SC', Georgia, serif"},
            "indigo-porcelain": {"bg": "#f5f7fa", "text": "#1e2a3a", "accent": "#3b5998", "meta": "#6b7b8d", "font": "'Noto Serif SC', 'Source Han Serif SC', Georgia, serif"},
            "forest-ink": {"bg": "#f6f8f4", "text": "#1a2e1a", "accent": "#4a7c59", "meta": "#5d6d5d", "font": "'Noto Serif SC', 'Source Han Serif SC', Georgia, serif"},
            "kraft-paper": {"bg": "#fdf8f0", "text": "#3d2b1f", "accent": "#c4732e", "meta": "#8b7355", "font": "'Noto Serif SC', 'Source Han Serif SC', Georgia, serif"},
            "sand-dune": {"bg": "#fbf9f6", "text": "#2e261e", "accent": "#c4945a", "meta": "#9b8b7a", "font": "'Noto Serif SC', 'Source Han Serif SC', Georgia, serif"},
        }
        t = themes.get(theme, themes["ink-classic"])
        return f"""<style>
:root {{ --bg: {t["bg"]}; --text: {t["text"]}; --accent: {t["accent"]}; --meta: {t["meta"]}; --font: {t["font"]}; }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family: var(--font); background: #000; display:flex; justify-content:center; align-items:center; min-height:100vh; }}
.deck-container {{ position:relative; width:1280px; height:720px; overflow:hidden; background:var(--bg); box-shadow:0 20px 60px rgba(0,0,0,.5); }}
.slide {{ position:absolute; top:0; left:0; width:100%; height:100%; display:flex; flex-direction:column; justify-content:center; padding:80px 100px; opacity:0; transform:translateX(40px); transition:opacity .5s,transform .5s; pointer-events:none; }}
.slide.active {{ opacity:1; transform:translateX(0); pointer-events:auto; }}
.slide.prev {{ opacity:0; transform:translateX(-40px); }}
/* Cover */
.slide-cover {{ align-items:center; text-align:center; }}
.slide-cover .cover-title {{ font-size:48px; font-weight:700; color:var(--text); letter-spacing:2px; line-height:1.3; max-width:800px; }}
.slide-cover .cover-subtitle {{ font-size:20px; color:var(--meta); margin-top:24px; font-style:italic; }}
.slide-cover .cover-line {{ width:60px; height:2px; background:var(--accent); margin:32px auto; }}
/* Section divider */
.slide-section {{ justify-content:center; align-items:flex-start; }}
.slide-section .section-num {{ font-size:14px; color:var(--accent); letter-spacing:3px; text-transform:uppercase; margin-bottom:16px; }}
.slide-section .section-title {{ font-size:42px; font-weight:700; color:var(--text); line-height:1.2; max-width:700px; }}
.slide-section .section-line {{ width:80px; height:1px; background:var(--accent); margin-top:32px; }}
/* Title + Body */
.slide-title-body {{ justify-content:center; align-items:flex-start; }}
.slide-title-body .slide-title {{ font-size:32px; font-weight:700; color:var(--text); margin-bottom:32px; }}
.slide-title-body .slide-body {{ font-size:18px; color:var(--text); line-height:1.8; max-width:900px; }}
.slide-title-body .slide-body p {{ margin-bottom:12px; }}
.slide-title-body ul {{ padding-left:24px; }}
.slide-title-body li {{ margin-bottom:10px; line-height:1.6; }}
/* Two column */
.slide-two-column {{ flex-direction:row; gap:60px; padding:80px; }}
.slide-two-column .col {{ flex:1; display:flex; flex-direction:column; justify-content:center; }}
.slide-two-column .col-title {{ font-size:24px; font-weight:700; color:var(--text); margin-bottom:20px; }}
.slide-two-column .col-body {{ font-size:16px; color:var(--text); line-height:1.7; }}
/* Quote */
.slide-quote {{ justify-content:center; align-items:center; text-align:center; padding:100px 160px; }}
.slide-quote .quote-mark {{ font-size:120px; color:var(--accent); line-height:1; opacity:.3; margin-bottom:-40px; font-family:Georgia,serif; }}
.slide-quote .quote-text {{ font-size:30px; color:var(--text); font-style:italic; line-height:1.5; max-width:800px; }}
.slide-quote .quote-author {{ font-size:16px; color:var(--meta); margin-top:24px; }}
/* Big Number */
.slide-big-number {{ justify-content:center; align-items:center; text-align:center; }}
.slide-big-number .big-num {{ font-size:120px; font-weight:900; color:var(--accent); line-height:1; }}
.slide-big-number .big-label {{ font-size:24px; color:var(--text); margin-top:16px; }}
/* Timeline */
.slide-timeline {{ justify-content:center; align-items:flex-start; padding:80px 100px; }}
.slide-timeline .slide-title {{ font-size:28px; margin-bottom:40px; }}
.slide-timeline .tl-items {{ position:relative; padding-left:40px; border-left:2px solid var(--accent); }}
.slide-timeline .tl-item {{ margin-bottom:24px; position:relative; }}
.slide-timeline .tl-item::before {{ content:''; position:absolute; left:-48px; top:6px; width:12px; height:12px; background:var(--accent); border-radius:50%; }}
.slide-timeline .tl-date {{ font-size:14px; color:var(--accent); margin-bottom:4px; }}
.slide-timeline .tl-text {{ font-size:18px; color:var(--text); }}
/* Grid cards */
.slide-grid-cards {{ flex-direction:row; flex-wrap:wrap; gap:24px; padding:80px; align-content:center; }}
.slide-grid-cards .grid-card {{ flex:0 0 calc(50% - 12px); padding:32px; border:1px solid rgba(0,0,0,.08); backdrop-filter:blur(4px); }}
.slide-grid-cards .grid-card h4 {{ font-size:20px; color:var(--text); margin-bottom:8px; }}
.slide-grid-cards .grid-card p {{ font-size:15px; color:var(--meta); line-height:1.6; }}
/* Closing */
.slide-closing {{ align-items:center; text-align:center; }}
.slide-closing .closing-title {{ font-size:36px; color:var(--text); }}
.slide-closing .closing-subtitle {{ font-size:18px; color:var(--meta); margin-top:16px; }}
/* Navigation */
.progress-bar {{ position:absolute; top:0; left:0; height:3px; background:var(--accent); z-index:100; transition:width .3s; }}
.nav-dot-btn {{ position:absolute; top:50%; transform:translateY(-50%); z-index:100; background:none; border:none; font-size:40px; color:var(--meta); cursor:pointer; padding:12px; opacity:.4; transition:opacity .3s; }}
.nav-dot-btn:hover {{ opacity:1; }}
.nav-dot-btn.prev {{ left:16px; }}
.nav-dot-btn.next {{ right:16px; }}
.dots-nav {{ position:absolute; bottom:20px; left:50%; transform:translateX(-50%); display:flex; gap:8px; z-index:100; }}
.dots-nav .dot {{ width:8px; height:8px; border-radius:50%; background:var(--meta); opacity:.3; cursor:pointer; transition:opacity .3s; }}
.dots-nav .dot.active {{ opacity:1; background:var(--accent); }}
.slide-counter {{ position:absolute; bottom:20px; right:24px; font-size:13px; color:var(--meta); z-index:100; }}
/* Decorative background */
.slide-bg {{ position:absolute; inset:0; pointer-events:none; z-index:0; opacity:.6; }}
.slide-bg .geo-circle {{ position:absolute; border-radius:50%; border:1px solid var(--accent); opacity:.08; }}
.slide-bg .geo-line {{ position:absolute; background:var(--accent); opacity:.04; }}
/* Image layouts */
.slide-image-full {{ padding:0; }}
.slide-image-full .img-full-bg {{ position:absolute; inset:0; background-size:cover; background-position:center; }}
.slide-image-full .img-full-overlay {{ position:absolute; inset:0; background:linear-gradient(to top, var(--bg) 0%, transparent 60%, var(--bg) 100%); z-index:1; }}
.slide-image-full .img-full-content {{ position:relative; z-index:2; display:flex; flex-direction:column; justify-content:flex-end; height:100%; padding:70px 90px; }}
.slide-image-full .img-full-title {{ font-size:36px; font-weight:700; color:var(--text); max-width:700px; }}
.slide-image-full .img-full-body {{ font-size:17px; color:var(--text); margin-top:12px; max-width:600px; line-height:1.6; }}
.slide-image-left {{ flex-direction:row; padding:0; }}
.slide-image-left .img-col {{ width:45%; background-size:cover; background-position:center; position:relative; }}
.slide-image-left .img-col::after {{ content:''; position:absolute; right:0; top:0; bottom:0; width:40px; background:linear-gradient(to right, transparent, var(--bg)); }}
.slide-image-left .text-col {{ flex:1; padding:60px 70px; display:flex; flex-direction:column; justify-content:center; }}
.slide-image-left .text-col .slide-title {{ font-size:28px; font-weight:700; color:var(--text); margin-bottom:20px; }}
.slide-image-left .text-col .slide-body {{ font-size:16px; color:var(--text); line-height:1.7; }}
/* Corner accents */
.corner-accent {{ position:absolute; width:24px; height:24px; z-index:5; pointer-events:none; }}
.corner-accent.tl {{ top:30px; left:30px; border-top:2px solid var(--accent); border-left:2px solid var(--accent); }}
.corner-accent.br {{ bottom:30px; right:30px; border-bottom:2px solid var(--accent); border-right:2px solid var(--accent); }}
/* Background photo overlay */
.bg-photo-overlay {{ position:absolute; inset:0; z-index:0; pointer-events:none;
  background:linear-gradient(135deg, rgba(255,255,255,.35) 0%, rgba(255,255,255,.1) 50%, rgba(255,255,255,.4) 100%); }}
/* Gradient/pattern decorations */
.slide-bg-deco {{ position:absolute; inset:0; z-index:0; pointer-events:none; overflow:hidden; }}
.bg-deco-circle {{ position:absolute; border-radius:50%; border:1px solid var(--accent); opacity:.06; }}
/* Ensure content stays above backgrounds */
.slide > *:not(.bg-photo-overlay):not(.slide-bg-deco):not(.img-full-bg):not(.img-full-overlay):not(.img-col) {{ position:relative; z-index:1; }}
</style>"""

    def _render_slide_a(self, slide: SlideContent, theme: str,
                         bg_type: str = "gradient", slide_index: int = 0) -> str:
        """Render a single slide in Style A (Editorial Magazine)."""
        layout = slide.layout.value if slide.layout else "title-body"
        title = self._escape(slide.title or "")
        body = self._render_markdown_body(slide.body or "")
        bullets = slide.bullet_points or []
        subtitle = self._escape(slide.subtitle or "")
        # Background
        bg_style = self._slide_bg_style(slide, theme, bg_type, slide_index)
        bg_attr = f' style="{bg_style}"' if bg_style else ""
        photo_overlay = '<div class="bg-photo-overlay"></div>' if bg_type == "photo" and bg_style else ""
        # Decoration for gradient/pattern backgrounds
        bg_decoration = (
            '<div class="slide-bg-deco">'
            f'<div class="bg-deco-circle" style="top:8%;left:5%;width:200px;height:200px;"></div>'
            f'<div class="bg-deco-circle" style="bottom:10%;right:8%;width:160px;height:160px;"></div>'
            '</div>'
        ) if bg_type in ("gradient", "pattern") and bg_style else ""

        if layout == "cover":
            return f"""
<div class="slide slide-cover"{bg_attr}>{photo_overlay}{bg_decoration}
  <div class="cover-title">{title}</div>
  {f'<div class="cover-line"></div>' if title else ''}
  {f'<div class="cover-subtitle">{subtitle}</div>' if subtitle else ''}
</div>"""

        elif layout == "section":
            return f"""
<div class="slide slide-section"{bg_attr}>{photo_overlay}{bg_decoration}
  <div class="section-num">PART</div>
  <div class="section-title">{title}</div>
  <div class="section-line"></div>
</div>"""

        elif layout == "title-body":
            bullets_html = "".join(f"<li>{self._escape(b)}</li>" for b in bullets) if bullets else ""
            return f"""
<div class="slide slide-title-body"{bg_attr}>{photo_overlay}{bg_decoration}
  <div class="slide-title">{title}</div>
  <div class="slide-body">{body}{f'<ul>{bullets_html}</ul>' if bullets_html else ''}</div>
</div>"""

        elif layout == "two-column":
            cols = slide.columns or [{"title": "", "body": ""}, {"title": "", "body": ""}]
            cols_html = ""
            for col in cols:
                cols_html += f'<div class="col"><div class="col-title">{self._escape(col.get("title", ""))}</div><div class="col-body">{self._render_markdown_body(col.get("body", ""))}</div></div>'
            return f'<div class="slide slide-two-column"{bg_attr}>{photo_overlay}{bg_decoration}{cols_html}</div>'

        elif layout == "quote":
            author = self._escape(slide.quote_author or "")
            return f"""
<div class="slide slide-quote"{bg_attr}>{photo_overlay}{bg_decoration}
  <div class="quote-mark">"</div>
  <div class="quote-text">{self._escape(slide.quote or body)}</div>
  {f'<div class="quote-author">—— {author}</div>' if author else ''}
</div>"""

        elif layout == "big-number":
            return f"""
<div class="slide slide-big-number"{bg_attr}>{photo_overlay}{bg_decoration}
  <div class="big-num">{self._escape(slide.big_number or '')}</div>
  {f'<div class="big-label">{self._escape(slide.big_number_label or title)}</div>' if title or slide.big_number_label else ''}
</div>"""

        elif layout == "timeline":
            return f"""
<div class="slide slide-timeline"{bg_attr}>{photo_overlay}{bg_decoration}
  <div class="slide-title">{title}</div>
  <div class="tl-items">{body}</div>
</div>"""

        elif layout == "grid-cards":
            cards_html = ""
            for b in bullets:
                parts = b.split("：", 1) if "：" in b else b.split(":", 1)
                h = parts[0] if len(parts) > 1 else b
                p = parts[1] if len(parts) > 1 else ""
                cards_html += f'<div class="grid-card"><h4>{self._escape(h)}</h4>{f"<p>{self._escape(p)}</p>" if p else ""}</div>'
            return f'<div class="slide slide-grid-cards"{bg_attr}>{photo_overlay}{bg_decoration}{cards_html}</div>'

        elif layout == "image-full":
            img_url = slide.image_url or self._placeholder_url(1280, 720, slide.slide_number)
            return f"""
<div class="slide slide-image-full"{bg_attr}>
  <div class="img-full-bg" style="background-image:url({img_url});"></div>
  <div class="img-full-overlay"></div>
  <div class="img-full-content">
    <div class="img-full-title">{title}</div>
    {f'<div class="img-full-body">{self._escape(slide.body[:200] if slide.body else "")}</div>' if slide.body else ''}
  </div>
  <div class="corner-accent tl"></div>
  <div class="corner-accent br"></div>
</div>"""

        elif layout == "image-left":
            img_url = slide.image_url or self._placeholder_url(576, 720, slide.slide_number + 100)
            return f"""
<div class="slide slide-image-left"{bg_attr}>{photo_overlay}{bg_decoration}
  <div class="img-col" style="background-image:url({img_url});"></div>
  <div class="text-col">
    <div class="slide-title">{title}</div>
    <div class="slide-body">{body}{''.join(f'<li>{self._escape(b)}</li>' for b in bullets) if bullets else ''}</div>
  </div>
</div>"""

        elif layout == "image-right":
            img_url = slide.image_url or self._placeholder_url(576, 720, slide.slide_number + 200)
            bullets_html = "".join(f"<li>{self._escape(b)}</li>" for b in bullets) if bullets else ""
            return f"""
<div class="slide slide-image-left"{bg_attr} style="flex-direction:row-reverse;">{photo_overlay}{bg_decoration}
  <div class="img-col" style="background-image:url({img_url});"></div>
  <div class="text-col">
    <div class="slide-title">{title}</div>
    <div class="slide-body">{body}{f'<ul>{bullets_html}</ul>' if bullets_html else ''}</div>
  </div>
</div>"""

        elif layout == "closing":
            return f"""
<div class="slide slide-closing"{bg_attr}>{photo_overlay}{bg_decoration}
  <div class="closing-title">{title or '谢谢'}</div>
  {f'<div class="closing-subtitle">{subtitle}</div>' if subtitle else ''}
</div>"""

        else:
            # Default: title + body
            return f"""
<div class="slide slide-title-body"{bg_attr}>{photo_overlay}{bg_decoration}
  {f'<div class="slide-title">{title}</div>' if title else ''}
  {f'<div class="slide-body">{body}</div>' if body else ''}
</div>"""

    # ========== Style B: Swiss Internationalist ==========

    def _render_style_b(self, outline: PPTOutline, bg_type: str = "gradient") -> str:
        """Render Swiss Internationalist style HTML."""
        slides_html = ""
        for i, slide in enumerate(outline.slides):
            slides_html += self._render_slide_b(slide, outline.theme, bg_type, i)

        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{self._escape(outline.title)}</title>
{self._get_style_b_css(outline.theme)}
</head>
<body>
<div class="swiss-deck" id="deck">
  <div class="swiss-progress"><div class="swiss-progress-fill" id="progress"></div></div>
  <button class="swiss-nav prev" onclick="navigate(-1)" aria-label="上一页">←</button>
  <button class="swiss-nav next" onclick="navigate(1)" aria-label="下一页">→</button>
  <div class="swiss-dots" id="dots"></div>
  <div class="swiss-counter"><span id="currentSlide">1</span>/<span>{len(outline.slides)}</span></div>
  <div class="swiss-grid-overlay" id="gridOverlay" style="display:none">
    {"".join(f'<div class="grid-line" style="left:{100/16*i}%"></div>' for i in range(17))}
  </div>
{slides_html}
</div>
{self._get_shared_script(len(outline.slides))}
</body>
</html>"""

    def _get_style_b_css(self, theme: str) -> str:
        themes = {
            "ikb-blue":      {"bg": "#ffffff", "text": "#1a1a1a", "accent": "#0015ff", "meta": "#6b6b6b", "rules": "#e0e0e0", "font": "'Noto Sans SC', 'PingFang SC', -apple-system, sans-serif"},
            "lemon-yellow":  {"bg": "#ffffff", "text": "#1a1a1a", "accent": "#ffe600", "meta": "#6b6b6b", "rules": "#e0e0e0", "font": "'Noto Sans SC', 'PingFang SC', -apple-system, sans-serif"},
            "lemon-green":   {"bg": "#ffffff", "text": "#1a1a1a", "accent": "#00ff62", "meta": "#6b6b6b", "rules": "#e0e0e0", "font": "'Noto Sans SC', 'PingFang SC', -apple-system, sans-serif"},
            "safety-orange": {"bg": "#ffffff", "text": "#1a1a1a", "accent": "#ff5f00", "meta": "#6b6b6b", "rules": "#e0e0e0", "font": "'Noto Sans SC', 'PingFang SC', -apple-system, sans-serif"},
        }
        t = themes.get(theme, themes["ikb-blue"])
        return f"""<style>
:root {{ --bg: {t["bg"]}; --text: {t["text"]}; --accent: {t["accent"]}; --meta: {t["meta"]}; --rules: {t["rules"]}; --font: {t["font"]}; }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family: var(--font); font-weight:400; background:#000; display:flex; justify-content:center; align-items:center; min-height:100vh; -webkit-font-smoothing:antialiased; }}
.swiss-deck {{ position:relative; width:1280px; height:720px; overflow:hidden; background:var(--bg); box-shadow:0 20px 60px rgba(0,0,0,.5); }}
/* 16-column grid helper */
.swiss-grid-overlay {{ position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none; z-index:200; }}
.swiss-grid-overlay .grid-line {{ position:absolute; top:0; height:100%; width:1px; background:rgba(0,21,255,.15); }}
/* Slides */
.swiss-slide {{ position:absolute; top:0; left:0; width:100%; height:100%; padding:60px 80px; opacity:0; transform:translateX(40px); transition:opacity .4s,transform .4s; pointer-events:none; display:flex; flex-direction:column; }}
.swiss-slide.active {{ opacity:1; transform:translateX(0); pointer-events:auto; }}
/* Typography */
.swiss-cover {{ justify-content:flex-end; padding-bottom:80px; }}
.swiss-cover .swiss-meta {{ font-size:12px; color:var(--accent); letter-spacing:4px; text-transform:uppercase; margin-bottom:20px; font-weight:600; }}
.swiss-cover .swiss-title {{ font-size:56px; font-weight:700; color:var(--text); line-height:1.1; letter-spacing:-1px; max-width:900px; }}
.swiss-cover .swiss-subtitle {{ font-size:18px; color:var(--meta); margin-top:16px; font-weight:400; }}
.swiss-cover .swiss-rule {{ width:100%; height:1px; background:var(--accent); margin-top:40px; }}
/* Section */
.swiss-section {{ justify-content:center; }}
.swiss-section .swiss-section-num {{ font-size:11px; color:var(--accent); letter-spacing:6px; margin-bottom:20px; font-weight:600; }}
.swiss-section .swiss-section-title {{ font-size:44px; font-weight:700; color:var(--text); max-width:800px; line-height:1.2; }}
.swiss-section .swiss-section-rule {{ width:60px; height:2px; background:var(--accent); margin-top:30px; }}
/* Title + Body (standard content slide) */
.swiss-content {{ justify-content:flex-start; padding-top:60px; }}
.swiss-content .swiss-content-title {{ font-size:28px; font-weight:700; color:var(--text); margin-bottom:32px; padding-bottom:20px; border-bottom:1px solid var(--rules); }}
.swiss-content .swiss-body {{ font-size:17px; color:var(--text); line-height:1.7; max-width:800px; }}
.swiss-content .swiss-body p {{ margin-bottom:10px; }}
.swiss-content ul {{ list-style:none; padding:0; }}
.swiss-content li {{ padding:8px 0; padding-left:20px; position:relative; border-bottom:1px solid var(--rules); }}
.swiss-content li::before {{ content:''; position:absolute; left:0; top:16px; width:6px; height:6px; background:var(--accent); }}
/* Two column (grid-based) */
.swiss-two-col {{ flex-direction:row; gap:0; padding:0; }}
.swiss-two-col .swiss-col {{ flex:1; padding:60px; display:flex; flex-direction:column; justify-content:center; }}
.swiss-two-col .swiss-col:first-child {{ border-right:1px solid var(--rules); }}
.swiss-two-col .swiss-col-title {{ font-size:22px; font-weight:700; color:var(--text); margin-bottom:20px; }}
.swiss-two-col .swiss-col-body {{ font-size:16px; color:var(--text); line-height:1.7; }}
/* Quote */
.swiss-quote {{ justify-content:center; align-items:flex-start; }}
.swiss-quote .swiss-quote-rule {{ width:120px; height:4px; background:var(--accent); margin-bottom:40px; }}
.swiss-quote .swiss-quote-text {{ font-size:28px; font-weight:500; color:var(--text); line-height:1.4; max-width:800px; }}
.swiss-quote .swiss-quote-author {{ font-size:14px; color:var(--meta); margin-top:20px; font-weight:400; }}
/* Big number */
.swiss-stat {{ justify-content:center; align-items:flex-start; }}
.swiss-stat .swiss-stat-num {{ font-size:140px; font-weight:900; color:var(--accent); line-height:1; letter-spacing:-4px; }}
.swiss-stat .swiss-stat-label {{ font-size:20px; color:var(--text); margin-top:8px; border-top:2px solid var(--accent); padding-top:16px; }}
/* Timeline */
.swiss-timeline {{ justify-content:flex-start; padding-top:60px; }}
.swiss-timeline .swiss-content-title {{ font-size:28px; font-weight:700; margin-bottom:40px; padding-bottom:20px; border-bottom:1px solid var(--rules); }}
.swiss-timeline .swiss-tl {{ display:flex; gap:0; }}
.swiss-timeline .swiss-tl-item {{ flex:1; padding:20px 16px 0 16px; border-top:3px solid var(--accent); }}
.swiss-timeline .swiss-tl-item .tl-num {{ font-size:12px; color:var(--accent); font-weight:700; margin-bottom:8px; }}
.swiss-timeline .swiss-tl-item .tl-text {{ font-size:15px; color:var(--text); line-height:1.5; }}
/* Grid cards */
.swiss-grid {{ flex-direction:row; flex-wrap:wrap; gap:1px; padding:0; background:var(--rules); }}
.swiss-grid .swiss-card {{ flex:0 0 calc(50% - 0.5px); background:var(--bg); padding:40px; display:flex; flex-direction:column; justify-content:center; }}
.swiss-grid .swiss-card h4 {{ font-size:20px; font-weight:700; margin-bottom:12px; color:var(--text); }}
.swiss-grid .swiss-card p {{ font-size:15px; color:var(--meta); line-height:1.6; }}
/* Comparison */
.swiss-compare {{ flex-direction:row; gap:0; padding:0; }}
.swiss-compare .swiss-compare-col {{ flex:1; padding:60px; }}
.swiss-compare .swiss-compare-col:first-child {{ background:var(--bg); border-right:2px solid var(--accent); }}
.swiss-compare .swiss-compare-col:last-child {{ background:color-mix(in srgb, var(--accent) 3%, var(--bg)); }}
.swiss-compare .swiss-compare-label {{ font-size:11px; color:var(--accent); letter-spacing:3px; margin-bottom:24px; font-weight:700; }}
.swiss-compare .swiss-compare-body {{ font-size:16px; color:var(--text); line-height:1.7; }}
/* Closing */
.swiss-closing {{ justify-content:center; align-items:flex-start; }}
.swiss-closing .swiss-closing-rule {{ width:100%; height:1px; background:var(--accent); margin-bottom:40px; }}
.swiss-closing .swiss-closing-title {{ font-size:40px; font-weight:700; color:var(--text); }}
.swiss-closing .swiss-closing-subtitle {{ font-size:16px; color:var(--meta); margin-top:12px; }}
/* Nav */
.swiss-progress {{ position:absolute; top:0; left:0; height:2px; background:var(--accent); z-index:100; transition:width .3s; }}
.swiss-nav {{ position:absolute; top:50%; transform:translateY(-50%); z-index:100; background:var(--bg); border:1px solid var(--rules); font-size:18px; color:var(--text); cursor:pointer; padding:12px 16px; transition:all .2s; }}
.swiss-nav:hover {{ border-color:var(--accent); color:var(--accent); }}
.swiss-nav.prev {{ left:20px; }}
.swiss-nav.next {{ right:20px; }}
.swiss-dots {{ position:absolute; bottom:20px; left:50%; transform:translateX(-50%); display:flex; gap:10px; z-index:100; }}
.swiss-dots .dot {{ width:6px; height:6px; background:var(--rules); cursor:pointer; transition:all .2s; }}
.swiss-dots .dot.active {{ background:var(--accent); transform:scale(1.4); }}
.swiss-counter {{ position:absolute; bottom:20px; right:24px; font-size:12px; color:var(--meta); z-index:100; letter-spacing:1px; }}
/* Swiss decorative patterns */
.swiss-bg-geo {{ position:absolute; inset:0; pointer-events:none; z-index:0; }}
.swiss-bg-geo .swiss-geo-rect {{ position:absolute; border:1px solid var(--accent); opacity:.06; }}
.swiss-bg-geo .swiss-geo-dot {{ position:absolute; width:3px; height:3px; background:var(--accent); opacity:.12; }}
/* Swiss image layouts */
.swiss-img-full {{ padding:0; }}
.swiss-img-full .swiss-img-bg {{ position:absolute; inset:0; background-size:cover; background-position:center; }}
.swiss-img-full .swiss-img-overlay {{ position:absolute; inset:0; background:linear-gradient(0deg, var(--bg) 0%, transparent 50%, rgba(0,0,0,.3) 100%); z-index:1; }}
.swiss-img-full .swiss-img-content {{ position:relative; z-index:2; display:flex; flex-direction:column; justify-content:flex-end; height:100%; padding:60px 80px; }}
.swiss-img-full .swiss-img-title {{ font-size:40px; font-weight:700; color:var(--text); max-width:750px; line-height:1.15; }}
.swiss-img-full .swiss-img-body {{ font-size:16px; color:var(--text); margin-top:12px; max-width:550px; }}
.swiss-img-left {{ flex-direction:row; padding:0; }}
.swiss-img-left .swiss-img-col {{ width:48%; background-size:cover; background-position:center; }}
.swiss-img-left .swiss-text-col {{ flex:1; padding:60px; display:flex; flex-direction:column; justify-content:center; border-left:1px solid var(--rules); }}
.swiss-img-left .swiss-text-col .swiss-content-title {{ font-size:26px; font-weight:700; color:var(--text); margin-bottom:24px; padding-bottom:16px; border-bottom:2px solid var(--accent); }}
.swiss-img-left .swiss-text-col .swiss-body {{ font-size:16px; color:var(--text); line-height:1.7; }}
/* Swiss corner marks */
.swiss-corner {{ position:absolute; z-index:5; pointer-events:none; }}
.swiss-corner::before,.swiss-corner::after {{ content:''; position:absolute; background:var(--accent); opacity:.3; }}
.swiss-corner.tl {{ top:28px; left:28px; }}
.swiss-corner.tl::before {{ width:18px; height:1px; top:0; left:0; }}
.swiss-corner.tl::after {{ width:1px; height:18px; top:0; left:0; }}
.swiss-corner.br {{ bottom:28px; right:28px; }}
.swiss-corner.br::before {{ width:18px; height:1px; bottom:0; right:0; }}
.swiss-corner.br::after {{ width:1px; height:18px; bottom:0; right:0; }}
/* Swiss photo overlay */
.swiss-photo-overlay {{ position:absolute; inset:0; z-index:0; pointer-events:none;
  background:linear-gradient(180deg, rgba(0,0,0,.25) 0%, rgba(0,0,0,.05) 50%, rgba(0,0,0,.2) 100%); }}
/* Swiss gradient/pattern decorations */
.swiss-bg-deco {{ position:absolute; inset:0; z-index:0; pointer-events:none; overflow:hidden; }}
.swiss-deco-rect {{ position:absolute; border:1px solid var(--accent); opacity:.05; }}
/* Ensure content stays above backgrounds */
.swiss-slide > *:not(.swiss-photo-overlay):not(.swiss-bg-deco):not(.swiss-img-bg):not(.swiss-img-overlay):not(.swiss-img-col) {{ position:relative; z-index:1; }}
</style>"""

    def _render_slide_b(self, slide: SlideContent, theme: str,
                         bg_type: str = "gradient", slide_index: int = 0) -> str:
        """Render a single slide in Style B (Swiss Internationalist)."""
        layout = slide.layout.value if slide.layout else "title-body"
        title = self._escape(slide.title or "")
        body = self._render_markdown_body(slide.body or "")
        bullets = slide.bullet_points or []
        subtitle = self._escape(slide.subtitle or "")
        # Background
        bg_style = self._slide_bg_style(slide, theme, bg_type, slide_index)
        bg_attr = f' style="{bg_style}"' if bg_style else ""
        swiss_photo_overlay = '<div class="swiss-photo-overlay"></div>' if bg_type == "photo" and bg_style else ""
        swiss_bg_deco = (
            '<div class="swiss-bg-deco">'
            f'<div class="swiss-deco-rect" style="top:6%;left:3%;width:120px;height:120px;"></div>'
            f'<div class="swiss-deco-rect" style="bottom:8%;right:5%;width:90px;height:90px;"></div>'
            '</div>'
        ) if bg_type in ("gradient", "pattern") and bg_style else ""

        if layout == "cover":
            return f"""
<div class="swiss-slide swiss-cover"{bg_attr}>{swiss_photo_overlay}{swiss_bg_deco}
  <div class="swiss-meta">PRESENTATION</div>
  <div class="swiss-title">{title}</div>
  {f'<div class="swiss-subtitle">{subtitle}</div>' if subtitle else ''}
  <div class="swiss-rule"></div>
</div>"""

        elif layout == "section":
            return f"""
<div class="swiss-slide swiss-section"{bg_attr}>{swiss_photo_overlay}{swiss_bg_deco}
  <div class="swiss-section-num">SECTION</div>
  <div class="swiss-section-title">{title}</div>
  <div class="swiss-section-rule"></div>
</div>"""

        elif layout == "title-body":
            bullets_html = "".join(f"<li>{self._escape(b)}</li>" for b in bullets) if bullets else ""
            return f"""
<div class="swiss-slide swiss-content"{bg_attr}>{swiss_photo_overlay}{swiss_bg_deco}
  <div class="swiss-content-title">{title}</div>
  <div class="swiss-body">{body}{f'<ul>{bullets_html}</ul>' if bullets_html else ''}</div>
</div>"""

        elif layout == "two-column":
            cols = slide.columns or [{"title": "", "body": ""}, {"title": "", "body": ""}]
            cols_html = ""
            for col in cols:
                cols_html += f'<div class="swiss-col"><div class="swiss-col-title">{self._escape(col.get("title", ""))}</div><div class="swiss-col-body">{self._render_markdown_body(col.get("body", ""))}</div></div>'
            return f'<div class="swiss-slide swiss-two-col"{bg_attr}>{swiss_photo_overlay}{swiss_bg_deco}{cols_html}</div>'

        elif layout == "comparison":
            cols = slide.columns or [{"title": "", "body": ""}, {"title": "", "body": ""}]
            if len(cols) >= 2:
                return f"""
<div class="swiss-slide swiss-compare"{bg_attr}>{swiss_photo_overlay}{swiss_bg_deco}
  <div class="swiss-compare-col">
    <div class="swiss-compare-label">{self._escape(cols[0].get("title", "A"))}</div>
    <div class="swiss-compare-body">{self._render_markdown_body(cols[0].get("body", ""))}</div>
  </div>
  <div class="swiss-compare-col">
    <div class="swiss-compare-label">{self._escape(cols[1].get("title", "B"))}</div>
    <div class="swiss-compare-body">{self._render_markdown_body(cols[1].get("body", ""))}</div>
  </div>
</div>"""
            return self._render_slide_b_default(title, body, bullets)

        elif layout == "quote":
            author = self._escape(slide.quote_author or "")
            quote_text = self._escape(slide.quote or body)
            return f"""
<div class="swiss-slide swiss-quote"{bg_attr}>{swiss_photo_overlay}{swiss_bg_deco}
  <div class="swiss-quote-rule"></div>
  <div class="swiss-quote-text">{quote_text}</div>
  {f'<div class="swiss-quote-author">—— {author}</div>' if author else ''}
</div>"""

        elif layout == "big-number":
            return f"""
<div class="swiss-slide swiss-stat"{bg_attr}>{swiss_photo_overlay}{swiss_bg_deco}
  <div class="swiss-stat-num">{self._escape(slide.big_number or '')}</div>
  {f'<div class="swiss-stat-label">{self._escape(slide.big_number_label or title)}</div>' if title or slide.big_number_label else ''}
</div>"""

        elif layout == "timeline":
            items_html = ""
            for b in bullets:
                parts = b.split("：", 1) if "：" in b else b.split(":", 1)
                items_html += f'<div class="swiss-tl-item"><div class="tl-num">{self._escape(parts[0])}</div><div class="tl-text">{self._escape(parts[1] if len(parts) > 1 else b)}</div></div>'
            return f"""
<div class="swiss-slide swiss-timeline"{bg_attr}>{swiss_photo_overlay}{swiss_bg_deco}
  <div class="swiss-content-title">{title}</div>
  <div class="swiss-tl">{items_html}</div>
</div>"""

        elif layout == "grid-cards":
            cards_html = ""
            for b in bullets:
                parts = b.split("：", 1) if "：" in b else b.split(":", 1)
                h = parts[0] if len(parts) > 1 else b[:20]
                p = parts[1] if len(parts) > 1 else b
                cards_html += f'<div class="swiss-card"><h4>{self._escape(h)}</h4><p>{self._escape(p)}</p></div>'
            return f'<div class="swiss-slide swiss-grid"{bg_attr}>{swiss_photo_overlay}{swiss_bg_deco}{cards_html}</div>'

        elif layout == "image-full":
            img_url = slide.image_url or self._placeholder_url(1280, 720, slide.slide_number)
            return f"""
<div class="swiss-slide swiss-img-full"{bg_attr}>
  <div class="swiss-img-bg" style="background-image:url({img_url});"></div>
  <div class="swiss-img-overlay"></div>
  <div class="swiss-img-content">
    <div class="swiss-img-title">{title}</div>
    {f'<div class="swiss-img-body">{self._escape(slide.body[:200] if slide.body else "")}</div>' if slide.body else ''}
  </div>
  <div class="swiss-corner tl"></div>
  <div class="swiss-corner br"></div>
</div>"""

        elif layout == "image-left":
            img_url = slide.image_url or self._placeholder_url(614, 720, slide.slide_number + 100)
            return f"""
<div class="swiss-slide swiss-img-left"{bg_attr}>{swiss_photo_overlay}{swiss_bg_deco}
  <div class="swiss-img-col" style="background-image:url({img_url});"></div>
  <div class="swiss-text-col">
    <div class="swiss-content-title">{title}</div>
    <div class="swiss-body">{body}{''.join(f'<li>{self._escape(b)}</li>' for b in bullets) if bullets else ''}</div>
  </div>
  <div class="swiss-corner br"></div>
</div>"""

        elif layout == "image-right":
            img_url = slide.image_url or self._placeholder_url(614, 720, slide.slide_number + 200)
            bullets_html = "".join(f"<li>{self._escape(b)}</li>" for b in bullets) if bullets else ""
            return f"""
<div class="swiss-slide swiss-img-left"{bg_attr} style="flex-direction:row-reverse;">{swiss_photo_overlay}{swiss_bg_deco}
  <div class="swiss-img-col" style="background-image:url({img_url});"></div>
  <div class="swiss-text-col" style="border-left:none;border-right:1px solid var(--rules);">
    <div class="swiss-content-title">{title}</div>
    <div class="swiss-body">{body}{f'<ul>{bullets_html}</ul>' if bullets_html else ''}</div>
  </div>
  <div class="swiss-corner tl"></div>
</div>"""

        elif layout == "closing":
            return f"""
<div class="swiss-slide swiss-closing"{bg_attr}>{swiss_photo_overlay}{swiss_bg_deco}
  <div class="swiss-closing-rule"></div>
  <div class="swiss-closing-title">{title or 'Thank You'}</div>
  {f'<div class="swiss-closing-subtitle">{subtitle}</div>' if subtitle else ''}
</div>"""

        else:
            return self._render_slide_b_default(title, body, bullets, bg_attr, swiss_photo_overlay, swiss_bg_deco)

    def _render_slide_b_default(self, title: str, body: str, bullets: list[str],
                                  bg_attr: str = "", overlay: str = "", deco: str = "") -> str:
        bullets_html = "".join(f"<li>{self._escape(b)}</li>" for b in bullets) if bullets else ""
        return f"""
<div class="swiss-slide swiss-content"{bg_attr}>{overlay}{deco}
  {f'<div class="swiss-content-title">{title}</div>' if title else ''}
  <div class="swiss-body">{body}{f'<ul>{bullets_html}</ul>' if bullets_html else ''}</div>
</div>"""

    # ========== Shared utilities ==========

    def _render_markdown_body(self, text: str) -> str:
        """Render a simple markdown body to HTML."""
        if not text:
            return ""
        lines = text.strip().split("\n")
        html = ""
        for line in lines:
            line = line.strip()
            if not line:
                html += "<br>"
            elif line.startswith("### "):
                html += f"<h4>{self._escape(line[4:])}</h4>"
            elif line.startswith("## "):
                html += f"<h3>{self._escape(line[3:])}</h3>"
            elif line.startswith("# "):
                html += f"<h2>{self._escape(line[2:])}</h2>"
            elif line.startswith("- "):
                html += f"<li>{self._escape(line[2:])}</li>"
            elif line.startswith("> "):
                html += f'<blockquote style="border-left:2px solid var(--accent);padding-left:16px;margin:8px 0;color:var(--meta);">{self._escape(line[2:])}</blockquote>'
            else:
                # Bold and italic support
                line = self._escape(line)
                line = line.replace("**", "").replace("__", "")  # simplified
                html += f"<p>{line}</p>"
        return html

    @staticmethod
    def _escape(text: str) -> str:
        """Escape HTML entities."""
        if not text:
            return ""
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

    def _get_shared_script(self, total_slides: int) -> str:
        """JavaScript for slide navigation (shared by both styles)."""
        return f"""<script>
(function() {{
  var slides = document.querySelectorAll('.slide, .swiss-slide');
  var dotsEl = document.getElementById('dots');
  var progress = document.getElementById('progress');
  var counter = document.getElementById('counter');
  var currentEl = document.getElementById('currentSlide');
  var current = 0;
  var total = slides.length;

  // Create dots
  for (var i = 0; i < total; i++) {{
    var dot = document.createElement('span');
    dot.className = 'dot' + (i === 0 ? ' active' : '');
    dot.onclick = (function(idx) {{ return function() {{ goTo(idx); }}; }})(i);
    dotsEl.appendChild(dot);
  }}

  function update() {{
    slides.forEach(function(s, i) {{
      s.classList.remove('active', 'prev');
      if (i === current) s.classList.add('active');
      else if (i < current) s.classList.add('prev');
    }});
    var dots = dotsEl.querySelectorAll('.dot');
    dots.forEach(function(d, i) {{ d.classList.toggle('active', i === current); }});
    if (progress) progress.style.width = ((current + 1) / total * 100) + '%';
    if (counter) counter.textContent = (current + 1) + ' / ' + total;
    if (currentEl) currentEl.textContent = current + 1;
  }}

  function goTo(idx) {{
    current = Math.max(0, Math.min(total - 1, idx));
    update();
  }}

  window.navigate = function(dir) {{ goTo(current + dir); }};

  // Keyboard navigation
  document.addEventListener('keydown', function(e) {{
    if (e.key === 'ArrowRight' || e.key === 'ArrowDown' || e.key === ' ') {{
      e.preventDefault(); navigate(1);
    }} else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {{
      e.preventDefault(); navigate(-1);
    }} else if (e.key === 'Escape') {{
      // Toggle grid overlay
      var grid = document.getElementById('gridOverlay');
      if (grid) grid.style.display = grid.style.display === 'none' ? 'block' : 'none';
    }} else if (e.key === 'Home') {{
      e.preventDefault(); goTo(0);
    }} else if (e.key === 'End') {{
      e.preventDefault(); goTo(total - 1);
    }}
  }});

  // Touch swipe
  var touchStartX = 0;
  document.addEventListener('touchstart', function(e) {{ touchStartX = e.touches[0].clientX; }});
  document.addEventListener('touchend', function(e) {{
    var diff = touchStartX - e.changedTouches[0].clientX;
    if (Math.abs(diff) > 50) navigate(diff > 0 ? 1 : -1);
  }});

  // Mouse wheel
  var wheelTimeout;
  document.addEventListener('wheel', function(e) {{
    e.preventDefault();
    if (wheelTimeout) return;
    wheelTimeout = setTimeout(function() {{ wheelTimeout = null; }}, 800);
    navigate(e.deltaY > 0 ? 1 : -1);
  }}, {{ passive: false }});

  // Click on nav dots
  slides[0].classList.add('active');
  if (progress) progress.style.width = (1 / total * 100) + '%';
}})();
</script>"""


_template_service: TemplateService | None = None


def get_template_service() -> TemplateService:
    global _template_service
    if _template_service is None:
        _template_service = TemplateService()
    return _template_service
