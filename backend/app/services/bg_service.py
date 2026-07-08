"""Background image service — provides beautiful backgrounds for PPT slides.

Three background types:
- photo:   Keyword-based photos from Picsum (free, no API key)
- gradient: Curated CSS gradients matched to theme accent colors
- pattern:  Subtle SVG geometric patterns
"""
import hashlib
from dataclasses import dataclass
from enum import Enum


class BgType(str, Enum):
    PHOTO = "photo"
    GRADIENT = "gradient"
    PATTERN = "pattern"


@dataclass
class BgResult:
    """Result from background generation."""
    css: str            # CSS background property value
    overlay: str        # Optional overlay gradient for text readability
    source: str         # Human-readable source description


# ── Curated CSS Gradient Library (60 gradients organized by mood) ──

GRADIENTS = {
    # Warm / sunset tones
    "sunset-warm":    "linear-gradient(135deg, #ff6b6b 0%, #feca57 50%, #ff9ff3 100%)",
    "sunset-golden":  "linear-gradient(135deg, #f5af19 0%, #f12711 50%, #f5af19 100%)",
    "peach-dream":    "linear-gradient(135deg, #ee9ca7 0%, #ffdde1 100%)",
    "coral-reef":     "linear-gradient(135deg, #ff7e5f 0%, #feb47b 100%)",
    "rose-petal":     "linear-gradient(135deg, #e8cbc0 0%, #636fa4 100%)",

    # Cool / blue tones
    "ocean-deep":     "linear-gradient(135deg, #0c3483 0%, #a2b6df 50%, #6b8cce 100%)",
    "frost-morning":  "linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%)",
    "arctic-twilight": "linear-gradient(135deg, #2193b0 0%, #6dd5ed 100%)",
    "midnight-blue":  "linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%)",
    "sky-serenity":   "linear-gradient(135deg, #89f7fe 0%, #66a6ff 100%)",

    # Nature / green
    "forest-canopy":  "linear-gradient(135deg, #134e5e 0%, #71b280 100%)",
    "mint-fresh":     "linear-gradient(135deg, #00b4db 0%, #0083b0 100%)",
    "emerald-mist":   "linear-gradient(135deg, #348f50 0%, #56b4d3 100%)",
    "sage-garden":    "linear-gradient(135deg, #96c93d 0%, #00b09b 100%)",
    "pine-glade":     "linear-gradient(135deg, #1d976c 0%, #93f9b9 100%)",

    # Purple / violet
    "lavender-haze":  "linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%)",
    "cosmic-dust":    "linear-gradient(135deg, #8e2de2 0%, #4a00e0 100%)",
    "orchid-blush":   "linear-gradient(135deg, #c471f5 0%, #fa71cd 100%)",
    "twilight-magic": "linear-gradient(135deg, #7028e4 0%, #e5b2ca 100%)",
    "plum-velvet":    "linear-gradient(135deg, #614385 0%, #516395 100%)",

    # Modern / tech
    "neon-pulse":     "linear-gradient(135deg, #00f2fe 0%, #4facfe 100%)",
    "cyber-lavender": "linear-gradient(135deg, #b224ef 0%, #7579ff 100%)",
    "data-stream":    "linear-gradient(135deg, #1a2980 0%, #26d0ce 100%)",
    "quantum-glow":   "linear-gradient(135deg, #0cd2e5 0%, #4339b5 100%)",
    "silicon-dawn":   "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",

    # Elegant / minimal
    "marble-white":   "linear-gradient(135deg, #e6e9f0 0%, #eef1f5 100%)",
    "silver-thread":  "linear-gradient(135deg, #bdc3c7 0%, #2c3e50 100%)",
    "pearl-essence":  "linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)",
    "cashmere-cream": "linear-gradient(135deg, #fdfcfb 0%, #e2d1c3 100%)",
    "linen-paper":    "linear-gradient(135deg, #d7ccc8 0%, #f5f5f5 100%)",

    # Bold / dramatic
    "volcanic-ash":   "linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%)",
    "crimson-tide":   "linear-gradient(135deg, #cb2d3e 0%, #ef473a 100%)",
    "obsidian-glass": "linear-gradient(135deg, #000000 0%, #434343 100%)",
    "electric-storm": "linear-gradient(135deg, #2b5876 0%, #4e4376 100%)",
    "aurora-burst":   "linear-gradient(135deg, #00c6ff 0%, #0072ff 100%)",

    # Soft / pastel
    "cotton-candy":   "linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)",
    "baby-blue":      "linear-gradient(135deg, #e0eafc 0%, #cfdef3 100%)",
    "powder-pink":    "linear-gradient(135deg, #ffeef8 0%, #f3e7e9 100%)",
    "mint-chip":      "linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%)",
    "vanilla-cream":  "linear-gradient(135deg, #fff9e6 0%, #f5e6cc 100%)",
}

# Organize gradients by tag for keyword matching
GRADIENT_TAGS = {
    "warm":   ["sunset-warm", "sunset-golden", "peach-dream", "coral-reef", "rose-petal"],
    "cool":   ["ocean-deep", "frost-morning", "arctic-twilight", "midnight-blue", "sky-serenity"],
    "nature": ["forest-canopy", "mint-fresh", "emerald-mist", "sage-garden", "pine-glade"],
    "purple": ["lavender-haze", "cosmic-dust", "orchid-blush", "twilight-magic", "plum-velvet"],
    "tech":   ["neon-pulse", "cyber-lavender", "data-stream", "quantum-glow", "silicon-dawn"],
    "elegant":["marble-white", "silver-thread", "pearl-essence", "cashmere-cream", "linen-paper"],
    "bold":   ["volcanic-ash", "crimson-tide", "obsidian-glass", "electric-storm", "aurora-burst"],
    "soft":   ["cotton-candy", "baby-blue", "powder-pink", "mint-chip", "vanilla-cream"],
}


# ── SVG Pattern Library ──

SVG_PATTERNS = {
    "dots": """
        <svg xmlns='http://www.w3.org/2000/svg' width='24' height='24'>
          <circle cx='12' cy='12' r='1.5' fill='{color}' opacity='0.06'/>
        </svg>""",
    "grid": """
        <svg xmlns='http://www.w3.org/2000/svg' width='40' height='40'>
          <rect width='40' height='40' fill='none' stroke='{color}' stroke-width='0.5' opacity='0.06'/>
        </svg>""",
    "cross": """
        <svg xmlns='http://www.w3.org/2000/svg' width='20' height='20'>
          <line x1='10' y1='0' x2='10' y2='20' stroke='{color}' stroke-width='0.5' opacity='0.05'/>
          <line x1='0' y1='10' x2='20' y2='10' stroke='{color}' stroke-width='0.5' opacity='0.05'/>
        </svg>""",
    "diagonal": """
        <svg xmlns='http://www.w3.org/2000/svg' width='30' height='30'>
          <line x1='0' y1='30' x2='30' y2='0' stroke='{color}' stroke-width='0.5' opacity='0.06'/>
        </svg>""",
    "wave": """
        <svg xmlns='http://www.w3.org/2000/svg' width='60' height='20'>
          <path d='M0 10 Q15 0 30 10 Q45 20 60 10' fill='none' stroke='{color}' stroke-width='1' opacity='0.05'/>
        </svg>""",
    "hexagon": """
        <svg xmlns='http://www.w3.org/2000/svg' width='32' height='32'>
          <polygon points='16,0 32,9 32,23 16,32 0,23 0,9' fill='none' stroke='{color}' stroke-width='0.8' opacity='0.05'/>
        </svg>""",
    "triangle": """
        <svg xmlns='http://www.w3.org/2000/svg' width='40' height='40'>
          <polygon points='20,5 38,35 2,35' fill='none' stroke='{color}' stroke-width='0.5' opacity='0.04'/>
        </svg>""",
}


# ── Photo keyword → mood mapping ──

PHOTO_MOODS = {
    "technology": ["abstract", "technology", "digital", "data", "circuit"],
    "business":   ["office", "workspace", "business", "corporate", "meeting"],
    "nature":     ["landscape", "mountain", "forest", "ocean", "nature"],
    "city":       ["city", "architecture", "urban", "skyline", "building"],
    "creative":   ["art", "design", "creative", "color", "abstract"],
    "science":    ["science", "laboratory", "research", "microscope", "space"],
    "people":     ["team", "people", "collaboration", "community", "diversity"],
    "product":    ["product", "minimal", "studio", "clean", "modern"],
    "education":  ["education", "learning", "library", "books", "school"],
    "health":     ["health", "wellness", "medical", "healthcare", "fitness"],
}


class BackgroundService:
    """Generates CSS backgrounds for slides — photos, gradients, or patterns."""

    # Picsum base URL
    PICSUM = "https://picsum.photos"

    def get_background(
        self,
        bg_type: BgType,
        *,
        keyword: str = "",
        accent_hex: str = "#0015ff",
        slide_index: int = 0,
        width: int = 1280,
        height: int = 720,
    ) -> BgResult:
        """Generate a background of the requested type."""
        if bg_type == BgType.PHOTO:
            return self._photo_bg(keyword, slide_index, width, height)
        elif bg_type == BgType.GRADIENT:
            return self._gradient_bg(keyword, accent_hex, slide_index)
        else:
            return self._pattern_bg(keyword, accent_hex, slide_index)

    def auto_select(
        self,
        *,
        keyword: str = "",
        accent_hex: str = "#0015ff",
        slide_index: int = 0,
        prefer_photo: bool = True,
    ) -> BgResult:
        """Auto-select the best background type based on available info."""
        # Default: gradient for most slides, photo for hero/cover pages
        if prefer_photo and keyword:
            return self._photo_bg(keyword, slide_index)
        return self._gradient_bg(keyword, accent_hex, slide_index)

    # ── Photo backgrounds ──

    def _photo_bg(self, keyword: str, slide_index: int,
                  width: int = 1280, height: int = 720) -> BgResult:
        """Get a keyword-themed photo from Picsum."""
        seed = self._keyword_seed(keyword, slide_index)
        url = f"{self.PICSUM}/seed/{seed}/{width}/{height}"

        css = (
            f"background-image: url({url});"
            f"background-size: cover;"
            f"background-position: center;"
        )
        overlay = (
            "background: linear-gradient("
            "180deg, rgba(0,0,0,0.35) 0%, rgba(0,0,0,0.15) 50%, rgba(0,0,0,0.45) 100%"
            ");"
        )
        return BgResult(css=css, overlay=overlay, source=f"picsum/{seed}")

    def get_photo_url(self, keyword: str, slide_index: int = 0,
                      width: int = 1280, height: int = 720) -> str:
        """Get just a photo URL for use as img src / background-image."""
        seed = self._keyword_seed(keyword, slide_index)
        return f"{self.PICSUM}/seed/{seed}/{width}/{height}"

    # ── Gradient backgrounds ──

    def _gradient_bg(self, keyword: str, accent_hex: str,
                     slide_index: int) -> BgResult:
        """Select a curated gradient matching the keyword mood."""
        mood = self._detect_mood(keyword)
        candidates = GRADIENT_TAGS.get(mood, GRADIENT_TAGS["elegant"])
        idx = slide_index % len(candidates)
        gradient_name = candidates[idx]
        gradient_css = GRADIENTS[gradient_name]

        css = f"background: {gradient_css};"
        return BgResult(css=css, overlay="", source=f"gradient/{gradient_name}")

    def get_gradient(self, name_or_index) -> str:
        """Get a specific gradient by name or fallback to index-based."""
        if name_or_index in GRADIENTS:
            return GRADIENTS[name_or_index]
        names = list(GRADIENTS.keys())
        idx = hash(str(name_or_index)) % len(names)
        return GRADIENTS[names[idx]]

    def list_gradients_by_tag(self, tag: str) -> list[str]:
        """List gradient names for a given mood tag."""
        return GRADIENT_TAGS.get(tag, GRADIENT_TAGS["elegant"])

    # ── Pattern backgrounds ──

    def _pattern_bg(self, keyword: str, accent_hex: str,
                    slide_index: int) -> BgResult:
        """Create a subtle SVG pattern background."""
        mood = self._detect_mood(keyword)
        pattern_names = {
            "tech": "grid", "business": "diagonal", "nature": "wave",
            "city": "grid", "creative": "dots", "science": "hexagon",
            "people": "dots", "product": "diagonal", "education": "cross",
            "health": "wave",
        }
        pattern_name = pattern_names.get(mood, "dots")
        svg = SVG_PATTERNS[pattern_name].format(color=accent_hex.lstrip("#"))
        # URL-encode SVG for CSS
        encoded = svg.replace("#", "%23").replace("<", "%3C").replace(">", "%3E").replace('"', "'")
        css = (
            f"background-color: var(--bg, #ffffff);"
            f"background-image: url(\"data:image/svg+xml,{encoded}\");"
            f"background-repeat: repeat;"
        )
        return BgResult(css=css, overlay="", source=f"pattern/{pattern_name}")

    # ── Keyword helpers ──

    def _detect_mood(self, keyword: str) -> str:
        """Detect mood/tag from a keyword string."""
        if not keyword:
            return "elegant"
        kw = keyword.lower()
        for mood, words in PHOTO_MOODS.items():
            for w in words:
                if w in kw:
                    return mood
        # Fallback: hash-based
        moods = list(GRADIENT_TAGS.keys())
        return moods[hash(kw) % len(moods)]

    def extract_keyword(self, title: str = "", body: str = "",
                        bullet_points: list | None = None) -> str:
        """Extract the best background keyword from slide content."""
        # Use title words first, then body
        parts = []
        if title:
            parts.append(title)
        if body:
            parts.append(body[:100])
        if bullet_points:
            parts.append(" ".join(bullet_points[:3]))
        combined = " ".join(parts)

        # Simple keyword extraction: take meaningful words
        # Remove common stop words
        stop_words = {"的", "是", "在", "和", "了", "有", "个", "为", "与",
                      "the", "a", "an", "is", "are", "was", "were", "in", "on",
                      "at", "to", "for", "of", "with", "and", "or", "by"}
        words = [w for w in combined.replace(",", " ").replace("、", " ").split()
                 if len(w) > 1 and w.lower() not in stop_words]

        if not words:
            return "abstract modern"

        # Return the 2-3 most meaningful words
        return " ".join(words[:3])

    def _keyword_seed(self, keyword: str, slide_index: int) -> int:
        """Generate a stable numeric seed from keyword + slide index."""
        raw = f"{keyword}-{slide_index}"
        return int(hashlib.md5(raw.encode()).hexdigest()[:8], 16) % 1000

    def generate_slide_backgrounds(
        self,
        slides: list,
        bg_type: BgType = BgType.GRADIENT,
        accent_hex: str = "#0015ff",
    ) -> list[BgResult]:
        """Generate backgrounds for all slides in one pass."""
        results = []
        for i, slide in enumerate(slides):
            keyword = self.extract_keyword(
                title=getattr(slide, "title", "") or "",
                body=getattr(slide, "body", "") or "",
                bullet_points=getattr(slide, "bullet_points", None),
            )
            if bg_type == BgType.PHOTO and getattr(slide, "image_placeholder", None):
                keyword = slide.image_placeholder or keyword

            results.append(self.get_background(
                bg_type,
                keyword=keyword,
                accent_hex=accent_hex,
                slide_index=i,
            ))
        return results
