# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CCUX (Claude Code UI Generator) is a sophisticated Python CLI tool that automatically generates conversion-optimized frontend landing pages using professional UX design thinking methodology. The tool leverages Claude AI to implement a comprehensive 12-phase design process used by professional UX agencies, combining automated competitor analysis with strategic design decisions.

## Claude Integration

### Purpose of Claude Integration
This project integrates with the Claude CLI to provide automated UI/UX design intelligence. Claude AI powers:

1. **Reference Discovery**: Automatically finds 3 competitor websites based on product descriptions
2. **Design Analysis**: Analyzes captured screenshots for UI patterns, strengths, and weaknesses
3. **User Research**: Creates empathy maps, personas, and user journeys
4. **Strategic Copy**: Generates conversion-optimized copy based on competitive analysis
5. **Code Generation**: Produces production-ready HTML/React components with TailwindCSS

### Claude CLI Usage
The tool invokes Claude CLI using:
```bash
claude --print "prompt content here"
```

**Special Notes:**
- **Timeout Protection**: 5-minute timeout per Claude invocation to prevent hanging
- **Token Management**: Automatically summarizes product descriptions >100 words to 100-150 words to optimize token usage
- **Usage Tracking**: Parses and displays input tokens, output tokens, and estimated costs from stderr
- **Error Handling**: Graceful error capture with user-friendly messages
- **Streaming Output**: Real-time progress indication during Claude processing

## Commands Reference

### `ccux init`
Initialize CCUX by installing required Playwright browsers.

**Usage:**
```bash
ccux init
```

**Description:** Downloads and installs Chromium browser for Playwright screenshot capture. Must be run once after installation.

**Example:**
```bash
ccux init
```

---

### `ccux gen`
Generate a conversion-optimized landing page using AI-powered design thinking.

**Usage:**
```bash
ccux gen [OPTIONS]
```

**Options:**
- `--desc, -d TEXT`: Product description
- `--desc-file FILE`: Path to file containing product description
- `--url, -u URL`: Reference URLs (can be used multiple times, max 3)
- `--framework, -f [html|react]`: Output framework (default: html)
- `--theme, -t [minimal|brutalist|playful|corporate|morphism|animated|terminal|aesthetic|dark|vibrant|sustainable|data|illustrated]`: Design theme (default: minimal)
- `--no-design-thinking`: Skip full design thinking process for faster generation
- `--output, -o DIR`: Output directory (default: output/landing-page)

**Interactive Mode (Recommended):**
```bash
ccux gen
```

**Quick Generation Examples:**
```bash
# Simple mode (faster, no design thinking)
ccux gen --desc "AI-powered project management tool" --no-design-thinking

# With theme specification
ccux gen --desc "Product description" --theme brutalist

# Load from file with multiple references
ccux gen --desc-file product_desc.txt --url https://strapi.io --url https://discord.com --theme brutalist

# React output with corporate theme
ccux gen --desc "SaaS platform" --framework react --theme corporate

# New modern themes
ccux gen --desc "Design portfolio" --theme morphism
ccux gen --desc "Developer tools" --theme terminal
ccux gen --desc "Interactive story" --theme animated
ccux gen --desc "Music platform" --theme aesthetic

# Additional theme examples
ccux gen --desc "Developer tools" --theme dark
ccux gen --desc "Marketing campaign" --theme vibrant
ccux gen --desc "Eco-friendly products" --theme sustainable
ccux gen --desc "Analytics dashboard" --theme data
ccux gen --desc "Educational platform" --theme illustrated
```

**Comprehensive Analysis (Default):**
```bash
# Full 12-phase design thinking process
ccux gen --desc "AI-powered project management tool"

# With custom reference URLs
ccux gen --url https://linear.app --desc "Project management tool"
```

---

### `ccux regen`
Regenerate specific sections of an existing landing page.

**Usage:**
```bash
ccux regen [OPTIONS]
```

**Options:**
- `--section, -s TEXT`: Section(s) to regenerate (comma-separated)
- `--all`: Regenerate all sections
- `--desc, -d TEXT`: Product description (auto-detected if not provided)
- `--file, -f FILE`: Path to landing page file
- `--output, -o DIR`: Output directory

**Examples:**
```bash
# Regenerate hero section
ccux regen --section hero

# Regenerate multiple sections
ccux regen --section hero,features,pricing

# Regenerate all sections
ccux regen --all

# Regenerate with custom description
ccux regen --section hero --desc "Updated product description"

# Regenerate specific file
ccux regen --section pricing --file custom/page.html
```

---

### `ccux theme`
Change the design theme of an existing landing page.

**Usage:**
```bash
ccux theme THEME [OPTIONS]
```

**Arguments:**
- `THEME`: New design theme (minimal|brutalist|playful|corporate|morphism|animated|terminal|aesthetic|dark|vibrant|sustainable|data|illustrated)

**Options:**
- `--file, -f FILE`: Path to landing page file
- `--output, -o DIR`: Output directory

**Examples:**
```bash
# Change to brutalist theme
ccux theme brutalist

# Change theme for specific file
ccux theme playful --file custom/page.html

# Change to corporate theme
ccux theme corporate

# New modern themes
ccux theme morphism --file portfolio.html
ccux theme terminal --file dev-tools.html
ccux theme animated --file interactive-story.html
ccux theme aesthetic --file music-site.html

# Additional theme examples
ccux theme dark --file developer-app.html
ccux theme vibrant --file marketing-site.html
ccux theme sustainable --file eco-brand.html
ccux theme data --file analytics-dashboard.html
ccux theme illustrated --file education-platform.html
```

**Note:** Requires a landing page generated with full design thinking process (not `--no-design-thinking`).

---

### `ccux help`
Show comprehensive help and usage examples with different topics.

**Usage:**
```bash
ccux help [TOPIC]
```

**Topics:**
- `quickstart`: Complete getting started guide with step-by-step instructions
- `themes`: All available design themes with detailed descriptions and use cases  
- `examples`: Common usage patterns, commands, and practical scenarios
- `workflows`: Step-by-step workflows for different user types and goals

**Examples:**
```bash
# Show main help menu with command overview and quick start
ccux help

# Get detailed quickstart guide for new users
ccux help quickstart

# Browse all 13 available themes with descriptions
ccux help themes

# View common usage examples and patterns
ccux help examples

# Learn step-by-step workflows for different scenarios
ccux help workflows
```

**Description:** This comprehensive help system makes CCUX more user-friendly by providing:
- Interactive command reference with examples
- Progressive learning from basic to advanced usage
- Self-service documentation built into the tool
- Real-world workflows for different use cases
- Complete theme guide with descriptions and usage patterns

---

### `ccux version`
Show version information.

**Usage:**
```bash
ccux version
```

**Example:**
```bash
ccux version
```

## Design Thinking Workflow

The tool implements a comprehensive 12-phase design process when not using `--no-design-thinking`:

1. **Reference Discovery** - Auto-finds 3 competitor sites using Claude AI
2. **Screenshot Capture** - Playwright automation captures competitor landing pages
3. **Deep Product Understanding** - Value proposition analysis and problem identification
4. **Competitive UX Analysis** - Screenshot analysis for patterns and weaknesses
5. **User Empathy Mapping** - User research and persona development
6. **Define Site Flow** - Journey mapping and lean sitemap creation
7. **Content Strategy** - Strategic copy development before visual design
8. **Wireframe Validation** - Mobile-first layout validation
9. **Design System** - Typography, colors, WCAG compliance
10. **High-Fidelity Design** - Interactive elements and polish
11. **Final Copy Generation** - Professional conversion copy refinement
12. **Implementation** - Code generation with strategic design decisions

## Configuration

### Available Themes

#### Core Themes
- `minimal`: Clean, content-focused design following Dieter Rams' principles of good design
- `brutalist`: Raw, honest design inspired by Brutalist architecture - bold and uncompromising
- `playful`: Joyful, approachable design using organic shapes and vibrant colors
- `corporate`: Traditional, trustworthy design following established business conventions

#### Modern Design Theory Themes
- `morphism`: Soft, tactile design combining neumorphism and glassmorphism principles
- `animated`: Motion-first design where animation drives user experience and storytelling
- `terminal`: Monospace, CLI-inspired aesthetic appealing to developers and tech enthusiasts
- `aesthetic`: Retro-futuristic design drawing from Y2K, vaporwave, and cyber aesthetics

#### Additional Theme Options
- `dark`: Modern dark theme optimized for contrast and reduced eye strain
- `vibrant`: Colorful, dopamine-rich design that energizes user interactions
- `sustainable`: Nature-inspired design emphasizing eco-conscious branding
- `data`: Information-dense design optimized for dashboards and analytics
- `illustrated`: Hand-drawn, custom illustration-driven design for humanized experiences

**For detailed theme specifications, use cases, and implementation guidelines, see [THEME_IMPLEMENTATION_GUIDE.md](THEME_IMPLEMENTATION_GUIDE.md)**

### Available Frameworks
- `html`: Single HTML file with inline TailwindCSS (default)
- `react`: React component with ESM imports

### Optional Configuration File
Create `ccux.yaml` in your working directory:

```yaml
framework: html    # html or react
theme: minimal     # minimal|brutalist|playful|corporate|morphism|animated|terminal|aesthetic|dark|vibrant|sustainable|data|illustrated
sections: [hero, features, pricing, footer]
claude_cmd: claude
output_dir: output/landing-page
```

## Usage Notes

### Token and Size Limits
- **Automatic Summarization**: Product descriptions >100 words are automatically summarized to 100-150 words to optimize Claude token usage
- **Screenshot Optimization**: Uses JPEG compression for captured screenshots to reduce prompt size
- **Reference Limit**: Maximum 3 reference URLs to prevent prompt bloat
- **Timeout Protection**: 5-minute timeout per Claude invocation

### Performance Optimization
- **Concurrent Processing**: Multiple Claude invocations run in parallel where possible
- **Memory Management**: Cleanup between screenshot captures for large reference sets
- **Resource Blocking**: Playwright blocks ads, trackers, and unnecessary resources for faster page loads

### Error Handling
- **Graceful Fallbacks**: Continues without screenshots if reference capture fails
- **Keyboard Interrupts**: Proper cleanup on Ctrl+C with subprocess termination
- **User-Friendly Messages**: Clear error messages with suggested solutions

## Architecture

### Core Components

1. **CLI Interface** (`src/ccux/cli.py`)
   - Typer-based command structure with rich terminal formatting
   - Interactive mode for guided user experience
   - Configuration loading and validation
   - Robust subprocess handling with real-time streaming

2. **Web Scraping** (`src/ccux/scrape.py` & `src/ccux/scrape_simple.py`)
   - Playwright automation for screenshot capture
   - Cookie consent and modal handling
   - Multiple reference site capture with error recovery
   - Resource optimization and timeout handling

3. **Prompt Templates** (`src/ccux/prompt_templates.py`)
   - 12-phase design thinking methodology
   - Structured prompts for consistent outputs
   - UI/UX best practices integration
   - Section-specific regeneration prompts

### Output Structure
- **HTML mode**: Single `index.html` file with inline TailwindCSS
- **React mode**: `App.jsx` component + `index.html` shell with ESM imports
- **Design Analysis**: `design_analysis.json` with complete research data
- **Screenshots**: Reference images saved as `.jpg` files
- **Section Markers**: HTML comments for precise section identification and regeneration

### Dependencies
- **Typer** (≥0.12.0): CLI framework with rich terminal features
- **Rich** (≥13.7.0): Terminal formatting, progress bars, and user interaction
- **Playwright** (≥1.45.0): Web scraping and screenshot capture with Chromium
- **PyYAML** (≥6.0.1): Configuration file parsing

## Development Notes

### Code Style
- Emoji characters used in terminal output for visual feedback
- Rich formatting system for progress indicators and status messages
- Proper error handling with user-friendly messages
- Thread-safe I/O operations for concurrent processing
- **Generated Pages**: Use SVG icons or icon libraries instead of emoji characters for professional appearance and accessibility

### File Structure
```
src/ccux/
├── __init__.py          # Package initialization
├── __main__.py          # Entry point for python -m ccux
├── cli.py              # Main CLI interface with Typer commands
├── prompt_templates.py  # 12-phase design thinking prompts
├── scrape.py           # Advanced Playwright web scraping
└── scrape_simple.py    # Simplified screenshot capture
```

### What This Project Does

1. **Automated Competitive Research**: Discovers 3 competitor websites and design showcases
2. **Professional Design Process**: Implements a 12-phase UX methodology including product understanding, user research, wireframing, and visual design
3. **Screenshot Analysis**: Uses Playwright to capture and analyze competitor landing pages for design patterns
4. **Strategic Copy Generation**: Creates conversion-optimized copy based on user research and competitive analysis  
5. **Code Generation**: Outputs production-ready HTML or React components with TailwindCSS styling
6. **Real-time Streaming**: Shows Claude's design thinking process in real-time with progress indicators
7. **Section Regeneration**: Allows regenerating specific sections of existing landing pages
8. **Smart Text Summarization**: Automatically summarizes product descriptions longer than 100 words to 100-150 words while preserving key details

### Key Features

- **Automated Reference Discovery**: Finds competitors and design inspiration automatically using Claude AI
- **Multi-site Competitive Analysis**: Captures and analyzes 3 reference sites with screenshot comparison
- **Professional Design Process**: 12-phase methodology including empathy mapping, user journeys, and conversion optimization
- **Conversion-Optimized Copy**: Strategic messaging based on competitive analysis and user research
- **Multiple Output Formats**: Generates HTML with inline TailwindCSS or React components with ESM imports
- **Real-time Progress**: Streams Claude output live with rich terminal formatting and progress indicators
- **Section Regeneration**: Regenerate specific sections (hero, features, pricing, etc.) of existing landing pages
- **Interactive Mode**: Guided setup for users without command-line arguments
- **Robust Error Handling**: Timeout protection, graceful fallbacks, and comprehensive error reporting
- **Cross-platform Support**: Works on Windows, macOS, and Linux
- **Memory Efficient**: Cleanup between captures for large reference sets
- **Smart Text Processing**: Automatically summarizes lengthy product descriptions (>100 words) to optimize processing while preserving essential details

### Implementation Details

The tool implements a sophisticated workflow:

1. **Reference Discovery Phase**: Uses Claude AI to find 3 competitor websites
2. **Screenshot Capture**: Playwright automation captures competitor landing pages with error handling  
3. **Design Thinking Process**: 12-phase methodology including:
   - Deep product understanding and value proposition analysis
   - Competitive UX analysis of captured screenshots
   - User empathy mapping and persona development
   - Site flow and journey mapping
   - Content strategy development
   - Mobile-first wireframing validation
   - Visual identity and design system creation
   - High-fidelity design with interactive elements
   - Final copy refinement and polish
   - Strategic implementation with conversion optimization

4. **Section Management**: Advanced section handling including:
   - HTML comment markers for section identification
   - Individual section regeneration without affecting other parts
   - Context preservation during section updates
   - Design analysis tracking for regeneration history

5. **Code Generation**: Produces production-ready HTML or React components with:
   - Semantic HTML structure with section markers
   - TailwindCSS styling with custom design system
   - SEO optimization with meta tags and schema markup
   - Responsive design patterns
   - Accessibility compliance (WCAG guidelines)
   - Performance optimizations
   - SVG icons or icon libraries (Heroicons, Lucide, Feather) instead of emoji characters for professional appearance and cross-platform compatibility

