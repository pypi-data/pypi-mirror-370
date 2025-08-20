#!/usr/bin/env python3
"""
CCUX - Claude Code UI Generator CLI
A sophisticated Python CLI tool that automatically generates conversion-optimized 
frontend landing pages using professional UX design thinking methodology.
"""

import os
import sys
import json
import time
import threading
import subprocess
import signal
import re
from pathlib import Path
from typing import Optional, List, Dict, Any
from urllib.parse import urlparse

import typer
import yaml
from rich import print
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.status import Status
from rich.table import Table
from rich.prompt import Prompt, Confirm

from . import __version__
from .scrape import capture_multiple_references
from .scrape_simple import capture
from .theme_specifications import (
    THEME_SPECIFICATIONS,
    get_theme_choices,
    get_theme_description,
    get_theme_design_system_rules,
    detect_theme_from_content
)
from .prompt_templates import (
    reference_discovery_prompt,
    deep_product_understanding_prompt,
    ux_analysis_prompt,
    empathize_prompt,
    define_prompt,
    ideate_prompt,
    wireframe_prompt,
    design_system_prompt,
    high_fidelity_design_prompt,
    prototype_prompt,
    implementation_prompt,
    landing_prompt,
    regeneration_prompt
)

app = typer.Typer(
    name="ccux",
    help="Claude Code UI Generator - Automatically generate conversion-optimized landing pages",
    no_args_is_help=True,
    rich_markup_mode="rich"
)
console = Console()

# Global variables for signal handling
current_subprocess = None
current_progress = None

def signal_handler(signum, frame):
    """Handle keyboard interrupts gracefully"""
    global current_subprocess, current_progress
    
    console.print("\n[yellow]⚠️  Interrupt received, cleaning up...[/yellow]")
    
    if current_subprocess:
        try:
            current_subprocess.terminate()
            current_subprocess.wait(timeout=5)
        except:
            try:
                current_subprocess.kill()
            except:
                pass
    
    if current_progress:
        current_progress.stop()
    
    console.print("[red]❌ Operation cancelled by user[/red]")
    sys.exit(1)

# Register signal handler
signal.signal(signal.SIGINT, signal_handler)

class Config:
    """Configuration management for CCUX"""
    
    def __init__(self, config_path: str = "ccux.yaml"):
        self.config_path = config_path
        self.defaults = {
            'framework': 'html',
            'theme': 'minimal',
            'sections': ['hero', 'features', 'pricing', 'footer'],
            'claude_cmd': 'claude',
            'output_dir': 'output/landing-page'
        }
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config = yaml.safe_load(f) or {}
                # Merge with defaults
                return {**self.defaults, **config}
            except Exception as e:
                console.print(f"[yellow]⚠️  Error loading config: {e}. Using defaults.[/yellow]")
        
        return self.defaults.copy()
    
    def get(self, key: str, default=None):
        return self.config.get(key, default)

def run_claude_with_progress(prompt: str, description: str = "Claude Code is thinking...") -> tuple[str, Dict[str, Any]]:
    """Run Claude CLI with real-time progress indication and usage tracking"""
    global current_subprocess, current_progress
    
    config = Config()
    claude_cmd = config.get('claude_cmd', 'claude')
    
    # Prepare Claude command
    cmd = [claude_cmd, '--print', prompt]
    
    output_lines = []
    stderr_lines = []
    usage_stats = {}
    
    def read_stream(stream, lines_list):
        """Read from stream and collect output"""
        try:
            for line in iter(stream.readline, ''):
                if line:
                    lines_list.append(line.strip())
        except:
            pass
    
    with Progress(
        SpinnerColumn(),
        TextColumn(f"[bold blue]{description}"),
        TimeElapsedColumn(),
        console=console,
        transient=False
    ) as progress:
        current_progress = progress
        task = progress.add_task("Processing", total=None)
        
        try:
            # Start Claude process
            current_subprocess = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Start threads to read stdout and stderr
            stdout_thread = threading.Thread(
                target=read_stream, 
                args=(current_subprocess.stdout, output_lines)
            )
            stderr_thread = threading.Thread(
                target=read_stream, 
                args=(current_subprocess.stderr, stderr_lines)
            )
            
            stdout_thread.start()
            stderr_thread.start()
            
            # Wait for process with timeout (5 minutes)
            try:
                current_subprocess.wait(timeout=300)
            except subprocess.TimeoutExpired:
                current_subprocess.kill()
                raise Exception("Claude Code timed out after 5 minutes")
            
            # Wait for threads to finish
            stdout_thread.join(timeout=2)
            stderr_thread.join(timeout=2)
            
            if current_subprocess.returncode != 0:
                error_msg = '\n'.join(stderr_lines) if stderr_lines else "Claude Code execution failed"
                raise Exception(f"Claude Code failed: {error_msg}")
            
            # Parse usage statistics from stderr
            for line in stderr_lines:
                if "Input tokens:" in line:
                    try:
                        usage_stats['input_tokens'] = int(line.split(':')[1].strip())
                    except:
                        pass
                elif "Output tokens:" in line:
                    try:
                        usage_stats['output_tokens'] = int(line.split(':')[1].strip())
                    except:
                        pass
                elif "Cost:" in line or "$" in line:
                    try:
                        # Extract cost from line
                        import re
                        cost_match = re.search(r'\$([0-9]+\.?[0-9]*)', line)
                        if cost_match:
                            usage_stats['cost'] = float(cost_match.group(1))
                    except:
                        pass
            
        except Exception as e:
            current_progress = None
            current_subprocess = None
            raise e
        
        finally:
            current_progress = None
            current_subprocess = None
    
    # Combine output
    full_output = '\n'.join(output_lines)
    
    # Show usage statistics if available
    if usage_stats:
        console.print("\n[bold cyan]📊 Usage Statistics:[/bold cyan]")
        if 'input_tokens' in usage_stats:
            console.print(f"  Input tokens: [green]{usage_stats['input_tokens']:,}[/green]")
        if 'output_tokens' in usage_stats:
            console.print(f"  Output tokens: [green]{usage_stats['output_tokens']:,}[/green]")
        if 'cost' in usage_stats:
            console.print(f"  Estimated cost: [green]${usage_stats['cost']:.4f}[/green]")
        console.print()
    
    return full_output, usage_stats

def summarize_long_description(desc: str) -> str:
    """Summarize product description if longer than 100 words"""
    word_count = len(desc.split())
    
    if word_count <= 100:
        return desc
    
    console.print(f"[yellow]📝 Description has {word_count} words, summarizing to 100-150 words...[/yellow]")
    
    summarization_prompt = f"""You are given a long product description. 
If the text is fewer than 100 words, return it unchanged. 
If it is longer than 100 words, summarize it into 100–150 words while keeping only the most important details:

- Problem it solves
- Target user
- Unique differentiator
- Best feature

Make the summary clear, concise, and business-oriented. 
Do not include filler or marketing fluff. 
Output only the final text (no explanations).

Product description to summarize:
{desc}"""
    
    try:
        summary, _ = run_claude_with_progress(summarization_prompt, "Summarizing description...")
        return summary.strip()
    except Exception as e:
        console.print(f"[yellow]⚠️  Failed to summarize description: {e}. Using original.[/yellow]")
        return desc

def safe_json_parse(text: str) -> Dict[str, Any]:
    """Safely parse JSON from Claude output"""
    try:
        # Try to extract JSON from code blocks
        lines = text.strip().split('\n')
        json_lines = []
        in_json = False
        
        for line in lines:
            if line.strip().startswith('```json') or line.strip().startswith('```'):
                in_json = True
                continue
            elif line.strip() == '```' and in_json:
                break
            elif in_json:
                json_lines.append(line)
            elif line.strip().startswith('{'):
                # Direct JSON start
                json_lines = [line]
                in_json = True
            elif in_json and line.strip().endswith('}'):
                json_lines.append(line)
                break
            elif in_json:
                json_lines.append(line)
        
        if json_lines:
            json_text = '\n'.join(json_lines)
            return json.loads(json_text)
        
        # Fallback: try parsing entire text
        return json.loads(text)
        
    except Exception:
        return {}

def strip_code_blocks(text: str) -> str:
    """Strip markdown code blocks from Claude output"""
    lines = text.strip().split('\n')
    result_lines = []
    in_code_block = False
    
    for line in lines:
        # Check for start of code block
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            continue
        
        # If not in code block, include the line
        if not in_code_block:
            result_lines.append(line)
    
    return '\n'.join(result_lines).strip()

def find_landing_page_files(output_dir: str = None) -> Dict[str, str]:
    """Find existing landing page files in common locations"""
    if output_dir is None:
        output_dir = "output/landing-page"
    
    search_paths = [
        output_dir,
        ".",
        "dist",
        "build",
        "public"
    ]
    
    found_files = {}
    
    for search_path in search_paths:
        if not os.path.exists(search_path):
            continue
            
        # Look for HTML files
        for file_name in ['index.html', 'landing.html', 'page.html']:
            file_path = os.path.join(search_path, file_name)
            if os.path.exists(file_path):
                found_files['html'] = file_path
                break
                
        # Look for React files
        for file_name in ['App.jsx', 'Landing.jsx', 'Page.jsx']:
            file_path = os.path.join(search_path, file_name)
            if os.path.exists(file_path):
                found_files['react'] = file_path
                break
    
    return found_files

def extract_page_context(file_path: str) -> Dict[str, Any]:
    """Extract metadata and context from existing landing page"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        context = {
            'framework': 'react' if file_path.endswith('.jsx') else 'html',
            'sections': [],
            'theme': 'minimal',  # Default
            'other_sections': []
        }
        
        # Extract sections using markers
        section_patterns = [
            r'<!-- START: (\w+) -->(.*?)<!-- END: \1 -->',
            r'<!-- SECTION: (\w+) -->(.*?)<!-- END SECTION: \1 -->'
        ]
        
        sections = []
        for pattern in section_patterns:
            found = re.findall(pattern, content, re.DOTALL)
            sections.extend(found)
        
        for section_name, _ in sections:
            context['sections'].append(section_name)
        
        # Enhanced theme detection using new system
        context['theme'] = detect_theme_from_content(content)
            
        return context
        
    except Exception as e:
        console.print(f"[yellow]⚠️  Could not extract context from {file_path}: {e}[/yellow]")
        return {'framework': 'html', 'sections': [], 'theme': 'minimal', 'other_sections': []}

def update_design_analysis_for_regen(output_dir: str, sections_regenerated: List[str], product_desc: str, usage_stats: Dict[str, Any]) -> None:
    """Update design_analysis.json file with regeneration information"""
    analysis_file = os.path.join(output_dir, 'design_analysis.json')
    
    try:
        # Load existing analysis or create new one
        if os.path.exists(analysis_file):
            with open(analysis_file, 'r') as f:
                analysis_data = json.load(f)
        else:
            analysis_data = {}
        
        # Update regeneration history
        if 'regeneration_history' not in analysis_data:
            analysis_data['regeneration_history'] = []
        
        # Add current regeneration record
        regen_record = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'sections_updated': sections_regenerated,
            'product_description': product_desc,
            'usage_stats': usage_stats,
            'method': 'regen_command'
        }
        
        analysis_data['regeneration_history'].append(regen_record)
        
        # Update last_updated timestamp
        analysis_data['last_updated'] = time.strftime('%Y-%m-%d %H:%M:%S')
        
        # Update sections list
        if 'sections' not in analysis_data:
            analysis_data['sections'] = []
        
        # Add regenerated sections to sections list if not already present
        for section in sections_regenerated:
            if section not in analysis_data['sections']:
                analysis_data['sections'].append(section)
        
        # Update product understanding if provided
        if product_desc and product_desc != "Landing page product":
            if 'product_understanding' not in analysis_data:
                analysis_data['product_understanding'] = {}
            
            analysis_data['product_understanding']['description'] = product_desc
            analysis_data['product_understanding']['last_updated'] = time.strftime('%Y-%m-%d %H:%M:%S')
        
        # Save updated analysis
        with open(analysis_file, 'w') as f:
            json.dump(analysis_data, f, indent=2)
        
        console.print(f"[cyan]📊 Updated design analysis: {analysis_file}[/cyan]")
        
    except Exception as e:
        console.print(f"[yellow]⚠️  Could not update design analysis: {e}[/yellow]")


def replace_sections_in_file(file_path: str, new_sections_content: str, sections_to_replace: List[str]) -> bool:
    """Replace specific sections in the landing page file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        updated_content = original_content
        
        # Extract new sections from generated content
        new_section_pattern = r'<!-- START: (\w+) -->(.*?)<!-- END: \1 -->'
        new_sections = dict(re.findall(new_section_pattern, new_sections_content, re.DOTALL))
        
        # Replace each requested section
        for section_name in sections_to_replace:
            section_key = section_name.lower()
            if section_key in new_sections:
                new_section_code = f'<!-- START: {section_key} -->{new_sections[section_key]}<!-- END: {section_key} -->'
                
                # Try multiple patterns to find existing section
                patterns_to_try = [
                    f'<!-- START: {section_key} -->.*?<!-- END: {section_key} -->',
                    f'<!-- SECTION: {section_key} -->.*?<!-- END SECTION: {section_key} -->',
                    f'<!-- {section_name.title()} Section -->.*?(?=<!-- .* Section -->|</body>|$)',
                    f'<section[^>]*class="[^"]*{section_key}[^"]*"[^>]*>.*?</section>'
                ]
                
                section_replaced = False
                for pattern in patterns_to_try:
                    if re.search(pattern, updated_content, re.DOTALL | re.IGNORECASE):
                        updated_content = re.sub(pattern, new_section_code, updated_content, flags=re.DOTALL | re.IGNORECASE)
                        section_replaced = True
                        console.print(f"[green]✓ Replaced {section_name} section using pattern match[/green]")
                        break
                
                if not section_replaced:
                    # Section doesn't exist, append it (could be a new section)
                    # Try to find a good insertion point (before closing body tag)
                    if '</body>' in updated_content:
                        # Insert before </body> and after </script> if it exists
                        script_end = updated_content.rfind('</script>')
                        body_end = updated_content.rfind('</body>')
                        
                        if script_end > 0 and script_end < body_end:
                            # Insert after </script> but before </body>
                            insertion_point = script_end + len('</script>')
                            updated_content = updated_content[:insertion_point] + f'\n{new_section_code}\n' + updated_content[insertion_point:]
                        else:
                            # Insert just before </body>
                            updated_content = updated_content.replace('</body>', f'{new_section_code}\n</body>')
                    else:
                        updated_content += f'\n{new_section_code}'
                    
                    console.print(f"[yellow]⚠ Added new {section_name} section (original not found)[/yellow]")
        
        # Clean up any duplicate sections that might have been created
        for section_name in sections_to_replace:
            section_key = section_name.lower()
            # Find all instances of this section and keep only the first one
            section_pattern = f'<!-- START: {section_key} -->.*?<!-- END: {section_key} -->'
            matches = list(re.finditer(section_pattern, updated_content, re.DOTALL))
            if len(matches) > 1:
                # Keep the first match, remove the rest
                for i in range(len(matches) - 1, 0, -1):  # Remove from end to beginning
                    match = matches[i]
                    updated_content = updated_content[:match.start()] + updated_content[match.end():]
                console.print(f"[yellow]🧹 Cleaned up duplicate {section_name} sections[/yellow]")
        
        # Write updated content back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
            
        return True
        
    except Exception as e:
        console.print(f"[red]❌ Error updating file {file_path}: {e}[/red]")
        return False

@app.command()
def init():
    """Initialize CCUX by installing Playwright browsers"""
    console.print("[bold blue]🚀 Initializing CCUX...[/bold blue]")
    
    try:
        # Install Playwright browsers
        with Status("[bold green]Installing Playwright browsers...", console=console):
            result = subprocess.run(
                ["python", "-m", "playwright", "install", "chromium"],
                capture_output=True,
                text=True,
                check=True
            )
        
        console.print("[bold green]✅ CCUX initialized successfully![/bold green]")
        console.print("\nYou can now run:")
        console.print("  [bold]ccux gen --desc 'Your product description'[/bold]")
        
    except subprocess.CalledProcessError as e:
        console.print(f"[red]❌ Failed to initialize CCUX: {e.stderr}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]❌ Error during initialization: {e}[/red]")
        raise typer.Exit(1)

@app.command()
def gen(
    desc: Optional[str] = typer.Option(None, "--desc", "-d", help="Product description"),
    desc_file: Optional[str] = typer.Option(None, "--desc-file", help="Path to file containing product description"),
    urls: Optional[List[str]] = typer.Option(None, "--url", "-u", help="Reference URLs (can be used multiple times)"),
    framework: Optional[str] = typer.Option(None, "--framework", "-f", help="Output framework (html|react)"),
    theme: Optional[str] = typer.Option(None, "--theme", "-t", help=f"Design theme ({'/'.join(get_theme_choices())})"),
    no_design_thinking: bool = typer.Option(False, "--no-design-thinking", help="Skip design thinking process"),
    output_dir: Optional[str] = typer.Option(None, "--output", "-o", help="Output directory")
):
    """Generate a conversion-optimized landing page
    
    Run without arguments for interactive mode, or provide --desc for direct usage.
    Use --desc-file to load description from a text file for longer copy.
    """
    
    # Load configuration
    config = Config()
    
    # Handle desc from file or interactive mode
    if desc_file:
        # Read description from file
        if not os.path.exists(desc_file):
            console.print(f"[red]❌ Description file not found: {desc_file}[/red]")
            raise typer.Exit(1)
        try:
            with open(desc_file, 'r', encoding='utf-8') as f:
                desc = f.read().strip()
            console.print(f"[green]📄 Description loaded from: {desc_file}[/green]")
        except Exception as e:
            console.print(f"[red]❌ Error reading description file: {e}[/red]")
            raise typer.Exit(1)
    elif not desc:
        # Interactive mode - prompt for inputs
        console.print("[bold blue]🎨 Interactive Mode - CCUX Generator[/bold blue]")
        console.print("Let's create your landing page step by step.\n")
        
        # Get product description
        desc = Prompt.ask(
            "[bold]What product/service would you like to create a landing page for?[/bold]",
            default="",
            show_default=False
        )
        if not desc.strip():
            console.print("[red]❌ Product description is required.[/red]")
            raise typer.Exit(1)
        
        # Optional URLs
        if not urls:
            url_input = Prompt.ask(
                "[bold]Reference URLs (optional)[/bold]\nEnter competitor or inspiration websites (comma-separated)",
                default="",
                show_default=False
            )
            if url_input.strip():
                # Split by comma and filter valid URLs
                url_list = [u.strip() for u in url_input.split(',') if u.strip().startswith('http')]
                if url_list:
                    urls = url_list
        
        # Framework selection
        if not framework:
            framework_choices = ['html', 'react']
            framework = Prompt.ask(
                "[bold]Output framework[/bold]",
                choices=framework_choices,
                default='html'
            )
        
        # Theme selection with descriptions
        if not theme:
            theme_choices = get_theme_choices()
            console.print("\n[bold]Available themes:[/bold]")
            for i, choice in enumerate(theme_choices, 1):
                desc = get_theme_description(choice)
                console.print(f"  {i}. [cyan]{choice}[/cyan]: {desc[:60]}...")
            
            theme = Prompt.ask(
                "\n[bold]Select design theme[/bold]",
                choices=theme_choices,
                default='minimal'
            )
        
        # Design thinking process option
        if not no_design_thinking:
            use_design_thinking = Confirm.ask(
                "[bold]Run full design thinking process?[/bold]\n"
                "This includes competitor research, user analysis, and wireframing (takes longer but better results)",
                default=True
            )
            no_design_thinking = not use_design_thinking
        
        console.print(f"\n[bold green]✅ Configuration complete![/bold green]")
        console.print(f"Product: [cyan]{desc}[/cyan]")
        if urls:
            console.print(f"References: [cyan]{', '.join(urls)}[/cyan]")
        console.print(f"Framework: [cyan]{framework}[/cyan] | Theme: [cyan]{theme}[/cyan]")
        console.print(f"Design thinking: [cyan]{'Yes' if not no_design_thinking else 'No'}[/cyan]\n")
    
    # Summarize description if too long
    if desc:
        desc = summarize_long_description(desc)
    
    # Override config with CLI arguments
    framework = framework or config.get('framework', 'html')
    theme = theme or config.get('theme', 'minimal')
    output_dir = output_dir or config.get('output_dir', 'output/landing-page')
    sections = config.get('sections', ['hero', 'features', 'pricing', 'footer'])
    
    # Validate inputs
    valid_frameworks = ['html', 'react']
    valid_themes = get_theme_choices()
    
    if framework not in valid_frameworks:
        console.print(f"[red]❌ Invalid framework. Must be one of: {', '.join(valid_frameworks)}[/red]")
        raise typer.Exit(1)
    
    if theme not in valid_themes:
        console.print(f"[red]❌ Invalid theme. Must be one of: {', '.join(valid_themes)}[/red]")
        raise typer.Exit(1)
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    console.print(f"[bold blue]🎨 Generating landing page for: {desc}[/bold blue]")
    console.print(f"Framework: [green]{framework}[/green] | Theme: [green]{theme}[/green]")
    
    if no_design_thinking:
        # Simple mode - direct generation
        console.print("\n[bold yellow]⚡ Quick generation mode (no design thinking)[/bold yellow]")
        
        screenshot_path = None
        if urls and len(urls) > 0:
            try:
                # Use the first URL for simple mode
                url = urls[0]
                console.print(f"[bold blue]📸 Capturing reference screenshot from {url}...[/bold blue]")
                _, screenshot_path = capture(url, output_dir)
            except Exception as e:
                console.print(f"[yellow]⚠️  Failed to capture screenshot: {e}[/yellow]")
        
        # Generate directly
        prompt = landing_prompt(desc, framework, theme, sections)
        output, stats = run_claude_with_progress(prompt, "Generating landing page...")
        
        # Save output
        if framework == 'react':
            # Save React component
            with open(os.path.join(output_dir, 'App.jsx'), 'w') as f:
                f.write(strip_code_blocks(output))
            
            # Create minimal index.html shell
            html_shell = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{desc}</title>
    <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
    <div id="root"></div>
    <script type="text/babel" src="App.jsx"></script>
</body>
</html>'''
            
            with open(os.path.join(output_dir, 'index.html'), 'w') as f:
                f.write(html_shell)
        else:
            # Save HTML
            with open(os.path.join(output_dir, 'index.html'), 'w') as f:
                f.write(strip_code_blocks(output))
        
        console.print(f"[bold green]✅ Landing page generated successfully![/bold green]")
        console.print(f"📁 Output saved to: [bold]{output_dir}[/bold]")
        
    else:
        # Full design thinking process
        console.print("\n[bold green]🧠 Running comprehensive design thinking process...[/bold green]")
        
        try:
            # Phase 1: Reference Discovery
            console.print("\n[bold]Phase 1: Reference Discovery[/bold]")
            prompt = reference_discovery_prompt(desc)
            refs_output, _ = run_claude_with_progress(prompt, "Discovering competitor references...")
            
            # Parse reference URLs
            ref_urls = []
            for line in refs_output.split('\n'):
                if '–' in line and 'http' in line:
                    try:
                        url_part = line.split('–')[1].strip()
                        if url_part.startswith('http'):
                            ref_urls.append(url_part.split()[0])
                    except:
                        continue
            
            # Add user-provided URLs if available
            if urls:
                # Insert user URLs at the beginning, maintaining order
                for i, user_url in enumerate(reversed(urls)):
                    ref_urls.insert(0, user_url)
            
            # Limit to 3 references for performance
            ref_urls = ref_urls[:3]
            
            # 🔍 Debug / confirmation log
            if ref_urls:
                console.print("\n[bold]Discovered Reference URLs:[/bold]")
                for i, u in enumerate(ref_urls, 1):
                    console.print(f"  {i}. {u}", style="cyan")

            
            if not ref_urls:
                console.print("[yellow]⚠️  No reference URLs found. Continuing without screenshots.[/yellow]")
                screenshot_refs = []
            else:
                # Phase 2: Screenshot Capture
                console.print(f"\n[bold]Phase 2: Capturing {len(ref_urls)} reference screenshots[/bold]")
                screenshot_results = capture_multiple_references(ref_urls, output_dir)
                screenshot_refs = [(url, screenshot_path) for url, _, screenshot_path in screenshot_results]
            
            # Phase 3: Deep Product Understanding
            console.print("\n[bold]Phase 3: Deep Product Understanding[/bold]")
            prompt = deep_product_understanding_prompt(desc)
            product_output, _ = run_claude_with_progress(prompt, "Analyzing product positioning...")
            product_understanding = safe_json_parse(product_output)
            
            # Phase 4: UX Analysis
            if screenshot_refs:
                console.print("\n[bold]Phase 4: Competitive UX Analysis[/bold]")
                # Extract just the screenshot paths from the tuples
                screenshot_paths = [screenshot_path for url, screenshot_path in screenshot_refs]
                prompt = ux_analysis_prompt(desc, screenshot_paths)
                ux_output, _ = run_claude_with_progress(prompt, "Analyzing competitor UX patterns...")
                ux_analysis = safe_json_parse(ux_output)
            else:
                ux_analysis = {}
            
            # Phase 5: Empathy & User Research
            console.print("\n[bold]Phase 5: User Empathy Mapping[/bold]")
            prompt = empathize_prompt(desc, product_understanding, ux_analysis)
            empathy_output, _ = run_claude_with_progress(prompt, "Mapping user empathy...")
            user_research = safe_json_parse(empathy_output)
            
            # Phase 6: Define Site Flow
            console.print("\n[bold]Phase 6: Defining Site Flow[/bold]")
            prompt = define_prompt(desc, user_research)
            define_output, _ = run_claude_with_progress(prompt, "Defining site architecture...")
            site_flow = safe_json_parse(define_output)
            
            # Phase 7: Content Strategy
            console.print("\n[bold]Phase 7: Content Strategy[/bold]")
            prompt = ideate_prompt(desc, user_research, site_flow)
            ideate_output, _ = run_claude_with_progress(prompt, "Developing content strategy...")
            content_strategy = safe_json_parse(ideate_output)
            
            # Phase 8: Wireframes
            console.print("\n[bold]Phase 8: Wireframe Validation[/bold]")
            prompt = wireframe_prompt(desc, content_strategy, site_flow)
            wireframe_output, _ = run_claude_with_progress(prompt, "Creating wireframes...")
            wireframes = safe_json_parse(wireframe_output)
            
            # Phase 9: Design System
            console.print("\n[bold]Phase 9: Design System[/bold]")
            prompt = design_system_prompt(desc, wireframes, content_strategy, theme)
            design_output, _ = run_claude_with_progress(prompt, "Building design system...")
            design_system = safe_json_parse(design_output)
            
            # Phase 10: High-Fidelity Design
            console.print("\n[bold]Phase 10: High-Fidelity Design[/bold]")
            prompt = high_fidelity_design_prompt(desc, design_system, wireframes, content_strategy)
            hifi_output, _ = run_claude_with_progress(prompt, "Creating high-fidelity design...")
            hifi_design = safe_json_parse(hifi_output)
            
            # Phase 11: Final Copy Generation
            console.print("\n[bold]Phase 11: Final Copy Generation[/bold]")
            prompt = prototype_prompt(desc, content_strategy, design_system, wireframes)
            copy_output, _ = run_claude_with_progress(prompt, "Generating final copy...")
            final_copy = safe_json_parse(copy_output)
            
            # Phase 12: Implementation
            console.print("\n[bold]Phase 12: Code Implementation[/bold]")
            screenshot_path = screenshot_refs[0][1] if screenshot_refs else None
            design_data = {
                'design_system': design_system,
                'ux_analysis': ux_analysis,
                'wireframes': wireframes,
                'content_strategy': content_strategy
            }
            prompt = implementation_prompt(desc, final_copy, framework, theme, design_data)
            code_output, _ = run_claude_with_progress(prompt, "Implementing landing page...")
            
            # Save all outputs
            analysis_data = {
                'product_understanding': product_understanding,
                'ux_analysis': ux_analysis,
                'user_research': user_research,
                'site_flow': site_flow,
                'content_strategy': content_strategy,
                'wireframes': wireframes,
                'design_system': design_system,
                'hifi_design': hifi_design,
                'final_copy': final_copy
            }
            
            with open(os.path.join(output_dir, 'design_analysis.json'), 'w') as f:
                json.dump(analysis_data, f, indent=2)
            
            # Save code output
            if framework == 'react':
                with open(os.path.join(output_dir, 'App.jsx'), 'w') as f:
                    f.write(strip_code_blocks(code_output))
                
                html_shell = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{desc}</title>
    <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
    <div id="root"></div>
    <script type="text/babel" src="App.jsx"></script>
</body>
</html>'''
                
                with open(os.path.join(output_dir, 'index.html'), 'w') as f:
                    f.write(html_shell)
            else:
                with open(os.path.join(output_dir, 'index.html'), 'w') as f:
                    f.write(strip_code_blocks(code_output))
            
            console.print(f"\n[bold green]✅ Comprehensive landing page generated successfully![/bold green]")
            console.print(f"📁 Output saved to: [bold]{output_dir}[/bold]")
            console.print(f"📊 Design analysis saved to: [bold]{output_dir}/design_analysis.json[/bold]")
            
        except Exception as e:
            console.print(f"[red]❌ Error during design thinking process: {e}[/red]")
            raise typer.Exit(1)
    
    # Show preview instructions
    console.print("\n[bold cyan]🌐 Preview your landing page:[/bold cyan]")
    console.print(f"  [bold]cd {output_dir}[/bold]")
    console.print("  [bold]python -m http.server 3000[/bold]")
    console.print("  Then open [bold]http://localhost:3000[/bold] in your browser")

@app.command()
def regen(
    section: Optional[str] = typer.Option(None, "--section", "-s", help="Section(s) to regenerate (comma-separated)"),
    all: bool = typer.Option(False, "--all", help="Regenerate all sections"),
    desc: Optional[str] = typer.Option(None, "--desc", "-d", help="Product description (auto-detected if not provided)"),
    file: Optional[str] = typer.Option(None, "--file", "-f", help="Path to landing page file"),
    output_dir: Optional[str] = typer.Option(None, "--output", "-o", help="Output directory")
):
    """Regenerate specific sections of an existing landing page
    
    Examples:
      ccux regen --section hero
      ccux regen --section hero,features
      ccux regen --all
    """
    
    config = Config()
    output_dir = output_dir or config.get('output_dir', 'output/landing-page')
    
    # Find existing landing page files
    if file:
        if not os.path.exists(file):
            console.print(f"[red]❌ File not found: {file}[/red]")
            raise typer.Exit(1)
        target_file = file
    else:
        found_files = find_landing_page_files(output_dir)
        if not found_files:
            console.print(f"[red]❌ No landing page files found in {output_dir}[/red]")
            console.print("Run [bold]ccux gen[/bold] first to create a landing page")
            raise typer.Exit(1)
        
        # Prefer React if both exist, otherwise use what's available
        if 'react' in found_files:
            target_file = found_files['react']
        else:
            target_file = found_files['html']
    
    console.print(f"[bold blue]🔄 Regenerating sections in: {target_file}[/bold blue]")
    
    # Extract context from existing file
    context = extract_page_context(target_file)
    framework = context['framework']
    theme = context['theme']
    existing_sections = context['sections']
    
    console.print(f"Detected: [green]{framework}[/green] | Theme: [green]{theme}[/green] | Sections: [cyan]{', '.join(existing_sections)}[/cyan]")
    
    # Determine sections to regenerate
    if all:
        sections_to_regen = existing_sections if existing_sections else ['hero', 'features', 'pricing', 'footer']
    elif section:
        sections_to_regen = [s.strip() for s in section.split(',')]
    else:
        console.print("[red]❌ Must specify --section or --all[/red]")
        console.print("Examples:")
        console.print("  [bold]ccux regen --section hero[/bold]")
        console.print("  [bold]ccux regen --section hero,features[/bold]")
        console.print("  [bold]ccux regen --all[/bold]")
        raise typer.Exit(1)
    
    # Get product description
    if not desc:
        # Try to extract from existing metadata or config
        if os.path.exists(os.path.join(output_dir, 'design_analysis.json')):
            try:
                with open(os.path.join(output_dir, 'design_analysis.json'), 'r') as f:
                    analysis = json.load(f)
                    desc = analysis.get('product_understanding', {}).get('problem', 'Landing page product')[:100]
            except:
                pass
        
        if not desc:
            desc = Prompt.ask(
                "[bold]What is this landing page for?[/bold]",
                default="Product landing page",
                show_default=False
            )
    
    console.print(f"Regenerating sections: [bold]{', '.join(sections_to_regen)}[/bold]")
    
    try:
        # Build context for existing page
        other_sections = [s for s in existing_sections if s not in sections_to_regen]
        existing_context = {
            'theme': theme,
            'framework': framework,
            'other_sections': f"Already has: {', '.join(other_sections)}" if other_sections else "No other sections"
        }
        
        # Generate new sections
        prompt = regeneration_prompt(desc, framework, theme, sections_to_regen, existing_context)
        new_sections_content, stats = run_claude_with_progress(
            prompt, 
            f"Regenerating {len(sections_to_regen)} section(s)..."
        )
        
        # Replace sections in the file
        success = replace_sections_in_file(target_file, new_sections_content, sections_to_regen)
        
        if success:
            console.print(f"[bold green]✅ Successfully regenerated {len(sections_to_regen)} section(s)![/bold green]")
            console.print(f"📁 Updated file: [bold]{target_file}[/bold]")
            
            # Update design_analysis.json with regeneration info
            update_design_analysis_for_regen(output_dir, sections_to_regen, desc, stats)
            
            # Show preview instructions
            console.print(f"\n[bold cyan]🌐 Preview your updated page:[/bold cyan]")
            console.print(f"  [bold]cd {os.path.dirname(target_file)}[/bold]")
            console.print("  [bold]python -m http.server 3000[/bold]")
            console.print("  Then open [bold]http://localhost:3000[/bold] in your browser")
        else:
            console.print("[red]❌ Failed to update the landing page file[/red]")
            raise typer.Exit(1)
            
    except Exception as e:
        console.print(f"[red]❌ Error during regeneration: {e}[/red]")
        raise typer.Exit(1)

@app.command()
def theme(
    new_theme: str = typer.Argument(..., help=f"New design theme ({'/'.join(get_theme_choices())})"),
    file: Optional[str] = typer.Option(None, "--file", "-f", help="Path to landing page file"),
    output_dir: Optional[str] = typer.Option(None, "--output", "-o", help="Output directory")
):
    """Change the design theme of an existing landing page
    
    This command re-runs the design system and implementation phases 
    while preserving all research and wireframe data from the original generation.
    
    Examples:
      ccux theme brutalist
      ccux theme playful --file custom/page.html
    """
    
    config = Config()
    output_dir = output_dir or config.get('output_dir', 'output/landing-page')
    
    # Validate theme
    valid_themes = get_theme_choices()
    if new_theme not in valid_themes:
        console.print(f"[red]❌ Invalid theme. Must be one of: {', '.join(valid_themes)}[/red]")
        console.print("\n[bold]Available themes:[/bold]")
        for choice in valid_themes:
            desc = get_theme_description(choice)
            console.print(f"  [cyan]{choice}[/cyan]: {desc}")
        raise typer.Exit(1)
    
    # Find existing landing page files
    if file:
        if not os.path.exists(file):
            console.print(f"[red]❌ File not found: {file}[/red]")
            raise typer.Exit(1)
        target_file = file
    else:
        found_files = find_landing_page_files(output_dir)
        if not found_files:
            console.print(f"[red]❌ No landing page files found in {output_dir}[/red]")
            console.print("Run [bold]ccux gen[/bold] first to create a landing page")
            raise typer.Exit(1)
        
        # Prefer React if both exist, otherwise use what's available
        if 'react' in found_files:
            target_file = found_files['react']
        else:
            target_file = found_files['html']
    
    # Check for design analysis file
    analysis_file = os.path.join(output_dir, 'design_analysis.json')
    if not os.path.exists(analysis_file):
        console.print(f"[red]❌ Design analysis not found: {analysis_file}[/red]")
        console.print("This command requires a landing page generated with full design thinking process")
        console.print("Run [bold]ccux gen --desc 'your product'[/bold] without --no-design-thinking flag")
        raise typer.Exit(1)
    
    # Load existing design analysis
    try:
        with open(analysis_file, 'r') as f:
            analysis_data = json.load(f)
    except Exception as e:
        console.print(f"[red]❌ Error reading design analysis: {e}[/red]")
        raise typer.Exit(1)
    
    # Extract context from existing file
    context = extract_page_context(target_file)
    framework = context['framework']
    current_theme = context['theme']
    
    console.print(f"[bold blue]🎨 Changing theme from {current_theme} to {new_theme}[/bold blue]")
    console.print(f"Target file: [cyan]{target_file}[/cyan]")
    console.print(f"Framework: [green]{framework}[/green]")
    
    # Get product description from analysis
    product_desc = analysis_data.get('product_understanding', {}).get('problem', 'Landing page product')
    if len(product_desc) > 100:
        product_desc = product_desc[:100] + "..."
    
    console.print(f"Product: [cyan]{product_desc}[/cyan]")
    
    try:
        # Get required data from previous phases
        content_strategy = analysis_data.get('content_strategy', {})
        wireframes = analysis_data.get('wireframes', {})
        user_research = analysis_data.get('user_research', {})
        
        # Phase 9: Regenerate Design System with new theme
        console.print(f"\n[bold]Phase 9: Design System ({new_theme} theme)[/bold]")
        prompt = design_system_prompt(product_desc, wireframes, content_strategy, new_theme)
        design_output, _ = run_claude_with_progress(prompt, f"Building {new_theme} design system...")
        design_system = safe_json_parse(design_output)
        
        # Phase 10: High-Fidelity Design with new theme
        console.print(f"\n[bold]Phase 10: High-Fidelity Design ({new_theme} theme)[/bold]")
        prompt = high_fidelity_design_prompt(product_desc, design_system, wireframes, content_strategy)
        hifi_output, _ = run_claude_with_progress(prompt, f"Creating {new_theme} high-fidelity design...")
        hifi_design = safe_json_parse(hifi_output)
        
        # Phase 11: Keep existing copy (no need to regenerate)
        final_copy = analysis_data.get('final_copy', {})
        
        # Phase 12: Implementation with new theme
        console.print(f"\n[bold]Phase 12: Code Implementation ({new_theme} theme)[/bold]")
        design_data = {
            'design_system': design_system,
            'ux_analysis': analysis_data.get('ux_analysis', {}),
            'wireframes': wireframes,
            'content_strategy': content_strategy
        }
        prompt = implementation_prompt(product_desc, final_copy, framework, new_theme, design_data)
        code_output, stats = run_claude_with_progress(prompt, f"Implementing {new_theme} themed page...")
        
        # Save the new themed code
        if framework == 'react':
            with open(target_file, 'w') as f:
                f.write(strip_code_blocks(code_output))
        else:
            with open(target_file, 'w') as f:
                f.write(strip_code_blocks(code_output))
        
        # Update design analysis with new theme data
        analysis_data['design_system'] = design_system
        analysis_data['hifi_design'] = hifi_design
        analysis_data['current_theme'] = new_theme
        analysis_data['last_updated'] = time.strftime('%Y-%m-%d %H:%M:%S')
        
        # Add theme change to history
        if 'theme_history' not in analysis_data:
            analysis_data['theme_history'] = []
        
        theme_record = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'from_theme': current_theme,
            'to_theme': new_theme,
            'usage_stats': stats,
            'method': 'theme_command'
        }
        analysis_data['theme_history'].append(theme_record)
        
        # Save updated analysis
        with open(analysis_file, 'w') as f:
            json.dump(analysis_data, f, indent=2)
        
        console.print(f"[bold green]✅ Successfully changed theme to {new_theme}![/bold green]")
        console.print(f"📁 Updated file: [bold]{target_file}[/bold]")
        console.print(f"📊 Design analysis updated: [bold]{analysis_file}[/bold]")
        
        # Show preview instructions
        console.print(f"\n[bold cyan]🌐 Preview your themed page:[/bold cyan]")
        console.print(f"  [bold]cd {os.path.dirname(target_file)}[/bold]")
        console.print("  [bold]python -m http.server 3000[/bold]")
        console.print("  Then open [bold]http://localhost:3000[/bold] in your browser")
        
    except Exception as e:
        console.print(f"[red]❌ Error during theme change: {e}[/red]")
        raise typer.Exit(1)

@app.command()
def version():
    """Show version information"""
    console.print(f"[bold blue]CCUX v{__version__}[/bold blue]")
    console.print("Claude Code UI Generator")

if __name__ == "__main__":
    app()