from playwright.sync_api import sync_playwright
import os
from typing import Tuple, List
from urllib.parse import urlparse
import time
import subprocess
from rich import print

def ensure_chromium_installed() -> bool:
    """Check if Chromium is installed and install if needed"""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            browser.close()
            return True
    except Exception:
        print("[yellow]Chromium not found, installing...[/yellow]")
        try:
            subprocess.run(["python", "-m", "playwright", "install", "chromium"], 
                         check=True, capture_output=True, text=True)
            print("[green]Chromium installed successfully[/green]")
            return True
        except subprocess.CalledProcessError as e:
            print(f"[red]Failed to install Chromium: {e}[/red]")
            return False

def capture(url: str, out_dir: str = "output") -> Tuple[str, str]:
    """Simple capture without complex progress bars"""
    os.makedirs(out_dir, exist_ok=True)
    # Save screenshot in parent output directory
    parent_dir = os.path.dirname(out_dir) if out_dir.endswith('landing-page') else out_dir
    screenshot_path = os.path.join(parent_dir, "reference.jpg")
    
    if not ensure_chromium_installed():
        raise Exception("Chromium installation failed")
    
    print(f"Capturing {url}...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        
        try:
            page.goto(url, wait_until="networkidle", timeout=10000)
            page.wait_for_timeout(1000)
        except Exception:
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=8000)
                page.wait_for_timeout(1000)
            except Exception as e:
                browser.close()
                raise Exception(f"Failed to load {url}: {e}")
        
        # Handle common popups
        try:
            page.get_by_role("button", name="Accept").click(timeout=1000)
        except:
            pass
        
        dom = page.content()
        page.screenshot(path=screenshot_path, full_page=True, quality=80, type="jpeg")
        browser.close()
        
    print(f"Screenshot saved: {os.path.basename(screenshot_path)}")
    return dom, screenshot_path

def capture_multiple_references(urls: List[str], out_dir: str = "output", max_time_per_site: int = 30) -> List[Tuple[str, str, str]]:
    """Simple multiple capture without complex progress bars"""
    os.makedirs(out_dir, exist_ok=True)
    results = []
    
    if not ensure_chromium_installed():
        return []
        
    print(f"Capturing {len(urls)} reference screenshots...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        for i, url in enumerate(urls):
            try:
                print(f"  Capturing {i+1}/{len(urls)}: {url}")
                
                domain = urlparse(url).netloc.replace("www.", "").replace(".", "_")
                # Save screenshot in parent output directory
                parent_dir = os.path.dirname(out_dir) if out_dir.endswith('landing-page') else out_dir
                screenshot_path = os.path.join(parent_dir, f"reference_{i+1}_{domain}.jpg")
                
                page = browser.new_page(viewport={"width": 1920, "height": 1080})
                
                try:
                    page.goto(url, wait_until="networkidle", timeout=8000)
                    page.wait_for_timeout(1000)
                except Exception:
                    try:
                        page.goto(url, wait_until="domcontentloaded", timeout=6000)
                        page.wait_for_timeout(1000)
                    except Exception as e:
                        print(f"    Failed to load {url}: {e}")
                        continue
                
                # Handle common popups
                try:
                    page.get_by_role("button", name="Accept").click(timeout=1000)
                except:
                    pass
                
                dom = page.content()
                page.screenshot(path=screenshot_path, full_page=True, quality=80, type="jpeg")
                page.close()
                
                results.append((url, dom, screenshot_path))
                print(f"    Saved: {os.path.basename(screenshot_path)}")
                
                time.sleep(0.5)  # Brief pause between captures
                
            except Exception as e:
                print(f"    Failed to capture {url}: {e}")
                try:
                    page.close()
                except:
                    pass
                continue
        
        browser.close()
    
    print(f"Successfully captured {len(results)} of {len(urls)} reference sites")
    return results