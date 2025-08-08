"""
Free AI Hotel Scraper Demo

This demo showcases the intelligent scraper using only free AI models
and services - no paid API keys required!
"""

import asyncio
import os
from pathlib import Path
import time
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

console = Console()

def show_free_ai_features():
    """Show what AI features are available for free"""
    
    console.print(Panel(
        Text("🤖 Free AI Features Overview", style="bold green"),
        subtitle="No API Keys Required!",
        border_style="green"
    ))
    
    # Create a table of free AI features
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("🧠 AI Feature", style="cyan", width=25)
    table.add_column("📊 Model/Service", style="white", width=30)
    table.add_column("💰 Cost", style="green", width=15)
    table.add_column("📈 Capability", style="yellow")
    
    features = [
        ("Semantic Understanding", "Sentence Transformers", "FREE", "Content similarity & meaning"),
        ("Named Entity Recognition", "Hugging Face BERT", "FREE", "Extract contacts, locations"),
        ("Sentiment Analysis", "RoBERTa Sentiment", "FREE", "Content mood scoring"),
        ("Text Statistics", "TextStat Library", "FREE", "Readability & complexity"),
        ("Language Processing", "spaCy", "FREE", "Advanced NLP & parsing"),
        ("Content Classification", "Transformer Models", "FREE", "Smart categorization"),
        ("Confidence Scoring", "Custom Algorithm", "FREE", "Data quality assessment"),
        ("Text Chunking", "Built-in Logic", "FREE", "RAG optimization")
    ]
    
    for feature, model, cost, capability in features:
        table.add_row(feature, model, cost, capability)
    
    console.print(table)
    
    console.print("\n[green]✨ Key Benefits of Free AI:[/green]")
    benefits = [
        "🔓 No API keys or accounts required",
        "💸 Zero ongoing costs",
        "🚀 Models run locally or use free Hugging Face endpoints",
        "🔒 Your data stays private",
        "⚡ Fast processing without rate limits",
        "🌍 Works offline after initial model download"
    ]
    
    for benefit in benefits:
        console.print(f"  {benefit}")

def test_free_ai_components():
    """Test if free AI components are available"""
    
    console.print(Panel(
        Text("🧪 Testing Free AI Components", style="bold blue"),
        border_style="blue"
    ))
    
    components = [
        ("transformers", "🤗 Hugging Face Transformers"),
        ("sentence_transformers", "📊 Sentence Transformers"),
        ("spacy", "🔤 spaCy NLP"),
        ("torch", "🔥 PyTorch"),
        ("textstat", "📈 Text Statistics"),
        ("sklearn", "🤖 Scikit-learn"),
        ("numpy", "🔢 NumPy")
    ]
    
    results = []
    
    for module, description in components:
        try:
            if module == "sklearn":
                import sklearn
            else:
                __import__(module)
            results.append((description, "✅ Available", "Ready to use"))
        except ImportError:
            results.append((description, "❌ Missing", "Install with pip"))
    
    # Display results
    table = Table()
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="white")
    table.add_column("Notes", style="dim")
    
    for description, status, notes in results:
        table.add_row(description, status, notes)
    
    console.print(table)
    
    available_count = len([r for r in results if "✅" in r[1]])
    total_count = len(results)
    
    if available_count == total_count:
        console.print(f"\n[green]🎉 All {total_count} components available! Free AI is ready.[/green]")
        return True
    elif available_count >= 4:  # Core components available
        console.print(f"\n[yellow]⚠️ {available_count}/{total_count} components available. Basic AI features ready.[/yellow]")
        return True
    else:
        console.print(f"\n[red]❌ Only {available_count}/{total_count} components available. Install missing packages.[/red]")
        return False

def show_installation_guide():
    """Show how to install free AI components"""
    
    console.print(Panel(
        Text("📦 Free AI Installation Guide", style="bold yellow"),
        border_style="yellow"
    ))
    
    console.print("\n[bold]Quick Setup (Essential components):[/bold]")
    console.print("```bash")
    console.print("# Create virtual environment")
    console.print("python3 -m venv venv")
    console.print("source venv/bin/activate")
    console.print("")
    console.print("# Install free AI requirements")
    console.print("pip install -r requirements-free-ai.txt")
    console.print("")
    console.print("# Download free spaCy model")
    console.print("python -m spacy download en_core_web_sm")
    console.print("```")
    
    console.print("\n[bold]Minimal Installation (if space is limited):[/bold]")
    console.print("```bash")
    minimal_packages = [
        "transformers",
        "sentence-transformers", 
        "torch",
        "numpy",
        "scikit-learn",
        "spacy"
    ]
    console.print(f"pip install {' '.join(minimal_packages)}")
    console.print("```")
    
    console.print("\n[bold]Optional Enhancements:[/bold]")
    console.print("• Set HUGGINGFACE_TOKEN for faster downloads (free account)")
    console.print("• Configure USE_FREE_AI=true (default)")

async def demo_free_ai_extraction():
    """Demonstrate free AI extraction capabilities"""
    
    console.print(Panel(
        Text("🧠 Free AI Extraction Demo", style="bold magenta"),
        subtitle="No paid APIs required!",
        border_style="magenta"
    ))
    
    # Sample hotel text for demonstration
    sample_text = """
    Welcome to the Grand Plaza Hotel, a luxury 4-star accommodation in downtown San Francisco.
    Check-in is at 3:00 PM and check-out is at 11:00 AM. We offer complimentary WiFi throughout
    the property. Our fitness center is open 24/7 and features state-of-the-art equipment.
    The hotel is pet-friendly with a $50 fee per night. Free valet parking is available.
    Our award-winning restaurant serves breakfast from 6:00 AM to 10:00 AM.
    We're located just 2 blocks from Union Square and 15 minutes from the airport.
    For reservations, call (415) 555-0123 or email info@grandplaza.com.
    """
    
    console.print(f"[dim]Sample text: {sample_text[:100]}...[/dim]\n")
    
    try:
        # Test basic NLP without external dependencies
        console.print("[yellow]🔍 Testing Free AI Extraction...[/yellow]")
        
        # Basic pattern matching (always available)
        import re
        
        extractions = {}
        
        # Phone extraction
        phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phone_match = re.search(phone_pattern, sample_text)
        if phone_match:
            extractions['phone'] = phone_match.group()
        
        # Email extraction
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, sample_text)
        if email_match:
            extractions['email'] = email_match.group()
        
        # Time extraction
        time_pattern = r'\d{1,2}:\d{2}\s*[APap][Mm]'
        times = re.findall(time_pattern, sample_text)
        if times:
            extractions['times'] = times
        
        # Price extraction
        price_pattern = r'\$\d+(?:\.\d{2})?'
        prices = re.findall(price_pattern, sample_text)
        if prices:
            extractions['prices'] = prices
        
        # Keywords extraction
        amenity_keywords = ['wifi', 'fitness', 'parking', 'pet', 'restaurant']
        found_amenities = [keyword for keyword in amenity_keywords if keyword in sample_text.lower()]
        if found_amenities:
            extractions['amenities'] = found_amenities
        
        # Display results
        console.print("[green]✅ Basic Pattern Extraction Results:[/green]")
        for key, value in extractions.items():
            console.print(f"  • {key.title()}: {value}")
        
        # Test advanced AI if available
        try:
            from transformers import pipeline
            
            console.print("\n[green]✅ Advanced AI Available - Testing Sentiment Analysis...[/green]")
            
            # Free sentiment analysis
            sentiment_analyzer = pipeline("sentiment-analysis")
            sentiment_result = sentiment_analyzer(sample_text[:500])  # Limit text length
            
            console.print(f"  • Sentiment: {sentiment_result[0]['label']} ({sentiment_result[0]['score']:.2f})")
            
        except ImportError:
            console.print("\n[yellow]⚠️ Advanced AI not available - install transformers for more features[/yellow]")
        
        # Test spaCy if available
        try:
            import spacy
            nlp = spacy.load("en_core_web_sm")
            
            console.print("\n[green]✅ spaCy Available - Testing Entity Recognition...[/green]")
            
            doc = nlp(sample_text)
            entities = [(ent.text, ent.label_) for ent in doc.ents]
            
            for text, label in entities[:5]:  # Show first 5
                console.print(f"  • {label}: {text}")
                
        except (ImportError, OSError):
            console.print("\n[yellow]⚠️ spaCy not available - install for entity recognition[/yellow]")
        
        return True
        
    except Exception as e:
        console.print(f"[red]❌ Demo failed: {e}[/red]")
        return False

def show_deployment_options():
    """Show deployment options for free AI"""
    
    console.print(Panel(
        Text("☁️ Free AI Deployment Options", style="bold cyan"),
        border_style="cyan"
    ))
    
    options = [
        ("🌊 DigitalOcean App Platform", "Free tier available, automatic scaling", "Recommended"),
        ("🔥 Heroku", "Free tier (limited hours)", "Good for testing"),
        ("☁️ Railway", "Free tier with generous limits", "Developer friendly"),
        ("🐳 Docker + VPS", "Full control, pay for server only", "Advanced users"),
        ("🏠 Local Development", "Completely free", "Development & testing")
    ]
    
    table = Table()
    table.add_column("Platform", style="cyan")
    table.add_column("Features", style="white")
    table.add_column("Best For", style="yellow")
    
    for platform, features, best_for in options:
        table.add_row(platform, features, best_for)
    
    console.print(table)
    
    console.print("\n[bold]Why Free AI Works Great in the Cloud:[/bold]")
    cloud_benefits = [
        "🔄 Models cache after first download",
        "⚡ No external API calls = faster responses",
        "💰 No usage-based costs",
        "🔒 Data stays on your servers",
        "📈 Scales with your traffic"
    ]
    
    for benefit in cloud_benefits:
        console.print(f"  {benefit}")

async def main():
    """Main demo function for free AI features"""
    
    console.print(Panel.fit(
        Text("🤖 FREE AI HOTEL SCRAPER", style="bold white on green"),
        subtitle="No Paid APIs • No Subscriptions • No Limits"
    ))
    
    console.print("\n[bold]What you'll see in this demo:[/bold]")
    demo_items = [
        "🤖 Free AI models and capabilities",
        "🧪 Testing available components",
        "📦 Installation guide",
        "🧠 Live AI extraction demo",
        "☁️ Deployment options"
    ]
    
    for item in demo_items:
        console.print(f"  {item}")
    
    console.print("\n[dim]Press Enter to continue or Ctrl+C to exit...[/dim]")
    try:
        input()
    except KeyboardInterrupt:
        console.print("\n[yellow]Demo cancelled by user.[/yellow]")
        return
    
    # Run the demo sections
    sections = [
        ("Free AI Features", show_free_ai_features),
        ("Component Testing", test_free_ai_components),
        ("Installation Guide", show_installation_guide),
        ("AI Extraction Demo", demo_free_ai_extraction),
        ("Deployment Options", show_deployment_options)
    ]
    
    for section_name, section_func in sections:
        console.clear()
        console.print(f"\n[bold blue]📋 {section_name}[/bold blue]\n")
        
        if asyncio.iscoroutinefunction(section_func):
            await section_func()
        else:
            section_func()
        
        console.print("\n[dim]Press Enter to continue to next section...[/dim]")
        try:
            input()
        except KeyboardInterrupt:
            console.print("\n[yellow]Demo stopped by user.[/yellow]")
            break
    
    # Final summary
    console.clear()
    console.print(Panel(
        Text("🎉 Free AI Demo Complete!", style="bold green"),
        subtitle="Ready to deploy without any paid services",
        border_style="green"
    ))
    
    console.print("\n[bold]🚀 Next Steps:[/bold]")
    next_steps = [
        "1. Install free AI components: pip install -r requirements-free-ai.txt",
        "2. Download spaCy model: python -m spacy download en_core_web_sm",
        "3. Test locally: python demo_intelligent.py",
        "4. Deploy to cloud: ./deploy.sh (DigitalOcean)",
        "5. Enjoy unlimited AI-powered scraping! 🎊"
    ]
    
    for step in next_steps:
        console.print(f"  {step}")
    
    console.print("\n[green]💡 Remember: All AI features work without any API keys or paid subscriptions![/green]")

if __name__ == "__main__":
    # Check if we're in the right directory
    current_dir = Path(__file__).parent
    
    if not (current_dir / "requirements-free-ai.txt").exists():
        console.print("[red]❌ requirements-free-ai.txt not found[/red]")
        console.print("[yellow]Please run this from the project root directory[/yellow]")
    else:
        asyncio.run(main())
