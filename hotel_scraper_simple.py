"""
Simple Hotel Website Scraper for RAG Data
Extracts hotel information in a clean, structured format
"""

import json
import re
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class HotelInfo:
    """Structured hotel information for RAG consumption"""
    hotel_name: str
    website_url: str
    scraped_at: str
    
    # Contact & Location
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    
    # Check-in/out policies
    checkin_time: Optional[str] = None
    checkout_time: Optional[str] = None
    
    # Parking & Transportation
    parking_available: Optional[bool] = None
    parking_cost: Optional[str] = None
    parking_type: Optional[str] = None
    
    # Amenities
    wifi_info: Optional[str] = None
    fitness_center: Optional[bool] = None
    pool: Optional[bool] = None
    pet_policy: Optional[str] = None
    
    # Dining
    restaurants: List[Dict[str, str]] = None
    room_service: Optional[str] = None
    breakfast_info: Optional[str] = None
    
    # Nearby Attractions
    nearby_attractions: List[str] = None
    
    # Additional Services
    concierge_services: List[str] = None
    
    def __post_init__(self):
        if self.restaurants is None:
            self.restaurants = []
        if self.nearby_attractions is None:
            self.nearby_attractions = []
        if self.concierge_services is None:
            self.concierge_services = []

class SimpleHotelScraper:
    """Simplified scraper using requests and basic parsing"""
    
    def __init__(self):
        self.session = None
        
    def setup_session(self):
        """Initialize requests session"""
        try:
            import requests
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            })
        except ImportError:
            logger.error("requests library not installed. Run: pip install requests")
            raise
    
    def scrape_hotel_basic(self, url: str, hotel_name: str = None) -> HotelInfo:
        """Basic scraping using requests and regex"""
        if not self.session:
            self.setup_session()
            
        try:
            logger.info(f"Scraping: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            html_content = response.text.lower()
            
            # Initialize hotel info
            hotel_info = HotelInfo(
                hotel_name=hotel_name or self._extract_hotel_name_basic(response.text),
                website_url=url,
                scraped_at=datetime.now().isoformat()
            )
            
            # Extract information using regex patterns
            self._extract_basic_info(html_content, hotel_info)
            
            return hotel_info
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            raise
    
    def _extract_hotel_name_basic(self, html: str) -> str:
        """Extract hotel name from title tag"""
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.I)
        if title_match:
            return title_match.group(1).strip()
        return "Unknown Hotel"
    
    def _extract_basic_info(self, html: str, hotel_info: HotelInfo):
        """Extract basic information using regex patterns"""
        
        # Phone number
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        phone_match = re.search(phone_pattern, html)
        if phone_match:
            hotel_info.phone = phone_match.group()
        
        # Check-in time
        checkin_patterns = [
            r'check[- ]?in:?\s*(\d{1,2}:?\d{0,2}\s*[ap]m)',
            r'arrival time:?\s*(\d{1,2}:?\d{0,2}\s*[ap]m)'
        ]
        for pattern in checkin_patterns:
            match = re.search(pattern, html)
            if match:
                hotel_info.checkin_time = match.group(1)
                break
        
        # Check-out time
        checkout_patterns = [
            r'check[- ]?out:?\s*(\d{1,2}:?\d{0,2}\s*[ap]m)',
            r'departure time:?\s*(\d{1,2}:?\d{0,2}\s*[ap]m)'
        ]
        for pattern in checkout_patterns:
            match = re.search(pattern, html)
            if match:
                hotel_info.checkout_time = match.group(1)
                break
        
        # Parking
        if 'free parking' in html or 'complimentary parking' in html:
            hotel_info.parking_cost = "Free"
            hotel_info.parking_available = True
        elif 'valet' in html:
            hotel_info.parking_type = "Valet"
            hotel_info.parking_available = True
        elif 'parking' in html:
            hotel_info.parking_available = True
        
        # WiFi
        if 'free wifi' in html or 'complimentary wifi' in html:
            hotel_info.wifi_info = "Free WiFi available"
        elif 'wifi' in html:
            hotel_info.wifi_info = "WiFi available"
        
        # Amenities
        hotel_info.fitness_center = 'fitness' in html or 'gym' in html
        hotel_info.pool = 'pool' in html or 'swimming' in html
        
        # Pet policy
        if 'pet friendly' in html or 'pets welcome' in html:
            hotel_info.pet_policy = "Pet friendly"
        elif 'no pets' in html:
            hotel_info.pet_policy = "No pets allowed"
        
        # Room service
        if 'room service' in html:
            hotel_info.room_service = "Available"
        
        # Breakfast
        if 'complimentary breakfast' in html or 'free breakfast' in html:
            hotel_info.breakfast_info = "Complimentary breakfast included"
        elif 'breakfast' in html:
            hotel_info.breakfast_info = "Breakfast available"

class RAGDataExporter:
    """Export scraped data in RAG-ready formats"""
    
    def __init__(self, output_dir: str = "hotel_data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def save_for_rag(self, hotel_info: HotelInfo, format_type: str = "json"):
        """Save hotel data in RAG-ready format"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        hotel_name_clean = "".join(c for c in hotel_info.hotel_name if c.isalnum() or c in (' ', '-', '_')).strip()
        
        if format_type == "json":
            filename = f"{hotel_name_clean}_{timestamp}.json"
            self._save_json(hotel_info, filename)
        elif format_type == "txt":
            filename = f"{hotel_name_clean}_{timestamp}_rag.txt"
            self._save_rag_text(hotel_info, filename)
        elif format_type == "markdown":
            filename = f"{hotel_name_clean}_{timestamp}.md"
            self._save_markdown(hotel_info, filename)
        
        print(f"✅ Saved hotel data: {self.output_dir / filename}")
        return self.output_dir / filename
    
    def _save_json(self, hotel_info: HotelInfo, filename: str):
        """Save as structured JSON"""
        with open(self.output_dir / filename, 'w') as f:
            json.dump(asdict(hotel_info), f, indent=2, default=str)
    
    def _save_rag_text(self, hotel_info: HotelInfo, filename: str):
        """Save in clean text format optimized for RAG"""
        with open(self.output_dir / filename, 'w') as f:
            f.write(f"HOTEL INFORMATION\n")
            f.write(f"Hotel Name: {hotel_info.hotel_name}\n")
            f.write(f"Website: {hotel_info.website_url}\n")
            f.write(f"Last Updated: {hotel_info.scraped_at}\n\n")
            
            if hotel_info.phone:
                f.write(f"CONTACT INFORMATION\n")
                f.write(f"Phone: {hotel_info.phone}\n\n")
            
            f.write(f"CHECK-IN AND CHECK-OUT\n")
            if hotel_info.checkin_time:
                f.write(f"Check-in time: {hotel_info.checkin_time}\n")
            if hotel_info.checkout_time:
                f.write(f"Check-out time: {hotel_info.checkout_time}\n")
            f.write("\n")
            
            f.write(f"PARKING AND TRANSPORTATION\n")
            if hotel_info.parking_available:
                f.write(f"Parking: Available\n")
                if hotel_info.parking_cost:
                    f.write(f"Parking cost: {hotel_info.parking_cost}\n")
                if hotel_info.parking_type:
                    f.write(f"Parking type: {hotel_info.parking_type}\n")
            else:
                f.write(f"Parking: Information not available\n")
            f.write("\n")
            
            f.write(f"AMENITIES AND SERVICES\n")
            if hotel_info.wifi_info:
                f.write(f"WiFi: {hotel_info.wifi_info}\n")
            if hotel_info.fitness_center:
                f.write(f"Fitness center: Available\n")
            if hotel_info.pool:
                f.write(f"Pool: Available\n")
            if hotel_info.pet_policy:
                f.write(f"Pet policy: {hotel_info.pet_policy}\n")
            if hotel_info.room_service:
                f.write(f"Room service: {hotel_info.room_service}\n")
            if hotel_info.breakfast_info:
                f.write(f"Breakfast: {hotel_info.breakfast_info}\n")
            f.write("\n")
            
            if hotel_info.restaurants:
                f.write(f"DINING OPTIONS\n")
                for restaurant in hotel_info.restaurants:
                    f.write(f"- {restaurant.get('name', 'Restaurant')}\n")
                f.write("\n")
            
            if hotel_info.nearby_attractions:
                f.write(f"NEARBY ATTRACTIONS\n")
                for attraction in hotel_info.nearby_attractions:
                    f.write(f"- {attraction}\n")
                f.write("\n")
    
    def _save_markdown(self, hotel_info: HotelInfo, filename: str):
        """Save as markdown for easy reading"""
        with open(self.output_dir / filename, 'w') as f:
            f.write(f"# {hotel_info.hotel_name}\n\n")
            f.write(f"**Website:** {hotel_info.website_url}\n")
            f.write(f"**Data collected:** {hotel_info.scraped_at}\n\n")
            
            if hotel_info.phone:
                f.write(f"## Contact Information\n")
                f.write(f"- **Phone:** {hotel_info.phone}\n\n")
            
            f.write(f"## Check-in/Check-out\n")
            if hotel_info.checkin_time:
                f.write(f"- **Check-in:** {hotel_info.checkin_time}\n")
            if hotel_info.checkout_time:
                f.write(f"- **Check-out:** {hotel_info.checkout_time}\n")
            f.write("\n")
            
            f.write(f"## Parking\n")
            if hotel_info.parking_available:
                f.write(f"- **Available:** Yes\n")
                if hotel_info.parking_cost:
                    f.write(f"- **Cost:** {hotel_info.parking_cost}\n")
                if hotel_info.parking_type:
                    f.write(f"- **Type:** {hotel_info.parking_type}\n")
            else:
                f.write(f"- **Available:** Information not found\n")
            f.write("\n")
            
            f.write(f"## Amenities\n")
            amenities = []
            if hotel_info.wifi_info:
                amenities.append(f"WiFi: {hotel_info.wifi_info}")
            if hotel_info.fitness_center:
                amenities.append("Fitness center available")
            if hotel_info.pool:
                amenities.append("Pool available")
            if hotel_info.pet_policy:
                amenities.append(f"Pet policy: {hotel_info.pet_policy}")
            
            for amenity in amenities:
                f.write(f"- {amenity}\n")
            f.write("\n")
            
            if hotel_info.room_service or hotel_info.breakfast_info:
                f.write(f"## Dining Services\n")
                if hotel_info.room_service:
                    f.write(f"- **Room service:** {hotel_info.room_service}\n")
                if hotel_info.breakfast_info:
                    f.write(f"- **Breakfast:** {hotel_info.breakfast_info}\n")
                f.write("\n")
    
    def display_summary(self, hotel_info: HotelInfo):
        """Display a simple text summary"""
        print(f"\n{'='*50}")
        print(f"HOTEL DATA SUMMARY")
        print(f"{'='*50}")
        print(f"Hotel: {hotel_info.hotel_name}")
        print(f"Website: {hotel_info.website_url}")
        print(f"Phone: {hotel_info.phone or 'Not found'}")
        print(f"Check-in: {hotel_info.checkin_time or 'Not found'}")
        print(f"Check-out: {hotel_info.checkout_time or 'Not found'}")
        print(f"Parking: {hotel_info.parking_cost or 'Not specified'}")
        print(f"WiFi: {hotel_info.wifi_info or 'Not specified'}")
        print(f"Pet Policy: {hotel_info.pet_policy or 'Not specified'}")
        print(f"Room Service: {hotel_info.room_service or 'Not specified'}")
        print(f"Breakfast: {hotel_info.breakfast_info or 'Not specified'}")
        print(f"{'='*50}\n")

# Example usage function
def scrape_hotels(urls_and_names: List[tuple], output_format: str = "json"):
    """
    Scrape multiple hotels and save in RAG-ready format
    
    Args:
        urls_and_names: List of (url, hotel_name) tuples
        output_format: 'json', 'txt', or 'markdown'
    """
    scraper = SimpleHotelScraper()
    exporter = RAGDataExporter()
    
    results = []
    
    for url, hotel_name in urls_and_names:
        try:
            print(f"🔍 Scraping: {hotel_name}")
            hotel_data = scraper.scrape_hotel_basic(url, hotel_name)
            exporter.display_summary(hotel_data)
            filename = exporter.save_for_rag(hotel_data, output_format)
            results.append((hotel_name, filename, "success"))
            
        except Exception as e:
            print(f"❌ Failed to scrape {hotel_name}: {str(e)}")
            results.append((hotel_name, None, f"error: {str(e)}"))
    
    # Summary report
    print(f"\n📊 SCRAPING SUMMARY")
    print(f"{'='*50}")
    successful = sum(1 for _, _, status in results if status == "success")
    print(f"Successful: {successful}/{len(results)}")
    
    for hotel_name, filename, status in results:
        status_icon = "✅" if status == "success" else "❌"
        print(f"{status_icon} {hotel_name}: {status}")
    
    return results

if __name__ == "__main__":
    # Example usage - replace with actual hotel URLs
    example_hotels = [
        ("https://www.marriott.com", "Marriott Hotels"),
        ("https://www.hilton.com", "Hilton Hotels"),
        # Add your hotel URLs here
    ]
    
    print("🏨 Hotel Website Scraper for RAG Data")
    print("This tool extracts hotel information in formats ready for RAG systems")
    print("\nTo use this scraper:")
    print("1. Replace the example URLs with actual hotel websites")
    print("2. Run: python hotel_scraper_simple.py")
    print("3. Check the 'hotel_data' folder for output files")
    print("\nSupported output formats: json, txt, markdown")
