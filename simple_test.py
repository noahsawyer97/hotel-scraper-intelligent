"""
Simple setup verification without external dependencies

This script checks basic setup without requiring additional packages.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*50}")
    print(f" {title}")
    print(f"{'='*50}")

def test_basic_python():
    """Test basic Python functionality"""
    print_section("🐍 Python Environment")
    
    print(f"Python Version: {sys.version}")
    print(f"Python Executable: {sys.executable}")
    
    # Test basic modules
    basic_modules = [
        'json', 'pathlib', 'datetime', 'dataclasses', 
        'asyncio', 'urllib', 'html', 'csv'
    ]
    
    print("\nBuilt-in Modules:")
    for module in basic_modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError:
            print(f"  ❌ {module}")

def test_file_structure():
    """Test file structure"""
    print_section("📁 File Structure")
    
    current_dir = Path(__file__).parent
    
    files_to_check = [
        ("app.yaml", "DigitalOcean configuration"),
        ("app.py", "Flask API server"),
        ("intelligent_scraper.py", "AI-enhanced scraper"),
        ("intelligent_exporter.py", "Data export utilities"),
        ("worker.py", "Background processor"),
        ("deploy.sh", "Deployment script"),
        ("requirements-intelligent.txt", "Enhanced dependencies"),
        ("test_setup.py", "Setup verification"),
        ("demo_intelligent.py", "Demo script")
    ]
    
    print("Required Files:")
    all_present = True
    for filename, description in files_to_check:
        filepath = current_dir / filename
        if filepath.exists():
            size = filepath.stat().st_size
            print(f"  ✅ {filename:<30} ({size:,} bytes) - {description}")
        else:
            print(f"  ❌ {filename:<30} (missing) - {description}")
            all_present = False
    
    return all_present

def test_requirements():
    """Check requirements file"""
    print_section("📦 Dependencies")
    
    req_file = Path(__file__).parent / "requirements-intelligent.txt"
    
    if req_file.exists():
        print("Enhanced requirements file found:")
        with open(req_file, 'r') as f:
            lines = f.readlines()
        
        print(f"  Total dependencies: {len([l for l in lines if l.strip() and not l.startswith('#')])}")
        
        print("\nKey categories:")
        categories = {
            "Basic": ["requests", "beautifulsoup4", "selenium", "pandas"],
            "AI/ML": ["openai", "transformers", "torch", "spacy"],
            "Web": ["flask", "gunicorn", "celery"],
            "Data": ["redis", "sqlalchemy", "jsonlines"],
            "UI": ["rich"]
        }
        
        for category, packages in categories.items():
            found = [pkg for pkg in packages if any(pkg in line for line in lines)]
            print(f"  {category}: {len(found)}/{len(packages)} packages")
            if found:
                print(f"    {', '.join(found)}")
    else:
        print("❌ requirements-intelligent.txt not found")
        return False
    
    return True

def test_deployment_config():
    """Test deployment configuration"""
    print_section("☁️ Deployment Configuration")
    
    app_yaml = Path(__file__).parent / "app.yaml"
    
    if app_yaml.exists():
        print("✅ app.yaml found")
        with open(app_yaml, 'r') as f:
            content = f.read()
        
        # Check key sections
        checks = [
            ("name:", "App name configured"),
            ("services:", "Services defined"),
            ("envs:", "Environment variables"),
            ("databases:", "Database configuration"),
            ("run_command:", "Run command specified")
        ]
        
        for check, description in checks:
            if check in content:
                print(f"  ✅ {description}")
            else:
                print(f"  ⚠️ {description} - may need attention")
    else:
        print("❌ app.yaml not found")
        return False
    
    # Check deploy script
    deploy_script = Path(__file__).parent / "deploy.sh"
    if deploy_script.exists():
        print("✅ deploy.sh found")
        # Check if executable
        import stat
        if deploy_script.stat().st_mode & stat.S_IEXEC:
            print("  ✅ Script is executable")
        else:
            print("  ⚠️ Script not executable (run: chmod +x deploy.sh)")
    else:
        print("❌ deploy.sh not found")
    
    return True

def show_setup_instructions():
    """Show setup instructions"""
    print_section("🚀 Setup Instructions")
    
    print("1. Create Virtual Environment:")
    print("   python3 -m venv venv")
    print("   source venv/bin/activate  # On macOS/Linux")
    print()
    print("2. Install Dependencies:")
    print("   pip install -r requirements-intelligent.txt")
    print()
    print("3. Install AI Models (for full AI features):")
    print("   python -m spacy download en_core_web_sm")
    print()
    print("4. Set Environment Variables:")
    print("   export OPENAI_API_KEY='your_openai_key'")
    print("   export HUGGINGFACE_TOKEN='your_hf_token'  # optional")
    print()
    print("5. Test Locally:")
    print("   python demo_intelligent.py")
    print()
    print("6. Deploy to DigitalOcean:")
    print("   # Install doctl first: brew install doctl")
    print("   doctl auth init")
    print("   ./deploy.sh")

def show_features_summary():
    """Show enhanced features"""
    print_section("🌟 Enhanced Features")
    
    features = [
        "🧠 AI-Enhanced Extraction",
        "  • Semantic understanding with transformer models",
        "  • Named Entity Recognition (NER)",
        "  • Sentiment analysis",
        "  • Confidence scoring",
        "",
        "☁️ Cloud-Native Deployment",
        "  • DigitalOcean App Platform ready",
        "  • Auto-scaling infrastructure",
        "  • Redis caching",
        "  • Background task processing",
        "",
        "📊 Rich Data Export",
        "  • RAG-optimized text format",
        "  • Multiple export formats",
        "  • Rich console visualization",
        "  • Executive summaries",
        "",
        "🔧 Developer Experience",
        "  • Interactive web interface",
        "  • REST API endpoints",
        "  • Health monitoring",
        "  • Error tracking"
    ]
    
    for feature in features:
        print(feature)

def main():
    """Run basic verification"""
    print("🏨 INTELLIGENT HOTEL SCRAPER - Basic Setup Verification")
    print("=" * 60)
    
    # Run tests
    test_basic_python()
    files_ok = test_file_structure()
    req_ok = test_requirements()
    deploy_ok = test_deployment_config()
    
    # Summary
    print_section("📋 Summary")
    
    if files_ok and req_ok and deploy_ok:
        print("✅ Basic setup verification PASSED!")
        print("✅ All required files are present")
        print("✅ Configuration files look good")
        print()
        print("🎯 Ready for virtual environment setup and deployment!")
    else:
        print("⚠️ Some components need attention")
        print("Please check the output above for missing files or configuration issues")
    
    show_features_summary()
    show_setup_instructions()
    
    print("\n" + "="*60)
    print("Next: Follow the setup instructions above to get started!")

if __name__ == "__main__":
    main()
