#!/usr/bin/env python3

import sys
import os
import subprocess
sys.path.insert(0, 'src')

def test_cli_generation():
    """Test the CLI with a simple generation"""
    print("🧪 Testing CLI Generation...\n")
    
    # Clean up any existing output
    if os.path.exists("test_output"):
        import shutil
        shutil.rmtree("test_output")
    
    try:
        # Test with simple generation (no design thinking)
        cmd = [
            sys.executable, "-m", "src.ccux.cli", "gen",
            "--desc", "Simple test app for developers", 
            "--no-design-thinking",
            "--framework", "html",
            "--theme", "minimal",
            "--output-dir", "test_output"
        ]
        
        print("🚀 Running command:")
        print(f"   {' '.join(cmd)}")
        print()
        
        # Run the command
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        print("📤 STDOUT:")
        print(result.stdout)
        print()
        
        if result.stderr:
            print("📥 STDERR:")
            print(result.stderr)
            print()
        
        print(f"🔢 Return code: {result.returncode}")
        
        # Check if files were created
        if os.path.exists("test_output/index.html"):
            with open("test_output/index.html", "r") as f:
                content = f.read()
            if len(content) > 100:
                print(f"✅ HTML file created: {len(content)} characters")
                return True
            else:
                print(f"❌ HTML file is empty or too small: {len(content)} characters")
        else:
            print("❌ HTML file was not created")
            
        return False
        
    except subprocess.TimeoutExpired:
        print("❌ Command timed out (>2 minutes)")
        return False
    except Exception as e:
        print(f"❌ Command failed: {e}")
        return False

if __name__ == "__main__":
    success = test_cli_generation()
    
    if success:
        print("\n🎉 CLI generation works!")
        print("🔧 The issue with your blank HTML file should now be resolved")
    else:
        print("\n❌ CLI generation failed") 
        print("💡 This explains why your HTML file was blank")
        
        
        
        
