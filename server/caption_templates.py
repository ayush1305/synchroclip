# CapCut-style Caption Templates & Styles

TEMPLATES = {
    "capcut_classic": {
        "id": "capcut_classic",
        "name": "CapCut Classic / Hormozi",
        "category": "Trending",
        "fontname": "Montserrat, Arial Black, Impact, sans-serif",
        "fontsize": 68,
        "primary_color": "&H00FFFFFF",      # White (AABBGGRR)
        "secondary_color": "&H0000FFFF",    # Bright Yellow
        "outline_color": "&H00000000",      # Black
        "back_color": "&H80000000",         # Soft shadow
        "bold": 1,
        "italic": 0,
        "outline": 4.5,
        "shadow": 2.5,
        "alignment": 2,                     # Bottom-center
        "margin_v": 80,
        "animation": "bounce",
        "badge": "Trending",
        "preview_text": "THE QUICK BROWN FOX",
        "preview_highlight": "QUICK"
    },
    "neon_fox": {
        "id": "neon_fox",
        "name": "Neon Magenta & Cyan",
        "category": "Glow",
        "fontname": "Montserrat, Arial Black, Trebuchet MS",
        "fontsize": 72,
        "primary_color": "&H00FFFFFF",      # White
        "secondary_color": "&H00FF00EA",    # Neon Magenta / Pink
        "outline_color": "&H00FF5500",      # Neon Blue/Cyan edge
        "back_color": "&H00D400FF",         # Purple glow
        "bold": 1,
        "italic": 0,
        "outline": 3.0,
        "shadow": 6.0,
        "alignment": 2,
        "margin_v": 85,
        "animation": "glow_pulse",
        "badge": "Pro",
        "preview_text": "NEON FOX GLOW",
        "preview_highlight": "FOX"
    },
    "red_fire": {
        "id": "red_fire",
        "name": "Red Fire Glow",
        "category": "Glow",
        "fontname": "Arial Black, Impact, sans-serif",
        "fontsize": 70,
        "primary_color": "&H000015FF",      # Red-Orange glow
        "secondary_color": "&H0000FFFF",    # Fiery Yellow highlight
        "outline_color": "&H00000088",      # Dark Crimson outline
        "back_color": "&H000000FF",         # Deep Red aura
        "bold": 1,
        "italic": 0,
        "outline": 4.0,
        "shadow": 5.0,
        "alignment": 2,
        "margin_v": 80,
        "animation": "fire_pulse",
        "badge": "Pro",
        "preview_text": "THE QUICK FIRE",
        "preview_highlight": "QUICK"
    },
    "cinematic_serif": {
        "id": "cinematic_serif",
        "name": "Cinematic Editorial Serif",
        "category": "Serif",
        "fontname": "Georgia, Times New Roman, serif",
        "fontsize": 62,
        "primary_color": "&H00FFFFFF",      # Pure White
        "secondary_color": "&H00E0FFFF",    # Luminous Cyan-White
        "outline_color": "&H00111111",      # Subtle dark outline
        "back_color": "&H60000000",         # Soft aura
        "bold": 0,
        "italic": 1,
        "outline": 2.0,
        "shadow": 3.0,
        "alignment": 2,
        "margin_v": 90,
        "animation": "smooth_fade",
        "badge": "Pro",
        "preview_text": "The quick brown fox",
        "preview_highlight": "brown"
    },
    "word_pop": {
        "id": "word_pop",
        "name": "Word Pop / Single Focus",
        "category": "Word",
        "fontname": "Impact, Arial Black, Montserrat",
        "fontsize": 90,
        "primary_color": "&H00FFFFFF",
        "secondary_color": "&H0000E5FF",    # Amber Yellow Pop
        "outline_color": "&H00000000",
        "back_color": "&H90000000",
        "bold": 1,
        "italic": 0,
        "outline": 6.0,
        "shadow": 4.0,
        "alignment": 5,                     # Middle center
        "margin_v": 0,
        "animation": "word_zoom",
        "badge": "Pro",
        "preview_text": "QUICK",
        "preview_highlight": "QUICK"
    },
    "minimal_monoline": {
        "id": "minimal_monoline",
        "name": "Minimal Monoline",
        "category": "Monoline",
        "fontname": "Segoe UI, Inter, Helvetica, sans-serif",
        "fontsize": 54,
        "primary_color": "&H00F0F0F0",
        "secondary_color": "&H0080FF00",    # Toxic Green highlight
        "outline_color": "&H00101010",
        "back_color": "&HAA000000",         # Translucent pill backing
        "bold": 0,
        "italic": 0,
        "outline": 1.5,
        "shadow": 1.0,
        "alignment": 2,
        "margin_v": 70,
        "animation": "clean",
        "badge": "Pro",
        "preview_text": "The quick monoline",
        "preview_highlight": "monoline"
    },
    "none": {
        "id": "none",
        "name": "No Captions (Clean Video)",
        "category": "Trending",
        "fontname": "",
        "fontsize": 0,
        "primary_color": "",
        "secondary_color": "",
        "outline_color": "",
        "back_color": "",
        "bold": 0,
        "italic": 0,
        "outline": 0,
        "shadow": 0,
        "alignment": 2,
        "margin_v": 0,
        "animation": "none",
        "badge": "Clean",
        "preview_text": "Clean footage without subtitles",
        "preview_highlight": ""
    }
}

# Color palette for active word highlighting
HIGHLIGHT_COLORS = {
    "yellow": {"name": "Neon Yellow", "hex": "#facc15", "ass": "&H0000FFFF&"},
    "green": {"name": "Toxic Green", "hex": "#4ade80", "ass": "&H0000FF00&"},
    "cyan": {"name": "Electric Cyan", "hex": "#38bdf8", "ass": "&H00FFFF00&"},
    "pink": {"name": "Hot Magenta", "hex": "#f43f5e", "ass": "&H00FF00EA&"},
    "orange": {"name": "Fiery Orange", "hex": "#fb923c", "ass": "&H000088FF&"},
    "white": {"name": "Luminous White", "hex": "#ffffff", "ass": "&H00FFFFFF&"}
}

def get_template(template_id: str) -> dict:
    return TEMPLATES.get(template_id, TEMPLATES["capcut_classic"])

def build_ass_header(template_id: str, width: int = 1920, height: int = 1080) -> str:
    tpl = get_template(template_id)
    if tpl["id"] == "none":
        return ""

    header = f"""[Script Info]
Title: SynchroClip Dynamic Subtitles
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709
PlayResX: {width}
PlayResY: {height}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{tpl['fontname']},{tpl['fontsize']},{tpl['primary_color']},{tpl['secondary_color']},{tpl['outline_color']},{tpl['back_color']},{tpl['bold']},{tpl['italic']},0,0,100,100,0,0,1,{tpl['outline']},{tpl['shadow']},{tpl['alignment']},40,40,{tpl['margin_v']},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    return header
