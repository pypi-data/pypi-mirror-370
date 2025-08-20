
from playwright.sync_api import sync_playwright
import os
from typing import Tuple, List
from urllib.parse import urlparse
import time
import subprocess
from rich import print
from rich.console import Console
from rich.status import Status
from rich.progress import Progress, SpinnerColumn, TextColumn, MofNCompleteColumn

def ensure_chromium_installed() -> bool:
    """Check if Chromium is installed and install if needed"""
    try:
        with sync_playwright() as p:
            # Try to launch browser to check if installed
            browser = p.chromium.launch(headless=True)
            browser.close()
            return True
    except Exception:
        print("[yellow] Chromium not found, installing...[/yellow]")
        try:
            subprocess.run(["python", "-m", "playwright", "install", "chromium"], 
                         check=True, capture_output=True, text=True)
            print("[green] Chromium installed successfully[/green]")
            return True
        except subprocess.CalledProcessError as e:
            print(f"[red] Failed to install Chromium: {e}[/red]")
            return False

def get_browser_options():
    """Get optimized browser launch options"""
    return {
        "headless": True,
        "args": [
            "--disable-blink-features=AutomationControlled",
            "--disable-extensions",
            "--disable-plugins",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            "--disable-features=TranslateUI",
            "--disable-web-security",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
        ]
    }

def get_page_options():
    """Get optimized page options"""
    return {
        "viewport": {"width": 1920, "height": 1080},
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "extra_http_headers": {
            "Accept-Language": "en-US,en;q=0.9"
        }
    }

def handle_modals_and_popups(page):
    """Handle various types of modals and popups"""
    modal_strategies = [
        # Cookie banners - multi-language support
        lambda: page.get_by_role("button", name="Accept").click(timeout=1000),
        lambda: page.get_by_role("button", name="Accept All").click(timeout=1000),
        lambda: page.get_by_role("button", name="Accept Cookies").click(timeout=1000),
        lambda: page.get_by_role("button", name="Aceitar").click(timeout=1000),  # Portuguese
        lambda: page.get_by_role("button", name="Aceptar").click(timeout=1000),  # Spanish
        lambda: page.get_by_role("button", name="Akzeptieren").click(timeout=1000),  # German
        lambda: page.get_by_role("button", name="Accepter").click(timeout=1000),  # French
        
        # Common close patterns
        lambda: page.locator('[aria-label="Close"]').click(timeout=1000),
        lambda: page.locator('[data-dismiss="modal"]').click(timeout=1000),
        lambda: page.locator('.modal-close').click(timeout=1000),
        lambda: page.locator('.close').click(timeout=1000),
        lambda: page.locator('button:has-text("×")').click(timeout=1000),
        lambda: page.locator('button:has-text("✕")').click(timeout=1000),
        
        # Subscription/newsletter dismissals
        lambda: page.get_by_role("button", name="No thanks").click(timeout=1000),
        lambda: page.get_by_role("button", name="Maybe later").click(timeout=1000),
        lambda: page.get_by_role("button", name="Skip").click(timeout=1000),
        lambda: page.locator('[aria-label="Dismiss"]').click(timeout=1000),
        
        # Age verification
        lambda: page.get_by_role("button", name="I am 18 or older").click(timeout=1000),
        lambda: page.get_by_role("button", name="Yes").click(timeout=1000),
        
        # GDPR/Privacy dismissals
        lambda: page.get_by_role("button", name="Agree").click(timeout=1000),
        lambda: page.get_by_role("button", name="Continue").click(timeout=1000),
    ]
    
    for strategy in modal_strategies:
        try:
            strategy()
            page.wait_for_timeout(500)  # Brief pause after dismissal
            break  # Stop after first successful dismissal
        except Exception:
            continue
    
    # Try ESC key as final fallback
    try:
        page.keyboard.press("Escape")
        page.wait_for_timeout(500)
    except Exception:
        pass
    
    # Check for overlay/backdrop elements and try to dismiss
    try:
        overlays = page.locator('.overlay, .modal-backdrop, [style*="z-index"]').all()
        if overlays:
            # Try clicking outside the modal (backdrop click)
            page.locator('body').click(position={"x": 50, "y": 50}, timeout=1000)
    except Exception:
        pass

def capture_screenshot_with_retry(page, screenshot_path: str, max_attempts: int = 3):
    """Capture screenshot with multiple fallback strategies"""
    
    strategies = [
        # Strategy 1: Full page, high quality
        lambda: page.screenshot(path=screenshot_path, full_page=True, quality=80, type="jpeg"),
        
        # Strategy 2: Viewport only, medium quality  
        lambda: page.screenshot(path=screenshot_path, full_page=False, quality=60, type="jpeg"),
        
        # Strategy 3: Focus on main content area
        lambda: capture_main_content_area(page, screenshot_path),
        
        # Strategy 4: Simple fallback
        lambda: page.screenshot(path=screenshot_path, full_page=True, quality=40, type="jpeg"),
    ]
    
    for attempt in range(max_attempts):
        for i, strategy in enumerate(strategies):
            try:
                strategy()
                return  # Success, exit function
            except Exception as e:
                if attempt == max_attempts - 1 and i == len(strategies) - 1:
                    # Last attempt, last strategy - raise the error
                    raise Exception(f"All screenshot strategies failed: {e}")
                continue
        
        # Wait before retry
        page.wait_for_timeout(1000 * (attempt + 1))

def capture_main_content_area(page, screenshot_path: str):
    """Try to capture just the main content area"""
    main_selectors = ['main', '[role="main"]', '.main', '#main', 'article', '.content', '#content']
    
    for selector in main_selectors:
        try:
            element = page.locator(selector).first
            if element.is_visible():
                element.screenshot(path=screenshot_path, quality=70, type="jpeg")
                return
        except Exception:
            continue
    
    # Fallback to viewport screenshot
    page.screenshot(path=screenshot_path, full_page=False, quality=60, type="jpeg")

def get_user_friendly_error(error: Exception, url: str) -> str:
    """Convert technical errors to user-friendly messages"""
    error_str = str(error).lower()
    
    if "timeout" in error_str:
        return f"Site took too long to load: {url}"
    elif "connection" in error_str or "network" in error_str:
        return f"Network connection issue: {url}"  
    elif "403" in error_str or "forbidden" in error_str:
        return f"Site blocked access: {url}"
    elif "404" in error_str or "not found" in error_str:
        return f"Page not found: {url}"
    elif "ssl" in error_str or "certificate" in error_str:
        return f"SSL/Security issue: {url}"
    elif "screenshot" in error_str:
        return f"Screenshot capture failed: {url}"
    else:
        return f"Failed to capture {url}: {error}"

def should_retry_with_fallback(error: Exception) -> bool:
    """Determine if we should attempt fallback capture"""
    error_str = str(error).lower()
    
    # Retry for these types of errors
    fallback_conditions = [
        "timeout",
        "screenshot", 
        "element not found",
        "page crash",
        "navigation",
        "net::err"
    ]
    
    return any(condition in error_str for condition in fallback_conditions)

def attempt_fallback_capture(url: str, screenshot_path: str, browser) -> tuple[str, str] | None:
    """Attempt minimal fallback capture with basic settings"""
    try:
        print(f"     Attempting fallback capture for {url}")
        
        # Create minimal page with basic settings
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        
        # Simple navigation without waiting
        page.goto(url, timeout=15000)
        page.wait_for_timeout(3000)  # Basic wait
        
        # Simple screenshot without retries
        page.screenshot(path=screenshot_path, quality=40, type="jpeg")
        
        dom = page.content()
        page.close()
        
        return (dom, screenshot_path)
        
    except Exception:
        return None

def setup_resource_blocking(page):
    """Set up intelligent resource blocking for faster loading"""
    
    # Block resource types that aren't needed for layout/content analysis
    blocked_resources = [
        'font',      # Web fonts
        'media',     # Videos/audio  
        'other',     # Analytics, tracking
    ]
    
    # Block specific resource patterns
    blocked_patterns = [
        '*google-analytics*',
        '*googletagmanager*', 
        '*facebook.com/tr*',
        '*doubleclick*',
        '*googlesyndication*',
        '*.woff*',
        '*.ttf*',
        '*.mp4*',
        '*.mp3*',
        '*.avi*',
        '*advertisement*',
        '*ads.*'
    ]
    
    def handle_route(route):
        resource_type = route.request.resource_type
        url = route.request.url.lower()
        
        # Block unwanted resource types
        if resource_type in blocked_resources:
            route.abort()
            return
            
        # Block unwanted URL patterns
        for pattern in blocked_patterns:
            if pattern.replace('*', '') in url:
                route.abort()
                return
                
        # Allow everything else
        route.continue_()
    
    page.route('**/*', handle_route)

def capture(url: str, out_dir: str = "output") -> Tuple[str, str]:
    """
    Opens the URL, captures DOM and full-page screenshot.
    Returns (dom_html, screenshot_path).
    """
    os.makedirs(out_dir, exist_ok=True)
    # Save screenshot in parent output directory
    parent_dir = os.path.dirname(out_dir) if out_dir.endswith('landing-page') else out_dir
    screenshot_path = os.path.join(parent_dir, "reference.jpg")
    
    if not ensure_chromium_installed():
        raise Exception("Chromium installation failed")
    
    print(f"[bold blue] Capturing screenshot from {url}...[/bold blue]")
    with sync_playwright() as p:
        browser = p.chromium.launch(**get_browser_options())
        page = browser.new_page(**get_page_options())
    
        # Block unnecessary resources for faster loading
        setup_resource_blocking(page)
        
        # Advanced wait strategies for different site types
        try:
            page.goto(url, wait_until="networkidle", timeout=15000)
            
            # Wait for critical content indicators
            page.wait_for_function("""
            () => {
                // Wait for DOM to be stable
                const body = document.body;
                if (!body || body.children.length === 0) return false;
                
                // Check if main content areas are present
                const contentIndicators = [
                    'main', '[role="main"]', '.main', '#main',
                    'article', '.content', '#content', '.page',
                    'h1', 'h2', '.hero', '.banner'
                ];
                
                return contentIndicators.some(selector => 
                    document.querySelector(selector) !== null
                );
            }
            """, timeout=10000)
            
            # Additional wait for SPAs and dynamic content
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(1000)  # Reduced wait time for animations
            
        except Exception:
            # Fallback to basic loading
            page.goto(url, wait_until="domcontentloaded", timeout=20000)
            page.wait_for_timeout(2000)
            
        # Comprehensive modal/popup handling
        handle_modals_and_popups(page)
        
        dom = page.content()
        # Robust screenshot capture with retry logic
        capture_screenshot_with_retry(page, screenshot_path)
        browser.close()
        
    print(f"[green] Screenshot saved: {os.path.basename(screenshot_path)}[/green]")
    return dom, screenshot_path

def capture_multiple_references(urls: List[str], out_dir: str = "output", max_time_per_site: int = 30) -> List[Tuple[str, str, str]]:
    """
    Capture screenshots from multiple reference URLs with timeout safety.
    Returns list of (url, dom_html, screenshot_path) tuples.
    """
    os.makedirs(out_dir, exist_ok=True)
    results = []
    console = Console()
    
    if not ensure_chromium_installed():
        print("[red] Failed to ensure Chromium installation[/red]")
        return []
    
    print(f"[bold green] Capturing {len(urls)} reference screenshots...[/bold green]")
        
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        MofNCompleteColumn(),
        console=console,
        transient=False
    ) as progress:
        task = progress.add_task("Capturing references", total=len(urls))
        
        with sync_playwright() as p:
            browser = p.chromium.launch(**get_browser_options())
            
            for i, url in enumerate(urls):
                try:
                    progress.update(task, description=f"[bold green] Capturing {url}...[/bold green]")
                    
                    # Create unique filename for each site
                    domain = urlparse(url).netloc.replace("www.", "").replace(".", "_")
                    # Save screenshot in parent output directory
                    parent_dir = os.path.dirname(out_dir) if out_dir.endswith('landing-page') else out_dir
                    screenshot_path = os.path.join(parent_dir, f"reference_{i+1}_{domain}.jpg")
                    
                    page = browser.new_page(**get_page_options())
                    
                    # Block unnecessary resources for faster loading  
                    setup_resource_blocking(page)
                    
                    # Advanced wait strategies for different site types
                    try:
                        page.goto(url, wait_until="networkidle", timeout=15000)
                        
                        # Wait for critical content indicators
                        page.wait_for_function("""
                            () => {
                                // Wait for DOM to be stable
                                const body = document.body;
                                if (!body || body.children.length === 0) return false;
                                
                                // Check if main content areas are present
                                const contentIndicators = [
                                    'main', '[role="main"]', '.main', '#main',
                                    'article', '.content', '#content', '.page',
                                    'h1', 'h2', '.hero', '.banner'
                                ];
                                
                                return contentIndicators.some(selector => 
                                    document.querySelector(selector) !== null
                                );
                            }
                        """, timeout=10000)
                        
                        # Additional wait for SPAs and dynamic content
                        page.wait_for_load_state("domcontentloaded")
                        page.wait_for_timeout(1000)  # Reduced wait time for animations
                        
                    except Exception:
                        # Fallback to basic loading
                        page.goto(url, wait_until="domcontentloaded", timeout=20000)
                        page.wait_for_timeout(2000)
                    
                    # Comprehensive modal/popup handling
                    handle_modals_and_popups(page)
                    
                    dom = page.content()
                    # Robust screenshot capture with retry logic
                    capture_screenshot_with_retry(page, screenshot_path)
                    page.close()
                    
                    results.append((url, dom, screenshot_path))
                    
                    # Memory cleanup
                    del dom  # Free up DOM content memory
                    progress.advance(task)
                    progress.update(task, description=f"[bold green] Captured {os.path.basename(screenshot_path)}[/bold green]")
                    time.sleep(0.3)  # Brief pause to show success
                    
                    # Small delay between captures (reduced for performance)
                    time.sleep(0.5)
                    
                except Exception as e:
                    error_msg = get_user_friendly_error(e, url)
                    print(f"     {error_msg}")
                    
                    # Attempt graceful cleanup
                    try:
                        if 'page' in locals():
                            page.close()
                    except:
                        pass
                    
                    # Try fallback capture for certain error types  
                    if should_retry_with_fallback(e):
                        progress.update(task, description=f"[yellow] Trying fallback for {url}...[/yellow]")
                        fallback_result = attempt_fallback_capture(url, screenshot_path, browser)
                        if fallback_result:
                            dom, screenshot_path = fallback_result
                            results.append((url, dom, screenshot_path))
                            progress.advance(task)
                            progress.update(task, description=f"[bold green] Fallback succeeded: {os.path.basename(screenshot_path)}[/bold green]")
                            time.sleep(0.3)
                            continue
                    
                    progress.advance(task)  # Advance even on failure
                    
                    continue
                
            browser.close()
    
    if results:
        print(f"[bold green] Successfully captured {len(results)} of {len(urls)} reference sites[/bold green]")
    else:
        print("[red] Failed to capture any reference sites[/red]")
    
    return results
