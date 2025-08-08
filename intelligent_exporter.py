"""
Data export and formatting utilities for intelligent hotel scraper

This module provides enhanced data export capabilities with multiple formats
optimized for different use cases and RAG systems.
"""

import json
import jsonlines
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union
from dataclasses import asdict
import csv
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.panel import Panel

from intelligent_scraper import IntelligentHotelInfo

console = Console()

class IntelligentDataExporter:
    """Enhanced data exporter with AI insights formatting"""
    
    def __init__(self, output_dir: str = "intelligent_scraped_data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def export_hotel_data(self, hotel_info: IntelligentHotelInfo, 
                         formats: Union[str, List[str]] = "all") -> Dict[str, str]:
        """Export hotel data in specified format(s)"""
        if isinstance(formats, str):
            formats = [formats] if formats != "all" else [
                "json", "jsonl", "csv", "rag_text", "markdown", "summary"
            ]
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        hotel_name_clean = "".join(c for c in hotel_info.hotel_name if c.isalnum() or c in (' ', '-', '_')).strip()
        
        exported_files = {}
        
        for format_type in formats:
            try:
                if format_type == "json":
                    filename = f"{hotel_name_clean}_{timestamp}.json"
                    filepath = self._export_json(hotel_info, filename)
                    exported_files["json"] = str(filepath)
                
                elif format_type == "jsonl":
                    filename = f"{hotel_name_clean}_{timestamp}.jsonl"
                    filepath = self._export_jsonl(hotel_info, filename)
                    exported_files["jsonl"] = str(filepath)
                
                elif format_type == "csv":
                    filename = f"{hotel_name_clean}_{timestamp}.csv"
                    filepath = self._export_csv(hotel_info, filename)
                    exported_files["csv"] = str(filepath)
                
                elif format_type == "rag_text":
                    filename = f"{hotel_name_clean}_{timestamp}_rag.txt"
                    filepath = self._export_rag_text(hotel_info, filename)
                    exported_files["rag_text"] = str(filepath)
                
                elif format_type == "markdown":
                    filename = f"{hotel_name_clean}_{timestamp}.md"
                    filepath = self._export_markdown(hotel_info, filename)
                    exported_files["markdown"] = str(filepath)
                
                elif format_type == "summary":
                    filename = f"{hotel_name_clean}_{timestamp}_summary.txt"
                    filepath = self._export_summary(hotel_info, filename)
                    exported_files["summary"] = str(filepath)
                    
            except Exception as e:
                console.print(f"[red]Error exporting {format_type}: {e}[/red]")
        
        return exported_files
    
    def _export_json(self, hotel_info: IntelligentHotelInfo, filename: str) -> Path:
        """Export as structured JSON"""
        filepath = self.output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(asdict(hotel_info), f, indent=2, default=str, ensure_ascii=False)
        return filepath
    
    def _export_jsonl(self, hotel_info: IntelligentHotelInfo, filename: str) -> Path:
        """Export as JSONL for easier streaming and processing"""
        filepath = self.output_dir / filename
        with jsonlines.open(filepath, 'w') as writer:
            writer.write(asdict(hotel_info))
        return filepath
    
    def _export_csv(self, hotel_info: IntelligentHotelInfo, filename: str) -> Path:
        """Export as CSV with flattened structure"""
        filepath = self.output_dir / filename
        
        # Flatten complex fields
        data = asdict(hotel_info)
        flattened_data = self._flatten_dict(data)
        
        df = pd.DataFrame([flattened_data])
        df.to_csv(filepath, index=False, encoding='utf-8')
        return filepath
    
    def _flatten_dict(self, d: Dict, parent_key: str = '', sep: str = '_') -> Dict:
        """Flatten nested dictionary for CSV export"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                if v and isinstance(v[0], dict):
                    # For list of dicts, create separate columns for each item
                    for i, item in enumerate(v[:5]):  # Limit to first 5 items
                        if isinstance(item, dict):
                            items.extend(self._flatten_dict(item, f"{new_key}_{i}", sep=sep).items())
                        else:
                            items.append((f"{new_key}_{i}", str(item)))
                else:
                    # For simple lists, join as string
                    items.append((new_key, '; '.join(map(str, v))))
            else:
                items.append((new_key, v))
        
        return dict(items)
    
    def _export_rag_text(self, hotel_info: IntelligentHotelInfo, filename: str) -> Path:
        """Export in optimized format for RAG systems"""
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            # Header with metadata
            f.write(f"HOTEL INFORMATION PROFILE\n")
            f.write(f"{'=' * 50}\n\n")
            f.write(f"Hotel Name: {hotel_info.hotel_name}\n")
            f.write(f"Website: {hotel_info.website_url}\n")
            f.write(f"Data Quality Score: {hotel_info.confidence_score:.2f}/1.0\n")
            f.write(f"Last Updated: {hotel_info.scraped_at}\n")
            
            if hotel_info.sentiment_score is not None:
                sentiment_text = "Positive" if hotel_info.sentiment_score > 0.6 else "Neutral" if hotel_info.sentiment_score > 0.4 else "Negative"
                f.write(f"Content Sentiment: {sentiment_text} ({hotel_info.sentiment_score:.2f})\n")
            
            f.write(f"\n{'=' * 50}\n\n")
            
            # Contact Information
            f.write("CONTACT AND LOCATION\n")
            f.write("-" * 20 + "\n")
            if hotel_info.phone:
                f.write(f"Phone: {hotel_info.phone}\n")
            if hotel_info.email:
                f.write(f"Email: {hotel_info.email}\n")
            if hotel_info.address:
                f.write(f"Address: {hotel_info.address}\n")
            if hotel_info.city and hotel_info.state:
                f.write(f"Location: {hotel_info.city}, {hotel_info.state}\n")
            f.write("\n")
            
            # Policies
            f.write("HOTEL POLICIES\n")
            f.write("-" * 14 + "\n")
            if hotel_info.checkin_time:
                f.write(f"Check-in Time: {hotel_info.checkin_time}\n")
            if hotel_info.checkout_time:
                f.write(f"Check-out Time: {hotel_info.checkout_time}\n")
            if hotel_info.cancellation_policy:
                f.write(f"Cancellation Policy: {hotel_info.cancellation_policy}\n")
            if hotel_info.pet_policy:
                pet_status = hotel_info.pet_policy.get('allowed', 'Unknown') if isinstance(hotel_info.pet_policy, dict) else hotel_info.pet_policy
                f.write(f"Pet Policy: {pet_status}\n")
            f.write("\n")
            
            # Parking and Transportation
            f.write("PARKING AND TRANSPORTATION\n")
            f.write("-" * 26 + "\n")
            if hotel_info.parking_available:
                f.write("Parking: Available\n")
                if hotel_info.parking_cost:
                    f.write(f"Parking Cost: {hotel_info.parking_cost}\n")
                if hotel_info.parking_type:
                    f.write(f"Parking Type: {hotel_info.parking_type}\n")
            else:
                f.write("Parking: Information not available\n")
            
            if hotel_info.shuttle_service:
                f.write(f"Shuttle Service: {hotel_info.shuttle_service}\n")
            if hotel_info.distance_to_airport:
                f.write(f"Airport Distance: {hotel_info.distance_to_airport}\n")
            f.write("\n")
            
            # Amenities
            f.write("HOTEL AMENITIES\n")
            f.write("-" * 15 + "\n")
            if hotel_info.wifi_info:
                f.write(f"WiFi: {hotel_info.wifi_info}\n")
            
            if hotel_info.fitness_center:
                if isinstance(hotel_info.fitness_center, dict):
                    f.write(f"Fitness Center: Available - {hotel_info.fitness_center.get('details', '')}\n")
                else:
                    f.write("Fitness Center: Available\n")
            
            if hotel_info.pool:
                if isinstance(hotel_info.pool, dict):
                    pool_type = hotel_info.pool.get('type', 'Standard')
                    f.write(f"Pool: {pool_type} pool available\n")
                else:
                    f.write("Pool: Available\n")
            
            if hotel_info.spa_services:
                f.write(f"Spa Services: {', '.join(hotel_info.spa_services)}\n")
            
            if hotel_info.accessibility_features:
                f.write(f"Accessibility: {', '.join(hotel_info.accessibility_features)}\n")
            f.write("\n")
            
            # Dining
            if hotel_info.restaurants or hotel_info.room_service or hotel_info.breakfast_info:
                f.write("DINING OPTIONS\n")
                f.write("-" * 14 + "\n")
                
                if hotel_info.restaurants:
                    f.write("Restaurants:\n")
                    for restaurant in hotel_info.restaurants:
                        name = restaurant.get('name', 'Restaurant')
                        cuisine = restaurant.get('cuisine', '')
                        hours = restaurant.get('hours', '')
                        f.write(f"  • {name}")
                        if cuisine:
                            f.write(f" ({cuisine})")
                        if hours:
                            f.write(f" - {hours}")
                        f.write("\n")
                
                if hotel_info.room_service:
                    if isinstance(hotel_info.room_service, dict):
                        hours = hotel_info.room_service.get('hours', 'Available')
                        f.write(f"Room Service: {hours}\n")
                    else:
                        f.write(f"Room Service: {hotel_info.room_service}\n")
                
                if hotel_info.breakfast_info:
                    if isinstance(hotel_info.breakfast_info, dict):
                        bfast_type = hotel_info.breakfast_info.get('type', 'Available')
                        cost = hotel_info.breakfast_info.get('cost', '')
                        f.write(f"Breakfast: {bfast_type}")
                        if cost:
                            f.write(f" - {cost}")
                        f.write("\n")
                    else:
                        f.write(f"Breakfast: {hotel_info.breakfast_info}\n")
                f.write("\n")
            
            # Room Information
            if hotel_info.room_types or hotel_info.room_amenities:
                f.write("ROOM INFORMATION\n")
                f.write("-" * 16 + "\n")
                
                if hotel_info.room_types:
                    f.write("Room Types:\n")
                    for room in hotel_info.room_types:
                        room_type = room.get('type', 'Room')
                        description = room.get('description', '')
                        f.write(f"  • {room_type}")
                        if description:
                            f.write(f": {description[:100]}...")
                        f.write("\n")
                
                if hotel_info.room_amenities:
                    f.write(f"Room Amenities: {', '.join(hotel_info.room_amenities)}\n")
                f.write("\n")
            
            # Nearby Attractions
            if hotel_info.nearby_attractions:
                f.write("NEARBY ATTRACTIONS\n")
                f.write("-" * 18 + "\n")
                for attraction in hotel_info.nearby_attractions:
                    if isinstance(attraction, dict):
                        name = attraction.get('name', 'Attraction')
                        distance = attraction.get('distance', '')
                        f.write(f"  • {name}")
                        if distance and distance != 'Unknown':
                            f.write(f" ({distance})")
                        f.write("\n")
                    else:
                        f.write(f"  • {attraction}\n")
                f.write("\n")
            
            # AI Insights
            if hotel_info.key_selling_points or hotel_info.target_audience:
                f.write("AI-GENERATED INSIGHTS\n")
                f.write("-" * 21 + "\n")
                
                if hotel_info.key_selling_points:
                    f.write(f"Key Features: {', '.join(hotel_info.key_selling_points)}\n")
                
                if hotel_info.target_audience:
                    f.write(f"Target Audience: {', '.join(hotel_info.target_audience)}\n")
                
                if hotel_info.price_range_indicator:
                    f.write(f"Price Range: {hotel_info.price_range_indicator}\n")
                
                if hotel_info.unique_features:
                    f.write(f"Unique Features: {', '.join(hotel_info.unique_features)}\n")
                f.write("\n")
            
            # Services
            if hotel_info.concierge_services:
                f.write("ADDITIONAL SERVICES\n")
                f.write("-" * 19 + "\n")
                for service in hotel_info.concierge_services:
                    f.write(f"  • {service}\n")
                f.write("\n")
            
            # Footer
            f.write("=" * 50 + "\n")
            f.write("This data was extracted using AI-enhanced web scraping\n")
            f.write(f"Confidence Score: {hotel_info.confidence_score:.2f} (higher is better)\n")
            f.write("For the most current information, please contact the hotel directly.\n")
        
        return filepath
    
    def _export_markdown(self, hotel_info: IntelligentHotelInfo, filename: str) -> Path:
        """Export as Markdown documentation"""
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {hotel_info.hotel_name}\n\n")
            f.write(f"**Website:** {hotel_info.website_url}  \n")
            f.write(f"**Data Quality Score:** {hotel_info.confidence_score:.2f}/1.0  \n")
            f.write(f"**Last Updated:** {hotel_info.scraped_at}  \n\n")
            
            if hotel_info.key_selling_points:
                f.write("## 🌟 Key Features\n\n")
                for feature in hotel_info.key_selling_points:
                    f.write(f"- {feature}\n")
                f.write("\n")
            
            f.write("## 📞 Contact Information\n\n")
            if hotel_info.phone:
                f.write(f"**Phone:** {hotel_info.phone}  \n")
            if hotel_info.email:
                f.write(f"**Email:** {hotel_info.email}  \n")
            if hotel_info.address:
                f.write(f"**Address:** {hotel_info.address}  \n")
            f.write("\n")
            
            f.write("## 🏨 Policies\n\n")
            if hotel_info.checkin_time or hotel_info.checkout_time:
                f.write("### Check-in/Check-out\n")
                if hotel_info.checkin_time:
                    f.write(f"- **Check-in:** {hotel_info.checkin_time}\n")
                if hotel_info.checkout_time:
                    f.write(f"- **Check-out:** {hotel_info.checkout_time}\n")
                f.write("\n")
            
            if hotel_info.restaurants:
                f.write("## 🍽️ Dining\n\n")
                for restaurant in hotel_info.restaurants:
                    name = restaurant.get('name', 'Restaurant')
                    cuisine = restaurant.get('cuisine', '')
                    f.write(f"### {name}\n")
                    if cuisine:
                        f.write(f"**Cuisine:** {cuisine}  \n")
                    if restaurant.get('hours'):
                        f.write(f"**Hours:** {restaurant['hours']}  \n")
                    f.write("\n")
            
            if hotel_info.nearby_attractions:
                f.write("## 🎯 Nearby Attractions\n\n")
                for attraction in hotel_info.nearby_attractions:
                    if isinstance(attraction, dict):
                        name = attraction.get('name', 'Attraction')
                        distance = attraction.get('distance', '')
                        f.write(f"- **{name}**")
                        if distance and distance != 'Unknown':
                            f.write(f" ({distance})")
                        f.write("\n")
                    else:
                        f.write(f"- {attraction}\n")
                f.write("\n")
            
            f.write("---\n")
            f.write("*This information was automatically extracted using AI-enhanced web scraping.*\n")
        
        return filepath
    
    def _export_summary(self, hotel_info: IntelligentHotelInfo, filename: str) -> Path:
        """Export concise summary for quick reference"""
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"HOTEL SUMMARY: {hotel_info.hotel_name}\n")
            f.write("=" * (len(hotel_info.hotel_name) + 15) + "\n\n")
            
            # Essential info
            essentials = []
            if hotel_info.phone:
                essentials.append(f"Phone: {hotel_info.phone}")
            if hotel_info.checkin_time:
                essentials.append(f"Check-in: {hotel_info.checkin_time}")
            if hotel_info.checkout_time:
                essentials.append(f"Check-out: {hotel_info.checkout_time}")
            if hotel_info.parking_cost:
                essentials.append(f"Parking: {hotel_info.parking_cost}")
            if hotel_info.wifi_info:
                essentials.append(f"WiFi: {hotel_info.wifi_info}")
            
            f.write("QUICK FACTS:\n")
            for essential in essentials:
                f.write(f"• {essential}\n")
            f.write("\n")
            
            # Amenities summary
            amenities = []
            if hotel_info.fitness_center:
                amenities.append("Fitness Center")
            if hotel_info.pool:
                amenities.append("Pool")
            if hotel_info.spa_services:
                amenities.append("Spa Services")
            
            if amenities:
                f.write(f"AMENITIES: {', '.join(amenities)}\n\n")
            
            # Dining summary
            if hotel_info.restaurants:
                f.write(f"DINING: {len(hotel_info.restaurants)} restaurant(s)\n")
                for restaurant in hotel_info.restaurants[:3]:  # Top 3
                    name = restaurant.get('name', 'Restaurant')
                    cuisine = restaurant.get('cuisine', '')
                    f.write(f"• {name}")
                    if cuisine:
                        f.write(f" ({cuisine})")
                    f.write("\n")
                f.write("\n")
            
            # AI insights
            if hotel_info.key_selling_points:
                f.write(f"KEY FEATURES: {', '.join(hotel_info.key_selling_points)}\n\n")
            
            f.write(f"DATA QUALITY: {hotel_info.confidence_score:.0%}\n")
            f.write(f"SCRAPED: {hotel_info.scraped_at}\n")
        
        return filepath
    
    def display_rich_summary(self, hotel_info: IntelligentHotelInfo):
        """Display rich formatted summary in console"""
        # Main header
        header_text = Text(f"🏨 {hotel_info.hotel_name}", style="bold cyan")
        console.print(Panel(header_text, border_style="cyan"))
        
        # Create main table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Category", style="cyan", width=20)
        table.add_column("Information", style="white", width=50)
        table.add_column("AI Score", style="yellow", width=10)
        
        # Basic info
        table.add_row("🌐 Website", hotel_info.website_url, "")
        table.add_row("📞 Phone", hotel_info.phone or "Not found", "")
        table.add_row("📧 Email", hotel_info.email or "Not found", "")
        
        # Policies
        table.add_row("🕒 Check-in", hotel_info.checkin_time or "Not specified", "")
        table.add_row("🕕 Check-out", hotel_info.checkout_time or "Not specified", "")
        
        # Parking
        parking_info = "Not specified"
        if hotel_info.parking_available:
            parking_info = hotel_info.parking_cost or "Available"
            if hotel_info.parking_type:
                parking_info += f" ({hotel_info.parking_type})"
        table.add_row("🅿️ Parking", parking_info, "")
        
        # WiFi
        table.add_row("📶 WiFi", hotel_info.wifi_info or "Not specified", "")
        
        # Amenities
        amenities_list = []
        if hotel_info.fitness_center:
            amenities_list.append("Fitness")
        if hotel_info.pool:
            amenities_list.append("Pool")
        if hotel_info.spa_services:
            amenities_list.append("Spa")
        if hotel_info.business_center:
            amenities_list.append("Business Center")
        
        amenities_text = ", ".join(amenities_list) if amenities_list else "Basic amenities"
        table.add_row("🏋️ Amenities", amenities_text, "")
        
        # Dining
        dining_count = len(hotel_info.restaurants) if hotel_info.restaurants else 0
        dining_text = f"{dining_count} restaurant(s)" if dining_count > 0 else "No restaurants found"
        table.add_row("🍽️ Dining", dining_text, "")
        
        # Nearby attractions
        attractions_count = len(hotel_info.nearby_attractions) if hotel_info.nearby_attractions else 0
        attractions_text = f"{attractions_count} attraction(s)" if attractions_count > 0 else "No attractions found"
        table.add_row("🎯 Attractions", attractions_text, "")
        
        # AI insights
        if hotel_info.target_audience:
            table.add_row("👥 Target Audience", ", ".join(hotel_info.target_audience), "")
        
        if hotel_info.price_range_indicator:
            table.add_row("💰 Price Range", hotel_info.price_range_indicator, "")
        
        # Data quality
        confidence_color = "green" if hotel_info.confidence_score > 0.7 else "yellow" if hotel_info.confidence_score > 0.5 else "red"
        confidence_text = Text(f"{hotel_info.confidence_score:.0%}", style=confidence_color)
        table.add_row("📊 Data Quality", "", str(confidence_text))
        
        console.print(table)
        
        # Key selling points
        if hotel_info.key_selling_points:
            features_text = " • ".join(hotel_info.key_selling_points)
            console.print(Panel(
                Text(features_text, style="bold green"),
                title="🌟 Key Features",
                border_style="green"
            ))
        
        # Sentiment analysis
        if hotel_info.sentiment_score is not None:
            sentiment_text = "Positive" if hotel_info.sentiment_score > 0.6 else "Neutral" if hotel_info.sentiment_score > 0.4 else "Negative"
            sentiment_color = "green" if hotel_info.sentiment_score > 0.6 else "yellow" if hotel_info.sentiment_score > 0.4 else "red"
            console.print(Panel(
                Text(f"{sentiment_text} ({hotel_info.sentiment_score:.2f})", style=sentiment_color),
                title="😊 Content Sentiment",
                border_style=sentiment_color
            ))
        
        console.print(f"\n[dim]Last updated: {hotel_info.scraped_at}[/dim]")

# Example usage
if __name__ == "__main__":
    # This would typically be called with actual hotel data
    console.print("[yellow]IntelligentDataExporter ready for use![/yellow]")
