"""
Quick test script for the intelligent scraper setup

This script verifies that all components are properly configured
without requiring extensive setup or API keys.
"""

import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()

def test_imports():
    """Test if all required modules can be imported"""
    console.print(Panel("🧪 Testing Module Imports", border_style="blue"))
    
    imports_to_test = [
        ("requests", "Basic HTTP requests"),
        ("beautifulsoup4", "HTML parsing"),
        ("selenium", "Web browser automation"),
        ("pandas", "Data processing"),
        ("rich", "Rich text formatting"),
        ("flask", "Web framework"),
        ("dataclasses", "Data structures"),
        ("asyncio", "Async processing"),
        ("json", "JSON handling"),
        ("pathlib", "File path handling")
    ]
    
    results = []
    
    for module, description in imports_to_test:
        try:
            if module == "beautifulsoup4":
                import bs4
            elif module == "dataclasses":
                import dataclasses
            elif module == "pathlib":
                import pathlib
            else:
                __import__(module)
            results.append((module, "✅ Available", description))
        except ImportError:
            results.append((module, "❌ Missing", description))
    
    # Display results
    table = Table()
    table.add_column("Module", style="cyan")
    table.add_column("Status", style="white")
    table.add_column("Description", style="dim")
    
    for module, status, description in results:
        table.add_row(module, status, description)
    
    console.print(table)
    
    missing_modules = [r[0] for r in results if "❌" in r[1]]
    if missing_modules:
        console.print(f"\n[red]Missing modules: {', '.join(missing_modules)}[/red]")
        console.print("[yellow]Install with: pip install -r requirements-intelligent.txt[/yellow]")
        return False
    else:
        console.print("\n[green]✅ All basic modules available![/green]")
        return True

def test_ai_imports():
    """Test AI-related imports (optional)"""
    console.print(Panel("🤖 Testing AI Module Imports (Optional)", border_style="yellow"))
    
    ai_imports = [
        ("openai", "OpenAI API client"),
        ("transformers", "Hugging Face transformers"),
        ("torch", "PyTorch"),
        ("sentence_transformers", "Sentence embeddings"),
        ("spacy", "Advanced NLP"),
        ("textstat", "Text statistics"),
    ]
    
    ai_results = []
    
    for module, description in ai_imports:
        try:
            __import__(module)
            ai_results.append((module, "✅ Available", description))
        except ImportError:
            ai_results.append((module, "⚠️ Optional", description))
    
    # Display AI results
    table = Table()
    table.add_column("AI Module", style="cyan")
    table.add_column("Status", style="white")
    table.add_column("Description", style="dim")
    
    for module, status, description in ai_results:
        table.add_row(module, status, description)
    
    console.print(table)
    
    available_ai = [r[0] for r in ai_results if "✅" in r[1]]
    if available_ai:
        console.print(f"\n[green]AI modules available: {', '.join(available_ai)}[/green]")
    else:
        console.print("\n[yellow]No AI modules found. AI features will be disabled.[/yellow]")
        console.print("[dim]This is normal for basic setup. AI features are optional.[/dim]")

def test_file_structure():
    """Test if all required files are present"""
    console.print(Panel("📁 Testing File Structure", border_style="green"))
    
    current_dir = Path(__file__).parent
    
    required_files = [
        ("app.yaml", "DigitalOcean configuration", True),
        ("app.py", "Flask API server", True),
        ("intelligent_scraper.py", "AI-enhanced scraper", True),
        ("intelligent_exporter.py", "Data export utilities", True),
        ("worker.py", "Background task processor", True),
        ("deploy.sh", "Deployment script", True),
        ("requirements-intelligent.txt", "Enhanced dependencies", True),
        (".env.production", "Production environment", False),
        ("hotel_scraper.py", "Original scraper", False),
        ("README-Intelligent.md", "Enhanced documentation", False)
    ]
    
    table = Table()
    table.add_column("File", style="cyan")
    table.add_column("Status", style="white")
    table.add_column("Description", style="dim")
    table.add_column("Required", style="yellow")
    
    all_required_present = True
    
    for filename, description, required in required_files:
        filepath = current_dir / filename
        if filepath.exists():
            status = "✅ Present"
        else:
            status = "❌ Missing"
            if required:
                all_required_present = False
        
        req_text = "Required" if required else "Optional"
        table.add_row(filename, status, description, req_text)
    
    console.print(table)
    
    if all_required_present:
        console.print("\n[green]✅ All required files present![/green]")
        return True
    else:
        console.print("\n[red]❌ Some required files are missing![/red]")
        return False

def test_basic_functionality():
    """Test basic scraper functionality without external dependencies"""
    console.print(Panel("⚙️ Testing Basic Functionality", border_style="magenta"))
    
    try:
        from dataclasses import dataclass, asdict
        from datetime import datetime
        
        # Test data structure
        @dataclass
        class TestHotelInfo:
            hotel_name: str
            scraped_at: str
            confidence_score: float = 0.0
        
        test_hotel = TestHotelInfo(
            hotel_name="Test Hotel",
            scraped_at=datetime.now().isoformat(),
            confidence_score=0.95
        )
        
        # Test serialization
        test_dict = asdict(test_hotel)
        
        console.print("✅ Data structures working")
        console.print("✅ JSON serialization working")
        console.print("✅ Date/time handling working")
        
        # Test file operations
        test_file = Path(__file__).parent / "test_output.json"
        import json
        with open(test_file, 'w') as f:
            json.dump(test_dict, f, indent=2, default=str)
        
        if test_file.exists():
            test_file.unlink()  # Clean up
            console.print("✅ File operations working")
        
        console.print("\n[green]✅ Basic functionality tests passed![/green]")
        return True
        
    except Exception as e:
        console.print(f"\n[red]❌ Basic functionality test failed: {e}[/red]")
        return False

def show_next_steps():
    """Show next steps based on test results"""
    console.print(Panel("🚀 Next Steps", border_style="cyan"))
    
    steps = [
        "1. 📦 Install missing dependencies:",
        "   pip install -r requirements-intelligent.txt",
        "",
        "2. 🤖 For AI features, get API keys:",
        "   - OpenAI API key (required for AI features)",
        "   - Hugging Face token (optional)",
        "",
        "3. 🧪 Test locally:",
        "   python demo_intelligent.py",
        "",
        "4. ☁️ Deploy to DigitalOcean:",
        "   - Install doctl CLI",
        "   - Run: doctl auth init",
        "   - Run: ./deploy.sh",
        "",
        "5. 🔧 Configure environment variables in DO dashboard:",
        "   - OPENAI_API_KEY",
        "   - HUGGINGFACE_TOKEN (optional)",
        "   - SENTRY_DSN (optional)"
    ]
    
    for step in steps:
        console.print(step)

def main():
    """Run all tests"""
    console.print(Panel.fit(
        Text("🧪 INTELLIGENT HOTEL SCRAPER", style="bold white on blue"),
        subtitle="Setup Verification & Test Suite"
    ))
    
    console.print("\n[bold]Running setup verification tests...[/bold]\n")
    
    # Run tests
    basic_imports_ok = test_imports()
    console.print()
    
    test_ai_imports()
    console.print()
    
    files_ok = test_file_structure()
    console.print()
    
    functionality_ok = test_basic_functionality()
    console.print()
    
    # Overall results
    if basic_imports_ok and files_ok and functionality_ok:
        console.print(Panel(
            Text("🎉 Setup verification PASSED!", style="bold green"),
            subtitle="Ready for development and deployment",
            border_style="green"
        ))
    else:
        console.print(Panel(
            Text("⚠️ Setup verification INCOMPLETE", style="bold yellow"),
            subtitle="Some components need attention",
            border_style="yellow"
        ))
    
    show_next_steps()

if __name__ == "__main__":
    main()
