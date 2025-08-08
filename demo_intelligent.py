"""
Demo script for the Intelligent Hotel Scraper

This script demonstrates the enhanced capabilities of the AI-powered
hotel scraper with DigitalOcean deployment features.
"""

import asyncio
import os
from pathlib import Path
import time
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

# Import our enhanced modules
from intelligent_scraper import IntelligentHotelScraper
from intelligent_exporter import IntelligentDataExporter

console = Console()

async def demo_intelligent_scraper():
    """Demonstrate the intelligent scraper capabilities"""
    
    console.print(Panel(
        Text("🧠 Intelligent Hotel Scraper Demo", style="bold cyan"),
        subtitle="AI-Enhanced Web Scraping for Hotels",
        border_style="cyan"
    ))
    
    # Sample hotels for demonstration
    demo_hotels = [
        {
            "url": "https://www.marriott.com",
            "name": "Marriott Hotels (Demo)",
            "description": "Large hotel chain - test basic extraction"
        },
        {
            "url": "https://www.hilton.com",
            "name": "Hilton Hotels (Demo)",
            "description": "International hotel brand - test amenity detection"
        }
    ]
    
    # Initialize scraper and exporter
    console.print("\n[yellow]Initializing AI-enhanced scraper...[/yellow]")
    scraper = IntelligentHotelScraper(headless=True, use_ai=True)
    exporter = IntelligentDataExporter()
    
    try:
        for i, hotel in enumerate(demo_hotels):
            console.print(f"\n[bold blue]Demo {i+1}: {hotel['name']}[/bold blue]")
            console.print(f"[dim]{hotel['description']}[/dim]")
            console.print(f"[dim]URL: {hotel['url']}[/dim]")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TimeElapsedColumn(),
                console=console
            ) as progress:
                
                task = progress.add_task("Processing...", total=100)
                
                try:
                    # Scrape the hotel
                    progress.update(task, advance=20, description="Loading website...")
                    hotel_data = await scraper.scrape_hotel_intelligent(
                        hotel['url'], 
                        hotel['name']
                    )
                    
                    progress.update(task, advance=50, description="AI analysis...")
                    
                    # Display rich summary
                    console.print(f"\n[green]✅ Successfully scraped {hotel['name']}[/green]")
                    exporter.display_rich_summary(hotel_data)
                    
                    progress.update(task, advance=20, description="Exporting data...")
                    
                    # Export in multiple formats
                    exported_files = exporter.export_hotel_data(
                        hotel_data, 
                        formats=["json", "rag_text", "summary"]
                    )
                    
                    progress.update(task, advance=10, description="Complete!")
                    
                    console.print(f"\n[cyan]📁 Exported files:[/cyan]")
                    for format_type, filepath in exported_files.items():
                        console.print(f"  • {format_type.upper()}: {filepath}")
                    
                    # Show key insights
                    if hotel_data.key_selling_points:
                        console.print(f"\n[yellow]🌟 AI Insights:[/yellow]")
                        for point in hotel_data.key_selling_points:
                            console.print(f"  • {point}")
                    
                    console.print(f"\n[green]Data Quality Score: {hotel_data.confidence_score:.0%}[/green]")
                    
                except Exception as e:
                    console.print(f"[red]❌ Failed to scrape {hotel['name']}: {str(e)}[/red]")
                
                # Wait between demos
                if i < len(demo_hotels) - 1:
                    console.print("\n[dim]Waiting before next demo...[/dim]")
                    await asyncio.sleep(3)
    
    finally:
        scraper.close()
    
    console.print(Panel(
        Text("🎉 Demo completed! Check the exported files.", style="bold green"),
        border_style="green"
    ))

def demo_api_features():
    """Demonstrate API features for DigitalOcean deployment"""
    
    console.print(Panel(
        Text("🚀 DigitalOcean API Features", style="bold magenta"),
        subtitle="Cloud Deployment Capabilities",
        border_style="magenta"
    ))
    
    console.print("\n[yellow]API Endpoints Available:[/yellow]")
    
    endpoints = [
        ("GET", "/", "Interactive web interface"),
        ("GET", "/api/v1/health", "Health check and system status"),
        ("POST", "/api/v1/scrape", "Scrape single hotel (async)"),
        ("POST", "/api/v1/scrape/batch", "Scrape multiple hotels"),
        ("GET", "/api/v1/task/{id}", "Check task status and results")
    ]
    
    for method, endpoint, description in endpoints:
        method_color = "green" if method == "GET" else "red"
        console.print(f"  [{method_color}]{method:4}[/{method_color}] [cyan]{endpoint:25}[/cyan] {description}")
    
    console.print("\n[yellow]Cloud Infrastructure:[/yellow]")
    
    infrastructure = [
        "🔄 Auto-scaling with DigitalOcean App Platform",
        "⚡ Redis caching for fast responses",
        "🔧 Celery workers for background processing",
        "📊 Prometheus metrics and monitoring",
        "🛡️ Sentry error tracking",
        "🔒 Environment-based configuration"
    ]
    
    for feature in infrastructure:
        console.print(f"  {feature}")
    
    console.print("\n[yellow]AI Enhancement Features:[/yellow]")
    
    ai_features = [
        "🧠 Transformer models for semantic understanding",
        "🔍 Named Entity Recognition (NER)",
        "😊 Sentiment analysis of content",
        "⭐ Confidence scoring for data quality",
        "🎯 Smart categorization and insights",
        "📝 RAG-optimized text generation"
    ]
    
    for feature in ai_features:
        console.print(f"  {feature}")

def demo_deployment_instructions():
    """Show deployment instructions"""
    
    console.print(Panel(
        Text("🛠️ Deployment Instructions", style="bold blue"),
        subtitle="Getting Started with DigitalOcean",
        border_style="blue"
    ))
    
    steps = [
        ("1️⃣", "Install DigitalOcean CLI", "brew install doctl"),
        ("2️⃣", "Authenticate", "doctl auth init"),
        ("3️⃣", "Deploy application", "./deploy.sh"),
        ("4️⃣", "Set environment variables", "Configure in DO dashboard"),
        ("5️⃣", "Monitor deployment", "doctl apps get $APP_ID")
    ]
    
    console.print("\n[yellow]Quick Setup:[/yellow]")
    for step, description, command in steps:
        console.print(f"  {step} [bold]{description}[/bold]")
        console.print(f"     [dim]$ {command}[/dim]")
    
    console.print("\n[yellow]Required Environment Variables:[/yellow]")
    env_vars = [
        ("OPENAI_API_KEY", "Your OpenAI API key for AI features", "Required"),
        ("HUGGINGFACE_TOKEN", "Hugging Face token for models", "Optional"),
        ("SENTRY_DSN", "Error tracking service", "Optional"),
        ("REDIS_URL", "Caching service", "Auto-configured")
    ]
    
    for var, description, status in env_vars:
        status_color = "red" if status == "Required" else "yellow" if status == "Optional" else "green"
        console.print(f"  • [cyan]{var}[/cyan]: {description}")
        console.print(f"    [{status_color}]{status}[/{status_color}]")

def show_file_structure():
    """Display the project file structure"""
    
    console.print(Panel(
        Text("📁 Enhanced Project Structure", style="bold yellow"),
        border_style="yellow"
    ))
    
    # Get actual files in the directory
    current_dir = Path(__file__).parent
    
    important_files = [
        ("app.yaml", "DigitalOcean App Platform configuration"),
        ("app.py", "Flask API server with web interface"),
        ("intelligent_scraper.py", "AI-enhanced scraper engine"),
        ("intelligent_exporter.py", "Advanced data export utilities"),
        ("worker.py", "Background task processor"),
        ("deploy.sh", "Automated deployment script"),
        ("requirements-intelligent.txt", "Enhanced Python dependencies"),
        (".env.production", "Production environment template")
    ]
    
    console.print("\n[yellow]🆕 New Files (Intelligent Version):[/yellow]")
    for filename, description in important_files:
        filepath = current_dir / filename
        exists = "✅" if filepath.exists() else "❌"
        console.print(f"  {exists} [cyan]{filename:30}[/cyan] {description}")
    
    console.print("\n[yellow]📊 Enhanced Capabilities:[/yellow]")
    capabilities = [
        "🧠 AI-powered content understanding",
        "☁️ Cloud-native deployment ready",
        "⚡ Async processing and caching",
        "📈 Monitoring and health checks",
        "🔄 Background task queues",
        "📊 Rich data visualization",
        "🎯 RAG-optimized text output"
    ]
    
    for capability in capabilities:
        console.print(f"  {capability}")

async def main():
    """Main demo function"""
    
    console.print(Panel.fit(
        Text("🏨 INTELLIGENT HOTEL SCRAPER", style="bold white on blue"),
        subtitle="Enhanced AI + DigitalOcean Cloud Deployment"
    ))
    
    # Show what we're going to demo
    console.print("\n[bold]This demo will showcase:[/bold]")
    demo_items = [
        "🧠 AI-enhanced hotel data extraction",
        "📊 Rich data visualization and export",
        "🚀 DigitalOcean deployment features",
        "📁 Enhanced project structure"
    ]
    
    for item in demo_items:
        console.print(f"  {item}")
    
    console.print("\n[dim]Press Enter to continue or Ctrl+C to exit...[/dim]")
    try:
        input()
    except KeyboardInterrupt:
        console.print("\n[yellow]Demo cancelled by user.[/yellow]")
        return
    
    # Run the demos
    console.clear()
    
    # 1. Show file structure
    show_file_structure()
    input("\nPress Enter to continue...")
    console.clear()
    
    # 2. Demo API features
    demo_api_features()
    input("\nPress Enter to continue...")
    console.clear()
    
    # 3. Show deployment instructions
    demo_deployment_instructions()
    input("\nPress Enter to continue...")
    console.clear()
    
    # 4. Run intelligent scraper demo
    console.print("[yellow]Note: The following demo will attempt to scrape real websites.[/yellow]")
    console.print("[yellow]This may take 30-60 seconds per hotel. Continue? (y/n)[/yellow]")
    
    if input().lower().startswith('y'):
        await demo_intelligent_scraper()
    else:
        console.print("[yellow]Skipping live scraping demo.[/yellow]")
    
    console.print(Panel(
        Text("🎉 Demo Complete!", style="bold green"),
        subtitle="Ready for DigitalOcean deployment",
        border_style="green"
    ))
    
    console.print("\n[bold]Next Steps:[/bold]")
    next_steps = [
        "1. Review the generated files in the output directory",
        "2. Set up your DigitalOcean account and CLI",
        "3. Configure environment variables (especially OPENAI_API_KEY)",
        "4. Run ./deploy.sh to deploy to the cloud",
        "5. Test the API endpoints once deployed"
    ]
    
    for step in next_steps:
        console.print(f"  {step}")

if __name__ == "__main__":
    # Check if we have the required files
    current_dir = Path(__file__).parent
    required_files = ["intelligent_scraper.py", "intelligent_exporter.py", "app.yaml"]
    
    missing_files = [f for f in required_files if not (current_dir / f).exists()]
    
    if missing_files:
        console.print(f"[red]❌ Missing required files: {', '.join(missing_files)}[/red]")
        console.print("[yellow]Please ensure all files are in the same directory.[/yellow]")
    else:
        asyncio.run(main())
