"""
Enhanced Theme System with Modern Design Theory
Comprehensive theme specifications for CCUI
"""

from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class ThemeSpec:
    """Theme specification with design theory backing"""
    name: str
    description: str
    use_cases: List[str]
    target_audience: str
    design_philosophy: str
    visual_characteristics: Dict[str, Any]
    accessibility_priority: str
    implementation_notes: str

# Enhanced Theme System based on Modern Design Theory
THEME_SPECIFICATIONS = {
    "minimal": ThemeSpec(
        name="Minimal",
        description="Clean, content-focused design rooted in Dieter Rams' principles of clarity and function.",
        use_cases=[
            "B2B SaaS platforms",
            "Professional services",
            "Documentation sites",
            "Portfolio websites"
        ],
        target_audience="Efficiency-driven professionals who value clarity over decoration",
        design_philosophy="Less but better – eliminate non-essential elements, elevate hierarchy",
        visual_characteristics={
            "color_palette": "Neutral monochrome with restrained single accent",
            "typography": "System and modern sans-serif (Inter, SF Pro) for legibility",
            "spacing": "Generous whitespace, strict 8pt grid rhythm",
            "components": "Flat surfaces, hairline borders, subtle elevation (no skeuomorphism)",
            "interactions": "Micro-hover cues, restrained transitions (opacity/fade only)",
            "layout": "Grid-first, wide margins, plenty of negative space"
        },
        accessibility_priority="AAA target – strict readability and contrast across breakpoints",
        implementation_notes="Use fluid type scales, responsive whitespace, avoid decorative overload"
    ),

    "brutalist": ThemeSpec(
        name="Brutalist",
        description="Raw, bold design inspired by Brutalist architecture – uncompromising and experimental.",
        use_cases=[
            "Creative agencies",
            "Art portfolios",
            "Experimental products",
            "Bold brand statements"
        ],
        target_audience="Design-forward users seeking unconventional, striking aesthetics",
        design_philosophy="Raw materials, geometric intensity, deliberate visual discomfort",
        visual_characteristics={
            "color_palette": "High-contrast black/white with primary or neon accent",
            "typography": "Heavy sans-serif (Helvetica Bold, Arial Black)",
            "spacing": "Dense, overlapping, deliberate grid breaks",
            "components": "Hard edges, thick borders, no rounded corners",
            "interactions": "Abrupt state changes, instant feedback (no easing)",
            "layout": "Asymmetrical, overlapping blocks, raw visual stacking"
        },
        accessibility_priority="AA target – maintain legibility despite high-contrast extremes",
        implementation_notes="Use system fonts at heavy weights, avoid gradients, embrace harsh edges"
    ),

    "playful": ThemeSpec(
        name="Playful",
        description="Joyful, approachable design with vibrant colors and organic forms.",
        use_cases=[
            "Consumer apps",
            "Children's products",
            "Entertainment platforms",
            "Creative tools"
        ],
        target_audience="Consumers seeking delight, warmth, and engaging experiences",
        design_philosophy="Design should spark joy and emotional connection through whimsy",
        visual_characteristics={
            "color_palette": "Bright, saturated primaries with multi-color gradients",
            "typography": "Rounded sans (Circular, Nunito) with playful weight variations",
            "spacing": "Organic spacing, non-uniform padding",
            "components": "Rounded corners, gradient fills, soft shadows",
            "interactions": "Bouncy micro-animations, spring physics",
            "layout": "Fluid, circular and curved motifs"
        },
        accessibility_priority="AA target – careful management of bright color contrast",
        implementation_notes="Use CSS custom properties for color variations, implement spring-based motion"
    ),

    "corporate": ThemeSpec(
        name="Corporate",
        description="Trust-focused design using established business conventions and conservative styling.",
        use_cases=[
            "Financial services",
            "Healthcare",
            "Government",
            "Enterprise software"
        ],
        target_audience="Business professionals who require signals of reliability and authority",
        design_philosophy="Familiar patterns that convey competence, hierarchy, and trust",
        visual_characteristics={
            "color_palette": "Blue-dominant, conservative secondary palette",
            "typography": "Serif + sans pairings (Georgia, Arial)",
            "spacing": "Consistent grid, proportional margins",
            "components": "Conventional buttons, structured form layouts",
            "interactions": "Predictable, subtle transitions",
            "layout": "Formal hierarchy, left-to-right reading emphasis"
        },
        accessibility_priority="AA compliance minimum across corporate branding colors",
        implementation_notes="Follow established UI patterns, prioritize clarity over novelty"
    ),

    "morphism": ThemeSpec(
        name="Morphism",
        description="Soft, tactile UI blending neumorphism and glassmorphism principles.",
        use_cases=[
            "Mobile apps",
            "Design portfolios",
            "Premium products",
            "UI/UX showcases"
        ],
        target_audience="Design enthusiasts and premium product users",
        design_philosophy="Digital tactility – UI elements that appear touchable and layered",
        visual_characteristics={
            "color_palette": "Muted pastels with depth gradients",
            "typography": "Rounded sans (SF Pro, Poppins)",
            "spacing": "Generous padding for tactile touch targets",
            "components": "Inset/outset shadows, frosted glass backgrounds",
            "interactions": "Depth-shift on press, soft scaling",
            "layout": "Layered elements floating in depth"
        },
        accessibility_priority="AA target – ensure glass overlays maintain readable contrast",
        implementation_notes="Use multi-layer box-shadows, CSS backdrop-filter, avoid overuse of blur"
    ),

    "animated": ThemeSpec(
        name="Animated",
        description="Motion-first design where animation drives narrative and engagement.",
        use_cases=[
            "Interactive storytelling",
            "Product launches",
            "Creative portfolios",
            "Brand experiences"
        ],
        target_audience="Users seeking immersive, dynamic digital experiences",
        design_philosophy="Motion as primary design material – guiding attention and storytelling",
        visual_characteristics={
            "color_palette": "Dynamic, adaptive colors shifting with user input",
            "typography": "Variable and web fonts optimized for motion",
            "spacing": "Fluid spacing responsive to animations",
            "components": "Transformable, stateful UI blocks",
            "interactions": "Scroll-triggered scenes, choreographed transitions",
            "layout": "Scene-based transformations instead of static layouts"
        },
        accessibility_priority="AA target – respect prefers-reduced-motion for accessibility",
        implementation_notes="Use CSS/JS motion frameworks, optimize for GPU performance, support motion toggles"
    ),

    "terminal": ThemeSpec(
        name="Terminal",
        description="CLI-inspired design with monospace typography and retro computing aesthetics.",
        use_cases=[
            "Developer tools",
            "Technical documentation",
            "API platforms",
            "Hacker/security tools"
        ],
        target_audience="Developers, sysadmins, and tech-savvy audiences",
        design_philosophy="Lean into the nostalgia and efficiency of terminal interfaces",
        visual_characteristics={
            "color_palette": "Dark background with neon green/amber text",
            "typography": "Strict monospace (Fira Code, JetBrains Mono)",
            "spacing": "Character-grid spacing (ch units)",
            "components": "ASCII-art, code block metaphors",
            "interactions": "Typewriter effects, blinking cursors",
            "layout": "Terminal-window inspired fixed-width layouts"
        },
        accessibility_priority="High-contrast defaults, screen reader-friendly semantics",
        implementation_notes="Use CSS ch units for grid, typewriter animations, support ASCII visuals"
    ),

    "aesthetic": ThemeSpec(
        name="Aesthetic",
        description="Retro-futuristic design blending Y2K, vaporwave, and cyber nostalgia with modern UX.",
        use_cases=[
            "Creative platforms",
            "Music & entertainment",
            "Fashion brands",
            "Art communities"
        ],
        target_audience="Gen Z and millennials drawn to digital nostalgia and cyberculture",
        design_philosophy="Reinterpret nostalgic aesthetics with usability-focused design",
        visual_characteristics={
            "color_palette": "Dark navy/black with neon accents (cyan, magenta, electric blue)",
            "typography": "Retro-inspired but legible fonts (bold sans with neon glow)",
            "spacing": "Structured grid softened with retro visuals",
            "components": "Outlined neon UI, glowing buttons",
            "interactions": "Subtle neon glows, hover pulses",
            "layout": "Dark theme with vibrant accent-driven hierarchy"
        },
        accessibility_priority="AA target – maintain 4.5:1 contrast despite neon styling",
        implementation_notes="Always test neon contrasts on dark, ensure glow effects never replace contrast"
    ),

    "dark": ThemeSpec(
        name="Dark",
        description="Modern dark theme optimized for reduced eye strain and immersive focus.",
        use_cases=[
            "Developer tools",
            "Creative portfolios",
            "Entertainment platforms",
            "Productivity apps"
        ],
        target_audience="Night users, developers, gamers, and professionals",
        design_philosophy="Focus attention on content by minimizing luminance and maximizing contrast",
        visual_characteristics={
            "color_palette": "Deep grays/blacks with sharp accent colors (teal, purple, green)",
            "typography": "Readable sans (Inter, Roboto)",
            "spacing": "Balanced negative space for readability on dark",
            "components": "High-contrast CTAs, glowing outlines, subtle shadows",
            "interactions": "Smooth fades, glow hover states",
            "layout": "Content-forward with accent highlights"
        },
        accessibility_priority="AA target – maintain 4.5:1 contrast minimum",
        implementation_notes="Avoid mid-gray on dark, validate all text/background ratios"
    ),

    "vibrant": ThemeSpec(
        name="Vibrant",
        description="High-energy theme using bold colors and gradients to energize interactions.",
        use_cases=[
            "Marketing websites",
            "Consumer products",
            "Music apps",
            "Startups"
        ],
        target_audience="Younger, casual users who seek stimulation and excitement",
        design_philosophy="Color as emotion – bold hues designed to energize and engage",
        visual_characteristics={
            "color_palette": "Dopamine-rich gradients (purple-pink, orange-teal)",
            "typography": "Expressive, bold sans (Montserrat, Gilroy)",
            "spacing": "Dynamic asymmetry with active negative space",
            "components": "Gradient-filled CTAs, shadow pops",
            "interactions": "Gradient shifts, hover glows, micro-transitions",
            "layout": "Hero-first design with strong CTA emphasis"
        },
        accessibility_priority="AA target – ensure text legibility over bright backgrounds",
        implementation_notes="Validate gradient legibility, avoid oversaturation, layer dark overlays when needed"
    ),

    "sustainable": ThemeSpec(
        name="Sustainable",
        description="Nature-inspired design using earth tones and calm layouts for eco-conscious branding.",
        use_cases=[
            "Environmental organizations",
            "Eco-products",
            "Sustainable brands",
            "Wellness platforms"
        ],
        target_audience="Eco-conscious consumers and brands prioritizing sustainability",
        design_philosophy="Calm, grounded design that reflects environmental values",
        visual_characteristics={
            "color_palette": "Greens, browns, and muted naturals",
            "typography": "Organic, humanist fonts (Lora, Poppins)",
            "spacing": "Generous whitespace for light, airy feel",
            "components": "Soft corners, textures, nature-inspired motifs",
            "interactions": "Smooth fades, natural flow animations",
            "layout": "Grounded grid with breathing room"
        },
        accessibility_priority="AA target – ensure muted colors still pass contrast",
        implementation_notes="Avoid neon greens, prioritize muted natural palettes, always test color contrast"
    ),

    "data": ThemeSpec(
        name="Data",
        description="Dense, information-rich theme designed for analytics and dashboards.",
        use_cases=[
            "Analytics dashboards",
            "Finance apps",
            "Enterprise SaaS",
            "Developer tools"
        ],
        target_audience="Analysts, engineers, and decision-makers who need clarity at scale",
        design_philosophy="Clarity and efficiency in communicating large datasets",
        visual_characteristics={
            "color_palette": "Neutral grays with strong accent colors for charts",
            "typography": "Readable sans (Roboto, IBM Plex Sans)",
            "spacing": "Tight, grid-aligned spacing for density",
            "components": "Tables, charts, modular cards",
            "interactions": "Hover tooltips, interactive filters, smooth sorting",
            "layout": "Modular grid optimized for scanning data"
        },
        accessibility_priority="AAA target – clarity and colorblind-safe palette",
        implementation_notes="Validate chart colorblind safety, provide text equivalents for visualizations"
    ),

    "illustrated": ThemeSpec(
        name="Illustrated",
        description="Hand-drawn, character-driven design that emphasizes warmth and personality.",
        use_cases=[
            "Creative startups",
            "Onboarding flows",
            "Educational platforms",
            "Community websites"
        ],
        target_audience="Students, casual users, and creative professionals",
        design_philosophy="Humanize digital experiences with illustration as storytelling",
        visual_characteristics={
            "color_palette": "Soft pastels with vibrant accent pops",
            "typography": "Rounded, friendly fonts (Nunito, Quicksand)",
            "spacing": "Organic spacing around illustrations",
            "components": "Illustration-driven CTAs, custom iconography",
            "interactions": "Playful onboarding animations, micro-delight",
            "layout": "Centered, narrative-driven structures"
        },
        accessibility_priority="AA target – do not rely solely on illustration for meaning",
        implementation_notes="Use lightweight SVGs, consider Lottie for animated illustrations"
    )
}

def get_theme_design_system_rules(theme_name: str) -> str:
    """Generate theme-specific design system rules for prompts"""
    if theme_name not in THEME_SPECIFICATIONS:
        return ""
    
    theme = THEME_SPECIFICATIONS[theme_name]
    
    return f"""
THEME-SPECIFIC DESIGN SYSTEM RULES FOR {theme.name.upper()}:

Philosophy: {theme.design_philosophy}
Target Use: {', '.join(theme.use_cases[:2])}

Visual Requirements:
- Colors: {theme.visual_characteristics['color_palette']}
- Typography: {theme.visual_characteristics['typography']}
- Spacing: {theme.visual_characteristics['spacing']}
- Components: {theme.visual_characteristics['components']}
- Interactions: {theme.visual_characteristics['interactions']}
- Layout: {theme.visual_characteristics['layout']}

Accessibility: {theme.accessibility_priority}
Implementation Notes: {theme.implementation_notes}

CRITICAL: All design tokens must align with these {theme.name} theme characteristics.
"""

def get_theme_choices() -> List[str]:
    """Get all available theme names"""
    return list(THEME_SPECIFICATIONS.keys())

def get_theme_description(theme_name: str) -> str:
    """Get theme description for CLI help"""
    if theme_name not in THEME_SPECIFICATIONS:
        return "Unknown theme"
    
    theme = THEME_SPECIFICATIONS[theme_name]
    return f"{theme.description}"

def detect_theme_from_content(content: str) -> str:
    """Enhanced theme detection from HTML/CSS content with priority-based scoring"""
    content_lower = content.lower()
    
    # Specific theme patterns with higher priority checks first
    
    # 1. Brutalist (check before dark theme since both use bg-black)
    brutalist_score = 0
    if 'brutalist-border' in content_lower: brutalist_score += 10
    if 'brutalist-shadow' in content_lower: brutalist_score += 10
    if 'font-black' in content_lower: brutalist_score += 5
    if 'font-bold uppercase' in content_lower: brutalist_score += 3
    if 'bg-red-600' in content_lower and 'bg-yellow-400' in content_lower: brutalist_score += 5
    if 'jetbrains mono' in content_lower: brutalist_score += 3
    
    # 2. Morphism
    morphism_score = 0
    if 'backdrop-filter' in content_lower: morphism_score += 10
    if 'glassmorphism' in content_lower: morphism_score += 10
    if 'neumorphism' in content_lower: morphism_score += 10
    if 'bg-white/20' in content_lower or 'bg-opacity-' in content_lower: morphism_score += 5
    
    # 3. Terminal
    terminal_score = 0
    if 'font-mono' in content_lower: terminal_score += 5
    if 'text-green-400' in content_lower or 'text-green-500' in content_lower: terminal_score += 5
    if 'border-green-500' in content_lower: terminal_score += 5
    if 'animate-pulse' in content_lower and 'green' in content_lower: terminal_score += 3
    if 'terminal' in content_lower: terminal_score += 3
    
    # 4. Playful
    playful_score = 0
    if 'rounded-xl' in content_lower or 'rounded-2xl' in content_lower: playful_score += 5
    if 'bg-pink-' in content_lower or 'bg-purple-' in content_lower: playful_score += 5
    if 'hover:scale-' in content_lower: playful_score += 3
    if 'gradient' in content_lower and ('pink' in content_lower or 'purple' in content_lower): playful_score += 5
    
    # 5. Corporate
    corporate_score = 0
    if 'bg-blue-900' in content_lower or 'bg-blue-800' in content_lower: corporate_score += 5
    if 'shadow-lg' in content_lower or 'shadow-xl' in content_lower: corporate_score += 3
    if 'corporate' in content_lower or 'professional' in content_lower: corporate_score += 5
    
    # 6. Dark theme (check after brutalist to avoid conflicts)
    dark_score = 0
    if ('dark' in content_lower and 'theme' in content_lower): dark_score += 10
    if 'bg-gray-900' in content_lower: dark_score += 5
    if 'text-gray-100' in content_lower or 'text-white' in content_lower: dark_score += 3
    if 'border-gray-700' in content_lower: dark_score += 3
    
    # Return theme with highest score
    scores = {
        'brutalist': brutalist_score,
        'morphism': morphism_score,
        'terminal': terminal_score,
        'playful': playful_score,
        'corporate': corporate_score,
        'dark': dark_score
    }
    
    # Get theme with highest score (minimum threshold of 5)
    max_theme = max(scores, key=scores.get)
    if scores[max_theme] >= 5:
        return max_theme
    
    # Fallback patterns for other themes
    if 'neon' in content_lower or 'cyber' in content_lower or 'retro' in content_lower:
        return 'aesthetic'
    elif 'vibrant' in content_lower or 'dopamine' in content_lower:
        return 'vibrant'
    elif 'sustainable' in content_lower or 'eco' in content_lower:
        return 'sustainable'
    elif 'data' in content_lower or 'dashboard' in content_lower or 'analytics' in content_lower:
        return 'data'
    elif 'illustrated' in content_lower or 'illustration' in content_lower:
        return 'illustrated'
    elif 'animation' in content_lower and ('transform' in content_lower or 'keyframes' in content_lower):
        return 'animated'
    else:
        return 'minimal'