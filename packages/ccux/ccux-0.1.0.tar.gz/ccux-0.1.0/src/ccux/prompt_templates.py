
from textwrap import dedent
import os
from typing import List, Tuple, Dict

# Import theme specifications for theme-aware prompts
try:
    from .theme_specifications import get_theme_design_system_rules
except ImportError:
    # Fallback if theme_specifications not available
    def get_theme_design_system_rules(theme_name: str) -> str:
        return f"Generate design system for {theme_name} theme."

def reference_discovery_prompt(desc: str) -> str:
    return f"Given this product: '{desc}', find 3 live product URLs of similar tools. Only list working websites, not blogs. Format: Name – URL – short note."


def deep_product_understanding_prompt(desc: str) -> str:
    return f'JSON analysis of product: {desc}\n{{"problem":"Core issue","user":"Who needs it","differentiator":"Why not existing","best_feature":"Most loved","risks":"Possible failure reasons"}}\nRules: Be concise, no fluff, focus on user pain.'


def ux_analysis_prompt(product_desc: str, refs: List[str]) -> str:
    refs_text = "\n".join(
        f"- {screenshot_path.split('/')[-1]}" for screenshot_path in refs
    )

    return f'''UX competitive analysis of: {product_desc}

Read and analyze the following screenshots for UX patterns:
{refs_text}

Respond in JSON:
{{
  "patterns": {{
    "navigation": ["..."],
    "ctas": ["..."],
    "layouts": ["..."],
    "messaging": ["..."]
  }},
  "differentiators": [{{"screenshot":"...","element":"...","why":"..."}}],
  "weaknesses": {{
    "common": ["..."],
    "severe": ["..."]
  }},
  "recommendations": {{
    "adopt": ["..."],
    "avoid": ["..."],
    "innovate": ["..."]
  }},
  "summary": "1-2 sentence takeaway"
}}
Rules: Be concise, specific, mobile-first.'''


def empathize_prompt(product_desc: str, product_understanding: Dict, ux_analysis: Dict) -> str:
    short_problem = str(product_understanding.get("problem", "N/A"))[:200]
    short_user = str(product_understanding.get("user", "N/A"))[:200]
    short_diff = str(product_understanding.get("differentiator", "N/A"))[:200]
    
    nav_patterns = ux_analysis.get("patterns", {}).get("navigation", [])
    adopt = ux_analysis.get("recommendations", {}).get("adopt", [])
    avoid = ux_analysis.get("recommendations", {}).get("avoid", [])
    return f'''Product: {product_desc}

Understanding (trimmed):
- Problem: {short_problem}
- User: {short_user}
- Differentiator: {short_diff}

UX Insights:
- Navigation patterns: {nav_patterns}
- Adopt: {adopt}
- Avoid: {avoid}

Output JSON only:
{{
  "context": {{
    "device": "...",
    "channels": ["...", "...", "..."],
    "immediate_need": "..."
  }},
  "questions": {{
    "identity": ["...", "..."],
    "value": ["...", "..."],
    "trust": ["...", "..."]
  }},
  "conversion": {{
    "primary": "...",
    "secondary": ["...", "..."],
    "required_info": ["...", "..."]
  }},
  "personas": [
    {{
      "name": "...",
      "role": "...",
      "urgency": "...",
      "decision_process": "...",
      "content_needs": ["...", "..."]
    }}
  ],
  "touchpoints": {{
    "first_impression": "...",
    "dropoff_risk": "...",
    "persuasive_element": "..."
  }},
  "research_gaps": ["...", "..."]
}}
Rules: Be concise, quote user questions, focus on behaviors.'''


def define_prompt(product_desc, user_research) -> str:
    return f'''Product: {product_desc}

Research:
- Goal: {user_research.get("conversion",{}).get("primary","N/A")}
- Context: {user_research.get("context",{}).get("immediate_need","N/A")}
- Questions: {user_research.get("questions",{}).get("value",[])}
- Personas: {[p.get("name","N/A")+" ("+p.get("role","")+")" for p in user_research.get("personas",[])]}

Output JSON only:
{{
  "core_pages": {{
    "homepage": {{"job":"...","must_show":["...","..."],"next_step":"..."}},
    "key_secondary": [{{"page":"...","job":"...","exit_risk":"...","recovery":"..."}}]
  }},
  "primary_flow": {{
    "steps":["...","...","..."],
    "dropoff_points":["...","..."],
    "support_elements":["...","..."]
  }},
  "alternate_paths": {{
    "price_concerns":"...",
    "trust_issues":"...",
    "feature_questions":"..."
  }},
  "navigation": {{
    "global_nav":["...","...","..."],
    "mobile_priority":"...",
    "footer_strategy":"..."
  }},
  "conflicts":["...","..."],
  "research_gaps":["...","..."]
}}
Rules: Be concrete, use UI elements, flag conflicts, note missing research.'''

def ideate_prompt(product_desc, user_research, site_flow) -> str:
    return f'''Product: {product_desc}

Research:
- Goal: {user_research.get("conversion",{}).get("primary","N/A")}
- Questions: {user_research.get("questions",{}).get("value",[])}
- Homepage Must Show: {site_flow.get("core_pages",{}).get("homepage",{}).get("must_show",[])}
- Primary Flow: {site_flow.get("primary_flow",{}).get("steps",[])}

Output JSON only:
{{
  "core_messaging": {{
    "value_proposition": "...",
    "unique_angle": "..."
  }},
  "hero": {{
    "headline": "...",
    "subhead": "...",
    "primary_cta": "...",
    "supporting_element": "..."
  }},
  "benefits": [
    {{"headline":"...","proof_point":"...","icon_concept":"..."}},
    {{"headline":"...","proof_point":"...","icon_concept":"..."}},
    {{"headline":"...","proof_point":"...","icon_concept":"..."}}
  ],
  "objections": {{
    "top_3_concerns": ["...","...","..."],
    "faq_answers": [{{"question":"...","answer":"..."}}],
    "trust_elements": ["...","..."]
  }},
  "ctas": {{
    "primary_action":"...",
    "secondary_action":"...",
    "microcopy":"..."
  }},
  "rules": {{
    "tone":"...",
    "avoid":["...","..."],
    "must_include":["...","..."]
  }}
}}
Rules: Be concise, outcome-focused, use real user wording where possible.'''

def wireframe_prompt(product_desc, content_strategy, site_flow) -> str:
    return f'''Product: {product_desc}

Content:
- Hero: {content_strategy.get("hero",{}).get("headline","N/A")}
- Benefits: {[b.get("headline","N/A") for b in content_strategy.get("benefits",[])]}
- CTA: {content_strategy.get("ctas",{}).get("primary_action","N/A")}

Flow:
- Pages: {list(site_flow.get("core_pages",{}).keys())}
- Nav Priority: {site_flow.get("navigation",{}).get("mobile_priority","N/A")}

Output JSON only:
{{
  "layout": {{
    "sections": [
      {{"name":"hero","elements":["..."],"mobile_stack":["..."],"priority":"..."}},
      {{"name":"benefits","elements":["..."],"mobile_stack":["..."],"priority":"..."}}
    ]
  }},
  "mobile_checks": {{
    "critical":["...","...","..."],
    "red_flags":["...","..."]
  }},
  "interactions": {{
    "key":[{{"element":"...","behavior":"...","mobile_consideration":"..."}}]
  }},
  "responsive": {{
    "breakpoints": {{
      "mobile": {{"rules":["...","..."]}},
      "tablet": {{"rules":["...","..."]}}
    }}
  }}
}}
Rules: Be concise, mobile-first, ensure CTA always visible.'''


def design_system_prompt(product_desc, wireframes, content_strategy, theme: str = "minimal") -> str:
    return f'''Product: {product_desc}

Wireframes:
- Sections: {[s.get("name","N/A") for s in wireframes.get("layout",{}).get("sections",[])]}
- Mobile Checks: {wireframes.get("mobile_checks",{}).get("critical",[])}

Tone: {content_strategy.get("rules",{}).get("tone","Professional")}

Output JSON only:
{{
  "typography": {{
    "typeface_choice": "...",
    "brand_rationale": "...",
    "heading_hierarchy": {{"h1":"...","h2":"...","h3":"..."}},
    "body_text": "..."
  }},
  "color_tokens": {{
    "primary":"#...","primary_light":"#...","primary_dark":"#...",
    "secondary":"#...","accent":"#...","surface":"#...","background":"#...",
    "success":"#...","warning":"#...","error":"#...",
    "text_primary":"#...","text_secondary":"#...","text_muted":"#...",
    "border":"#...","border_light":"#...","shadow":"#..."
  }},
  "gradients": {{
    "primary_gradient":"linear-gradient(135deg, #... 0%, #... 100%)",
    "hero_gradient":"linear-gradient(180deg, #... 0%, #... 100%)",
    "card_gradient":"linear-gradient(145deg, #... 0%, #... 100%)",
    "button_gradient":"linear-gradient(135deg, #... 0%, #... 100%)"
  }},
  "shadows": {{
    "card_shadow":"0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06)",
    "button_shadow":"0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -2px rgba(0,0,0,0.05)",
    "hover_shadow":"0 20px 25px -5px rgba(0,0,0,0.1), 0 10px 10px -5px rgba(0,0,0,0.04)"
  }},
  "animations": {{
    "duration": {{"fast":"150ms","normal":"300ms","slow":"500ms"}},
    "easing": {{"ease_in":"cubic-bezier(0.4, 0, 1, 1)","ease_out":"cubic-bezier(0, 0, 0.2, 1)","ease_in_out":"cubic-bezier(0.4, 0, 0.2, 1)"}},
    "transforms": {{"scale_hover":"scale(1.05)","scale_click":"scale(0.95)","lift":"translateY(-2px)"}}
  }},
  "wcag_contrast": {{
    "primary_cta":"X.X:1 - PASS/FAIL",
    "body_text":"X.X:1 - PASS/FAIL",
    "secondary_text":"X.X:1 - PASS/FAIL",
    "error_text":"X.X:1 - PASS/FAIL",
    "accessible":"true/false"
  }},
  "signature_elements": [
    {{"element":"...","specification":"...","usage":"..."}},
    {{"element":"...","specification":"...","usage":"..."}}
  ],
  "components": {{
    "buttons": {{
      "primary":{{"default":"...","hover":"...","active":"...","disabled":"...","animation":"transform 300ms ease-out"}},
      "secondary":{{"default":"...","hover":"...","active":"...","disabled":"...","animation":"all 200ms ease-in-out"}},
      "ghost":{{"default":"...","hover":"...","active":"...","disabled":"...","animation":"all 150ms ease-in-out"}}
    }},
    "inputs": {{
      "text_field":{{"default":"...","focus":"...","error":"...","animation":"border-color 200ms ease-in-out"}},
      "select":{{"default":"...","focus":"...","hover":"...","animation":"all 150ms ease-out"}},
      "textarea":{{"default":"...","focus":"...","error":"...","animation":"border-color 200ms ease-in-out"}}
    }},
    "cards": {{
      "content":{{"default":"...","hover":"...","animation":"transform 300ms ease-out, box-shadow 300ms ease-out"}},
      "pricing":{{"default":"...","hover":"...","featured":"...","animation":"transform 200ms ease-in-out"}},
      "testimonial":{{"default":"...","hover":"...","animation":"all 250ms ease-out"}}
    }}
  }},
  "spacing_system": {{"scale":["2px","4px","8px","12px","16px","24px","32px","48px","64px","96px"],"usage":"..."}},
  "border_radius": {{"sm":"4px","md":"8px","lg":"12px","xl":"16px","2xl":"24px","full":"9999px"}},
  "svg_patterns": {{
    "hero_bg":"Complex geometric SVG background pattern with subtle animation",
    "section_divider":"Organic wave or curve SVG divider between sections",
    "decorative_elements":"Abstract shapes, dots, or lines for visual interest"
  }},
  "logo_concept": {{
    "style":"Modern, minimal, geometric/organic",
    "elements":"Icon + wordmark or symbol only",
    "colors":"Uses primary brand colors",
    "usage":"Header, footer, favicon"
  }},
  "summary": "..."
}}

{get_theme_design_system_rules(theme)}

Rules: Modern, animated, gradient-rich, high-contrast, mobile-optimized, includes SVG patterns and logo concept.'''


def high_fidelity_design_prompt(product_desc, design_system, wireframes, content_strategy) -> str:
    return f'''Product: {product_desc}

System:
- Typography: {design_system.get("typography",{}).get("typeface_choice","N/A")}
- Primary Color: {design_system.get("color_tokens",{}).get("primary","N/A")}
- Signature Elements: {[e.get("element","N/A") for e in design_system.get("signature_design_elements",[])]}

Wireframes: {[s.get("name","N/A") for s in wireframes.get("layout",{}).get("sections",[])]}
Tone: {content_strategy.get("rules",{}).get("tone","Professional")}

Output JSON only:
{{
  "design_specifications": {{
    "typography": "...",
    "colors": "...",
    "spacing": "...",
    "components": "..."
  }},
  "interactions": {{
    "hover_states": "...",
    "transitions": "...",
    "responsive": "..."
  }},
  "accessibility": {{
    "contrast": "...",
    "typography": "...",
    "navigation": "..."
  }},
  "implementation_ready": "..."
}}
Rules: Be clean, consistent, accessible, mobile-first.'''


def prototype_prompt(product_desc, content_strategy, design_system, wireframes) -> str:
    return f'''Product: {product_desc}

Content:
- Value Proposition: {content_strategy.get("core_messaging",{}).get("value_proposition","N/A")}
- Hero: {content_strategy.get("hero",{}).get("headline","N/A")}
- CTA: {content_strategy.get("ctas",{}).get("primary_action","N/A")}
- Tone: {content_strategy.get("rules",{}).get("tone","Professional")}

Design:
- Sections: {[s.get("name","N/A") for s in wireframes.get("layout",{}).get("sections",[])]}
- Personality: {design_system.get("typography",{}).get("brand_rationale","Modern and clean")}

Output JSON only:
{{
  "hero": {{"headline":"...","subheadline":"...","cta_primary":"...","cta_secondary":"..."}},
  "problem": {{"headline":"...","description":"...","pain_points":["...","...","..."]}},
  "solution": {{"headline":"...","value_proposition":"...","key_benefits":["...","...","..."]}},
  "features": {{"headline":"...","features":[{{"title":"...","description":"...","benefit":"..."}}]}},
  "social_proof": {{"headline":"...","testimonial":"...","stats":["...","...","..."]}},
  "pricing": {{"headline":"...","plan_name":"...","price":"...","features":["...","..."],"cta":"..."}},
  "footer": {{"cta_headline":"...","cta_description":"...","cta_button":"..."}}
}}
Rules: Use AIDA/PAS style, focus on benefits, strong CTAs, address objections, keep tone consistent.'''

def implementation_prompt(product_description, copy_content, framework, theme, design_data) -> str:
    """Final implementation prompt that consolidates all previous steps"""
    # Extract only what's essential from previous stages
    design_system = design_data.get('design_system', {})
    content_strategy = design_data.get('content_strategy', {})
    ux_analysis = design_data.get('ux_analysis', {})
    
    # Dynamic color handling
    primary_color = design_system.get('color_tokens', {}).get('primary')
    color_context = f"Primary Color: {primary_color}" if primary_color else "Color System: Generate appropriate palette"
    
    # Content highlights
    value_prop = content_strategy.get('core_messaging', {}).get('value_proposition', '')
    primary_cta = content_strategy.get('ctas', {}).get('primary_action', 'Get Started')
    
    return f'''You are a senior product designer implementing the final landing page.

Product: {product_description}
Framework: {framework}
Theme: {theme}

Consolidated Design Inputs:
1. {color_context}
2. Value Proposition: {value_prop[:120]}
3. Primary CTA: {primary_cta}
4. UX Patterns: {ux_analysis.get('recommendations', {}).get('adopt', [])[:2]}

Implementation Rules:
- Start with mobile layout then enhance for desktop
- Make every visual element serve a purpose
- Ensure 1.5s first contentful paint
- Maintain AA accessibility throughout
- Use system-generated assets where needed
- Use SVG icons or icon libraries (Heroicons, Lucide, Feather) instead of emoji characters for professional appearance
- IMPORTANT: When referencing images (reference.jpg, reference_1_*.jpg, etc.), use relative path ../filename.jpg since HTML is in output/landing-page/ but images are in output/

Visual Treatment Guide:
<!-- IMAGE-STRATEGY: [hero-image/product-shot/illustration/none] -->
<!-- ANIMATION-LEVEL: [none/micro/scroll-triggered] -->
<!-- VISUAL-DENSITY: [sparse/balanced/rich] -->

CRITICAL: Output ONLY the complete HTML code starting with <!DOCTYPE html>.
Do NOT include any explanations, descriptions, or markdown formatting.
Do NOT write about what you created - just output the raw HTML code.
Your response should begin immediately with <!DOCTYPE html> and end with </html>.'''


def landing_prompt(product_description, framework, theme, sections, design_data=None) -> str:
    sections_str = ", ".join(sections) if sections else "hero, features, pricing, footer"
    
    # Dynamic content integration
    content_hooks = ""
    if design_data:
        cs = design_data.get('content_strategy', {})
        hooks = [
            f"Value Hook: {cs.get('core_messaging',{}).get('unique_angle','')}",
            f"Emotional Trigger: {cs.get('hero',{}).get('supporting_element','')}",
            f"Social Proof: {cs.get('objections',{}).get('trust_elements',[])[:1]}"
        ]
        content_hooks = "\nContent Anchors:\n- " + "\n- ".join(filter(None, hooks))
    
    return f'''Create a high-converting landing page that adapts to its purpose.

Product: {product_description}
Sections: {sections_str}
Framework: {framework}
Theme: {theme}
{content_hooks}

Design Framework:
1. Assess each section's communication goal
2. Choose visual treatment accordingly:
   - Data → Charts/diagrams
   - Features → Product shots
   - Benefits → Illustrations
   - Social Proof → Testimonials with photos

Technical Requirements:
- Semantic HTML5
- CSS custom properties
- Responsive images
- Accessible interactions
- Use SVG icons or icon libraries (Heroicons, Lucide, Feather) instead of emoji characters for professional appearance
- IMPORTANT: When referencing images (reference.jpg, reference_1_*.jpg, etc.), use relative path ../filename.jpg since HTML is in output/landing-page/ but images are in output/

CRITICAL: Output ONLY the complete HTML code starting with <!DOCTYPE html>.
Do NOT include any explanations, descriptions, or markdown formatting.
Do NOT write about what you created - just output the raw HTML code.
Your response should begin immediately with <!DOCTYPE html> and end with </html>.'''


def regeneration_prompt(product_desc, framework, theme, section_list, existing_context=None) -> str:
    """Smart regeneration that understands existing design language"""
    context_analysis = ""
    if existing_context:
        context_analysis = "\n".join(
            f"- {k}: {v[:60]}..." if isinstance(v,str) else f"- {k}: {v}"
            for k,v in existing_context.items()
        )
    
    sections_to_generate = "\n".join([f"- {section}" for section in section_list])
    
    # Get theme-specific design rules
    theme_rules = ""
    if theme == "brutalist":
        theme_rules = """
BRUTALIST THEME REQUIREMENTS - MUST FOLLOW EXACTLY:
- Use ONLY these colors: bg-black, bg-white, bg-red-600, bg-yellow-400
- Use ONLY these text styles: font-black, font-bold, uppercase, tracking-tight, tracking-wide
- REQUIRED classes on ALL sections: brutalist-border, brutalist-shadow
- Typography: JetBrains Mono font (already loaded)
- NO rounded corners, NO gradients, NO soft shadows
- Use sharp, geometric layouts with high contrast
- All buttons MUST have: brutalist-border brutalist-shadow hover:translate-x-1 hover:translate-y-1 hover:shadow-none
- All text MUST be UPPERCASE where appropriate
- Color combinations: black text on white/yellow, white text on black/red"""
    elif theme == "minimal":
        theme_rules = """
MINIMAL THEME REQUIREMENTS - MUST FOLLOW EXACTLY:
- Use neutral colors: bg-white, bg-gray-50, bg-gray-100, text-gray-900, text-gray-600
- Typography: font-normal, font-medium, font-semibold (NO font-black)
- Generous whitespace: py-16, py-24, space-y-8, space-y-12
- Subtle borders: border border-gray-200, rounded-lg
- Clean buttons: bg-blue-600, hover:bg-blue-700, rounded-md, px-6 py-3
- Minimal shadows: shadow-sm, shadow-md
- Simple layouts with lots of breathing room"""
    elif theme == "playful":
        theme_rules = """
PLAYFUL THEME REQUIREMENTS - MUST FOLLOW EXACTLY:
- Bright colors: bg-pink-500, bg-purple-500, bg-blue-500, bg-yellow-400, bg-green-500
- Rounded elements: rounded-xl, rounded-2xl, rounded-full
- Fun typography: font-bold, font-extrabold
- Organic shapes and bouncy animations: hover:scale-105, transition-transform
- Colorful gradients: bg-gradient-to-r from-pink-500 to-purple-500
- Playful spacing and asymmetrical layouts"""
    elif theme == "corporate":
        theme_rules = """
CORPORATE THEME REQUIREMENTS - MUST FOLLOW EXACTLY:
- Professional colors: bg-blue-900, bg-gray-800, bg-white, text-blue-900
- Conservative typography: font-medium, font-semibold
- Structured layouts: grid system, even spacing
- Subtle shadows: shadow-lg, shadow-xl
- Professional buttons: bg-blue-600, hover:bg-blue-700
- Clean, trustworthy design patterns"""
    elif theme == "terminal":
        theme_rules = """
TERMINAL THEME REQUIREMENTS - MUST FOLLOW EXACTLY:
- Matrix colors: bg-black, bg-gray-900, text-green-400, text-green-300
- Monospace font: font-mono (already loaded)
- Terminal aesthetics: border-green-500, bg-green-500/10
- Command-line elements: $ prompts, code blocks
- Pixelated/blocky design: sharp edges, no rounded corners
- Glowing effects: animate-pulse, text-green-400"""
    elif theme == "dark":
        theme_rules = """
DARK THEME REQUIREMENTS - MUST FOLLOW EXACTLY:
- Dark backgrounds: bg-gray-900, bg-gray-800, bg-black
- Light text: text-white, text-gray-100, text-gray-300
- Dark accent colors: bg-blue-600, bg-purple-600, bg-indigo-600
- Subtle borders: border-gray-700, border-gray-600
- High contrast for accessibility"""
    elif theme == "morphism":
        theme_rules = """
MORPHISM THEME REQUIREMENTS - MUST FOLLOW EXACTLY:
- Soft backgrounds: bg-gray-100, bg-white, bg-gradient-to-br
- Glass effects: backdrop-blur-sm, bg-white/20, border border-white/20
- Soft shadows: shadow-xl, shadow-2xl with blur
- Rounded corners: rounded-xl, rounded-2xl
- Subtle colors with transparency: bg-blue-500/10, text-gray-700"""
    else:
        theme_rules = f"Follow {theme} theme guidelines with appropriate colors and styling"
    
    return f'''You are a design system specialist refreshing page sections.

Product: {product_desc}
Sections to update: {", ".join(section_list)}
Framework: {framework}
Theme: {theme}

Existing Context:
{context_analysis or "No specific context provided"}

{theme_rules}

Generate ONLY the requested sections with proper markers. For each section, use this format:

<!-- START: section_name -->
<section>
  ... section content ...
</section>
<!-- END: section_name -->

Sections to generate:
{sections_to_generate}

CRITICAL REGENERATION RULES:
1. MUST preserve the exact {theme} theme styling - analyze existing sections first
2. MUST maintain consistent design patterns with other sections
3. MUST use the same CSS classes and color scheme as existing content
4. Content can be updated, but design MUST match existing sections perfectly
5. When referencing images: use relative path ../filename.jpg
6. NO deviation from established visual patterns

CRITICAL: Output ONLY the HTML sections with START/END markers.
Do NOT include any explanations, descriptions, or markdown formatting.
Do NOT output a complete HTML document - just the requested sections.'''