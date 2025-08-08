"""
Hotel Website Scraper for Front Desk AI Agent

This module scrapes hotel websites for relevant information that can be used
by a front desk AI agent, including amenities, policies, nearby attractions,
restaurant information, and operational details.
"""

import json
import jsonlines
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import pandas as pd
from rich.console import Console
from rich.table import Table

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
console = Console()

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
    state: Optional[str] = None
    zip_code: Optional[str] = None
    
    # Check-in/out policies
    checkin_time: Optional[str] = None
    checkout_time: Optional[str] = None
    early_checkin_policy: Optional[str] = None
    late_checkout_policy: Optional[str] = None
    
    # Parking & Transportation
    parking_available: Optional[bool] = None
    parking_cost: Optional[str] = None
    parking_type: Optional[str] = None  # valet, self-park, etc.
    shuttle_service: Optional[str] = None
    public_transit_info: Optional[str] = None
    
    # Amenities
    wifi_info: Optional[str] = None
    fitness_center: Optional[bool] = None
    pool: Optional[bool] = None
    business_center: Optional[bool] = None
    pet_policy: Optional[str] = None
    smoking_policy: Optional[str] = None
    
    # Dining
    restaurants: List[Dict[str, str]] = None  # name, cuisine, hours, phone
    room_service: Optional[str] = None
    breakfast_info: Optional[str] = None
    
    # Nearby Attractions
    nearby_attractions: List[str] = None
    nearby_restaurants: List[str] = None
    nearby_shopping: List[str] = None
    
    # Policies
    cancellation_policy: Optional[str] = None
    deposit_policy: Optional[str] = None
    age_restrictions: Optional[str] = None
    
    # Additional Services
    concierge_services: List[str] = None
    laundry_service: Optional[str] = None
    luggage_storage: Optional[str] = None
    
    def __post_init__(self):
        if self.restaurants is None:
            self.restaurants = []
        if self.nearby_attractions is None:
            self.nearby_attractions = []
        if self.nearby_restaurants is None:
            self.nearby_restaurants = []
        if self.nearby_shopping is None:
            self.nearby_shopping = []
        if self.concierge_services is None:
            self.concierge_services = []

class HotelScraper:
    """Main scraper class for extracting hotel information"""
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.driver = None
        
    def setup_driver(self):
        """Initialize Chrome WebDriver"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        return self.driver
    
    def scrape_hotel(self, url: str, hotel_name: str = None) -> HotelInfo:
        """Scrape a single hotel website"""
        if not self.driver:
            self.setup_driver()
            
        try:
            logger.info(f"Scraping: {url}")
            self.driver.get(url)
            WebDriverWait(self.driver, 10).wait(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Get page source for BeautifulSoup parsing
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Initialize hotel info
            hotel_info = HotelInfo(
                hotel_name=hotel_name or self._extract_hotel_name(soup),
                website_url=url,
                scraped_at=datetime.now().isoformat()
            )
            
            # Extract various information sections
            self._extract_contact_info(soup, hotel_info)
            self._extract_policies(soup, hotel_info)
            self._extract_amenities(soup, hotel_info)
            self._extract_dining_info(soup, hotel_info)
            self._extract_nearby_info(soup, hotel_info)
            self._extract_services(soup, hotel_info)
            
            return hotel_info
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            raise
    
    def _extract_hotel_name(self, soup: BeautifulSoup) -> str:
        """Extract hotel name from various common selectors"""
        selectors = [
            'h1', '.hotel-name', '#hotel-name', '.property-name',
            '[data-testid="hotel-name"]', 'title'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element and element.get_text(strip=True):
                return element.get_text(strip=True)
        
        return "Unknown Hotel"
    
    def _extract_contact_info(self, soup: BeautifulSoup, hotel_info: HotelInfo):
        """Extract contact and location information"""
        # Phone number patterns
        phone_patterns = [
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            r'\(\d{3}\)\s*\d{3}[-.]?\d{4}'
        ]
        
        text = soup.get_text()
        for pattern in phone_patterns:
            import re
            match = re.search(pattern, text)
            if match:
                hotel_info.phone = match.group()
                break
        
        # Address extraction (simplified)
        address_keywords = ['address', 'location', 'directions']
        for keyword in address_keywords:
            elements = soup.find_all(text=re.compile(keyword, re.I))
            for element in elements:
                parent = element.parent
                if parent:
                    addr_text = parent.get_text(strip=True)
                    if len(addr_text) > 20:  # Basic address validation
                        hotel_info.address = addr_text[:200]  # Truncate if too long
                        break
    
    def _extract_policies(self, soup: BeautifulSoup, hotel_info: HotelInfo):
        """Extract check-in/out times and policies"""
        text_lower = soup.get_text().lower()
        
        # Check-in time
        checkin_patterns = [
            r'check[- ]?in:?\s*(\d{1,2}:?\d{0,2}\s*[ap]m)',
            r'arrival time:?\s*(\d{1,2}:?\d{0,2}\s*[ap]m)'
        ]
        
        for pattern in checkin_patterns:
            import re
            match = re.search(pattern, text_lower)
            if match:
                hotel_info.checkin_time = match.group(1)
                break
        
        # Check-out time
        checkout_patterns = [
            r'check[- ]?out:?\s*(\d{1,2}:?\d{0,2}\s*[ap]m)',
            r'departure time:?\s*(\d{1,2}:?\d{0,2}\s*[ap]m)'
        ]
        
        for pattern in checkout_patterns:
            match = re.search(pattern, text_lower)
            if match:
                hotel_info.checkout_time = match.group(1)
                break
        
        # Parking information
        if 'parking' in text_lower:
            if 'free parking' in text_lower or 'complimentary parking' in text_lower:
                hotel_info.parking_cost = "Free"
                hotel_info.parking_available = True
            elif 'valet' in text_lower:
                hotel_info.parking_type = "Valet"
                hotel_info.parking_available = True
            elif 'self-park' in text_lower or 'self park' in text_lower:
                hotel_info.parking_type = "Self-park"
                hotel_info.parking_available = True
    
    def _extract_amenities(self, soup: BeautifulSoup, hotel_info: HotelInfo):
        """Extract amenities information"""
        text_lower = soup.get_text().lower()
        
        # WiFi
        if 'free wifi' in text_lower or 'complimentary wifi' in text_lower:
            hotel_info.wifi_info = "Free WiFi available"
        elif 'wifi' in text_lower:
            hotel_info.wifi_info = "WiFi available"
        
        # Amenities
        hotel_info.fitness_center = 'fitness' in text_lower or 'gym' in text_lower
        hotel_info.pool = 'pool' in text_lower or 'swimming' in text_lower
        hotel_info.business_center = 'business center' in text_lower
        
        # Pet policy
        if 'pet friendly' in text_lower or 'pets welcome' in text_lower:
            hotel_info.pet_policy = "Pet friendly"
        elif 'no pets' in text_lower:
            hotel_info.pet_policy = "No pets allowed"
    
    def _extract_dining_info(self, soup: BeautifulSoup, hotel_info: HotelInfo):
        """Extract restaurant and dining information"""
        # Look for restaurant sections
        restaurant_keywords = ['restaurant', 'dining', 'bar', 'cafe', 'bistro']
        restaurants = []
        
        for keyword in restaurant_keywords:
            elements = soup.find_all(text=re.compile(keyword, re.I))
            for element in elements[:3]:  # Limit to avoid noise
                parent = element.parent
                if parent:
                    restaurant_text = parent.get_text(strip=True)
                    if len(restaurant_text) > 10:
                        restaurants.append({
                            'name': restaurant_text[:100],
                            'type': keyword,
                            'hours': 'Check with hotel',
                            'details': restaurant_text[:200]
                        })
        
        hotel_info.restaurants = restaurants[:5]  # Limit results
        
        # Room service
        text_lower = soup.get_text().lower()
        if 'room service' in text_lower:
            hotel_info.room_service = "Available"
        
        # Breakfast
        if 'breakfast' in text_lower:
            if 'complimentary breakfast' in text_lower or 'free breakfast' in text_lower:
                hotel_info.breakfast_info = "Complimentary breakfast included"
            else:
                hotel_info.breakfast_info = "Breakfast available"
    
    def _extract_nearby_info(self, soup: BeautifulSoup, hotel_info: HotelInfo):
        """Extract nearby attractions and points of interest"""
        text = soup.get_text()
        
        # Common attraction keywords
        attraction_keywords = [
            'museum', 'park', 'beach', 'downtown', 'airport', 'mall',
            'theater', 'stadium', 'convention center', 'university'
        ]
        
        attractions = []
        for keyword in attraction_keywords:
            if keyword in text.lower():
                # Find sentences containing the keyword
                sentences = text.split('.')
                for sentence in sentences:
                    if keyword in sentence.lower() and len(sentence.strip()) > 10:
                        attractions.append(sentence.strip()[:150])
                        break
        
        hotel_info.nearby_attractions = attractions[:5]
    
    def _extract_services(self, soup: BeautifulSoup, hotel_info: HotelInfo):
        """Extract additional services"""
        text_lower = soup.get_text().lower()
        services = []
        
        service_keywords = [
            'concierge', 'laundry', 'dry cleaning', 'luggage storage',
            'wake-up service', 'tour desk', 'car rental', 'babysitting'
        ]
        
        for service in service_keywords:
            if service in text_lower:
                services.append(service.title())
        
        hotel_info.concierge_services = services
    
    def close(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()

class HotelDataExporter:
    """Export scraped data in various formats for RAG consumption"""
    
    def __init__(self, output_dir: str = "hotel_data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def save_hotel_data(self, hotel_info: HotelInfo, format_type: str = "all"):
        """Save hotel data in specified format(s)"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        hotel_name_clean = "".join(c for c in hotel_info.hotel_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        
        if format_type in ["json", "all"]:
            self._save_json(hotel_info, f"{hotel_name_clean}_{timestamp}.json")
        
        if format_type in ["jsonl", "all"]:
            self._save_jsonl(hotel_info, f"{hotel_name_clean}_{timestamp}.jsonl")
        
        if format_type in ["csv", "all"]:
            self._save_csv(hotel_info, f"{hotel_name_clean}_{timestamp}.csv")
        
        if format_type in ["rag", "all"]:
            self._save_rag_format(hotel_info, f"{hotel_name_clean}_{timestamp}_rag.txt")
    
    def _save_json(self, hotel_info: HotelInfo, filename: str):
        """Save as JSON"""
        with open(self.output_dir / filename, 'w') as f:
            json.dump(asdict(hotel_info), f, indent=2, default=str)
    
    def _save_jsonl(self, hotel_info: HotelInfo, filename: str):
        """Save as JSONL for easier RAG ingestion"""
        with jsonlines.open(self.output_dir / filename, 'w') as writer:
            writer.write(asdict(hotel_info))
    
    def _save_csv(self, hotel_info: HotelInfo, filename: str):
        """Save as CSV"""
        df = pd.DataFrame([asdict(hotel_info)])
        df.to_csv(self.output_dir / filename, index=False)
    
    def _save_rag_format(self, hotel_info: HotelInfo, filename: str):
        """Save in a clean text format optimized for RAG"""
        with open(self.output_dir / filename, 'w') as f:
            f.write(f"Hotel Information: {hotel_info.hotel_name}\n")
            f.write(f"Website: {hotel_info.website_url}\n")
            f.write(f"Data collected: {hotel_info.scraped_at}\n\n")
            
            if hotel_info.address:
                f.write(f"Address: {hotel_info.address}\n")
            if hotel_info.phone:
                f.write(f"Phone: {hotel_info.phone}\n")
            
            f.write("\nCHECK-IN/CHECK-OUT POLICIES:\n")
            if hotel_info.checkin_time:
                f.write(f"Check-in time: {hotel_info.checkin_time}\n")
            if hotel_info.checkout_time:
                f.write(f"Check-out time: {hotel_info.checkout_time}\n")
            
            f.write("\nPARKING & TRANSPORTATION:\n")
            if hotel_info.parking_available:
                f.write(f"Parking available: Yes\n")
                if hotel_info.parking_cost:
                    f.write(f"Parking cost: {hotel_info.parking_cost}\n")
                if hotel_info.parking_type:
                    f.write(f"Parking type: {hotel_info.parking_type}\n")
            
            f.write("\nAMENITIES:\n")
            if hotel_info.wifi_info:
                f.write(f"WiFi: {hotel_info.wifi_info}\n")
            if hotel_info.fitness_center:
                f.write("Fitness center: Available\n")
            if hotel_info.pool:
                f.write("Pool: Available\n")
            if hotel_info.pet_policy:
                f.write(f"Pet policy: {hotel_info.pet_policy}\n")
            
            if hotel_info.restaurants:
                f.write("\nDINING OPTIONS:\n")
                for restaurant in hotel_info.restaurants:
                    f.write(f"- {restaurant.get('name', 'Restaurant')}: {restaurant.get('details', '')}\n")
            
            if hotel_info.room_service:
                f.write(f"Room service: {hotel_info.room_service}\n")
            if hotel_info.breakfast_info:
                f.write(f"Breakfast: {hotel_info.breakfast_info}\n")
            
            if hotel_info.nearby_attractions:
                f.write("\nNEARBY ATTRACTIONS:\n")
                for attraction in hotel_info.nearby_attractions:
                    f.write(f"- {attraction}\n")
            
            if hotel_info.concierge_services:
                f.write("\nADDITIONAL SERVICES:\n")
                for service in hotel_info.concierge_services:
                    f.write(f"- {service}\n")
    
    def display_summary(self, hotel_info: HotelInfo):
        """Display a rich formatted summary of scraped data"""
        table = Table(title=f"Hotel Data Summary: {hotel_info.hotel_name}")
        table.add_column("Category", style="cyan")
        table.add_column("Information", style="white")
        
        table.add_row("Hotel Name", hotel_info.hotel_name)
        table.add_row("Website", hotel_info.website_url)
        table.add_row("Phone", hotel_info.phone or "Not found")
        table.add_row("Check-in", hotel_info.checkin_time or "Not found")
        table.add_row("Check-out", hotel_info.checkout_time or "Not found")
        table.add_row("Parking", hotel_info.parking_cost or "Not specified")
        table.add_row("WiFi", hotel_info.wifi_info or "Not specified")
        table.add_row("Pet Policy", hotel_info.pet_policy or "Not specified")
        table.add_row("Restaurants", str(len(hotel_info.restaurants)) + " found")
        table.add_row("Nearby Attractions", str(len(hotel_info.nearby_attractions)) + " found")
        table.add_row("Services", str(len(hotel_info.concierge_services)) + " found")
        
        console.print(table)

if __name__ == "__main__":
    # Example usage
    scraper = HotelScraper(headless=True)
    exporter = HotelDataExporter()
    
    try:
        # Example hotel URLs (replace with actual hotel websites)
        test_urls = [
            ("https://www.marriott.com/en-us/hotels/hotel-deals/", "Marriott Example"),
            # Add more hotel URLs here
        ]
        
        for url, hotel_name in test_urls:
            try:
                hotel_data = scraper.scrape_hotel(url, hotel_name)
                exporter.display_summary(hotel_data)
                exporter.save_hotel_data(hotel_data, "all")
                console.print(f"✅ Successfully scraped and saved data for {hotel_name}")
            except Exception as e:
                console.print(f"❌ Failed to scrape {hotel_name}: {str(e)}")
    
    finally:
        scraper.close()
