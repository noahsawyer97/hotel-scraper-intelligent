#!/usr/bin/env python3
"""
OpenAI-Enhanced Hotel Scraper Demo

This demo showcases the enhanced intelligent scraper with OpenAI API integration
for superior data extraction quality.
"""

import os
import sys
import asyncio
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from intelligent_scraper import IntelligentHotelScraper

console = Console()

def check_environment():
    """Check if OpenAI API key is configured"""
    console.print("\n🔍 [bold cyan]Checking Environment Configuration...[/bold cyan]")
    
    # Load environment variables
    env_files = ['.env.production', '.env']
    for env_file in env_files:
        if os.path.exists(env_file):
            load_dotenv(env_file)
            console.print(f"✅ Loaded {env_file}")
            break
    else:
        console.print("⚠️  No .env file found")
    
    # Check OpenAI configuration
    openai_key = os.getenv('OPENAI_API_KEY')
    use_openai = os.getenv('USE_OPENAI_API', 'false').lower() == 'true'
    
    table = Table(title="Environment Status")
    table.add_column("Setting", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Value", style="yellow")
    
    table.add_row("OPENAI_API_KEY", "✅ Set" if openai_key else "❌ Missing", 
                  f"sk-...{openai_key[-8:]}" if openai_key else "Not configured")
    table.add_row("USE_OPENAI_API", "✅ Enabled" if use_openai else "❌ Disabled", 
                  str(use_openai))
    table.add_row("USE_FREE_AI", "✅ Enabled" if os.getenv('USE_FREE_AI', 'true').lower() == 'true' else "❌ Disabled",
                  os.getenv('USE_FREE_AI', 'true'))
    
    console.print(table)
    
    if not openai_key:
        console.print(Panel(
            "[red]⚠️  OpenAI API Key not found![/red]\n\n"
            "To use OpenAI-enhanced extraction:\n"
            "1. Copy .env.example to .env.production\n"
            "2. Add your OpenAI API key: OPENAI_API_KEY=sk-your-key-here\n"
            "3. Set USE_OPENAI_API=true\n\n"
            "The demo will run with free AI models only.",
            title="Configuration Warning"
        ))
        return False
    
    return True

async def demo_extraction_comparison():
    """Demo comparing OpenAI vs traditional extraction"""
    console.print("\n🚀 [bold green]Starting OpenAI-Enhanced Hotel Scraper Demo[/bold green]")
    
    # Test URLs (use sites that allow scraping)
    test_urls = [
        "https://www.example-hotel.com",  # Replace with actual hotel website
        # Add more test URLs here
    ]
    
    # For demo purposes, let's use a simplified test
    console.print("\n📝 [bold yellow]Demo Mode: Simulated Extraction[/bold yellow]")
    console.print("(Replace test_urls with real hotel websites for actual testing)")
    
    # Initialize scraper
    scraper = IntelligentHotelScraper(headless=True, use_ai=True)
    
    try:
        # Display scraper configuration
        table = Table(title="Scraper Configuration")
        table.add_column("Feature", style="cyan")
        table.add_column("Status", style="green")
        
        table.add_row("OpenAI Integration", "✅ Available" if hasattr(scraper, 'USE_OPENAI_API') else "❌ Not Available")
        table.add_row("Free AI Models", "✅ Available" if scraper.use_ai else "❌ Disabled")
        table.add_row("Browser Mode", "Headless" if scraper.headless else "Visible")
        
        console.print(table)
        
        # Simulated extraction results
        console.print("\n🔬 [bold blue]Extraction Quality Comparison[/bold blue]")
        
        comparison_table = Table(title="OpenAI vs Traditional Extraction")
        comparison_table.add_column("Data Field", style="cyan")
        comparison_table.add_column("Traditional Method", style="yellow")
        comparison_table.add_column("OpenAI Method", style="green")
        comparison_table.add_column("Improvement", style="magenta")
        
        comparisons = [
            ("Hotel Name", "Grand Hotel & Spa...", "Grand Hotel & Spa", "✅ Cleaned"),
            ("Phone", "(555) 123-4567 ext 123", "(555) 123-4567", "✅ Formatted"),
            ("Address", "123 Main St Downtown", "123 Main St, Downtown, CA 90210", "✅ Complete"),
            ("Check-in", "3PM", "3:00 PM", "✅ Standardized"),
            ("Amenities", "pool gym wifi", "Swimming Pool, Fitness Center, Free WiFi", "✅ Detailed"),
            ("Policies", "cancel 24h", "Cancellation allowed up to 24 hours before arrival", "✅ Descriptive")
        ]
        
        for field, traditional, openai_result, improvement in comparisons:
            comparison_table.add_row(field, traditional, openai_result, improvement)
        
        console.print(comparison_table)
        
        # Show cost and quality benefits
        console.print("\n💡 [bold cyan]Benefits of OpenAI Integration:[/bold cyan]")
        benefits = [
            "🎯 Higher accuracy in data extraction",
            "🔧 Better data formatting and standardization", 
            "🌍 Natural language understanding of policies",
            "⚡ Faster processing of complex content",
            "📊 Structured JSON output with validation",
            "🔍 Context-aware information extraction"
        ]
        
        for benefit in benefits:
            console.print(f"  {benefit}")
            
        console.print("\n💰 [bold yellow]Cost Considerations:[/bold yellow]")
        console.print("  • OpenAI API: ~$0.001-0.002 per hotel page")
        console.print("  • Improved accuracy: Fewer manual corrections needed")
        console.print("  • Time savings: Structured output ready for RAG systems")
        
    except Exception as e:
        console.print(f"\n❌ [bold red]Demo Error:[/bold red] {e}")
    finally:
        if scraper.driver:
            scraper.driver.quit()

def main():
    """Main demo function"""
    console.print(Panel(
        "[bold green]🏨 OpenAI-Enhanced Hotel Scraper Demo[/bold green]\n\n"
        "This demo showcases the enhanced intelligent scraper with OpenAI API integration.",
        title="Hotel Scraper Demo"
    ))
    
    # Check environment
    env_ok = check_environment()
    
    # Run extraction demo
    asyncio.run(demo_extraction_comparison())
    
    console.print("\n✅ [bold green]Demo completed![/bold green]")
    
    if not env_ok:
        console.print("\n🔧 [bold cyan]To enable full OpenAI features:[/bold cyan]")
        console.print("1. Get an OpenAI API key from https://platform.openai.com/")
        console.print("2. Copy .env.example to .env.production")
        console.print("3. Add your API key: OPENAI_API_KEY=sk-your-key-here")
        console.print("4. Set USE_OPENAI_API=true")
        console.print("5. Re-run this demo")

if __name__ == "__main__":
    main()
