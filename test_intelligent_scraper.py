#!/usr/bin/env python3
"""
Test the intelligent scraper with Mission Bay hotel data
"""
import json
import os
import sys
from pathlib import Path
from typing import List

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from intelligent_scraper import IntelligentHotelScraper
from intelligent_exporter import IntelligentDataExporter

def load_test_urls() -> List[str]:
    """Load test URLs from MissionBay.json"""
    json_path = Path(__file__).parent / "hotel_data" / "MissionBay.json"
    with open(json_path, 'r', encoding='utf-8-sig') as f:
        urls = json.load(f)
    return urls

def test_intelligent_scraper():
    """Test the intelligent scraper with a subset of Mission Bay URLs"""
    print("🚀 Testing Intelligent Hotel Scraper")
    print("=" * 50)
    
    # Load test URLs
    all_urls = load_test_urls()
    print(f"📋 Loaded {len(all_urls)} URLs from MissionBay.json")
    
    # Use first 5 URLs for testing to avoid overwhelming the system
    test_urls = all_urls[:5]
    print(f"🧪 Testing with first {len(test_urls)} URLs:")
    for i, url in enumerate(test_urls, 1):
        print(f"   {i}. {url}")
    
    # Initialize scraper
    print("\n🤖 Initializing Intelligent Scraper...")
    scraper = IntelligentHotelScraper()
    
    # Set environment variable for free AI mode but disable AI temporarily to test basic scraping
    os.environ['USE_FREE_AI'] = 'false'  # Disable AI to avoid tensor issues
    
    # Scrape hotels
    print("\n🔍 Starting intelligent scraping...")
    results = []
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n--- Scraping {i}/{len(test_urls)}: {url} ---")
        try:
            hotel_info = scraper.scrape_hotel(url)
            if hotel_info:
                results.append(hotel_info)
                print(f"✅ Successfully scraped: {hotel_info.hotel_name}")
                print(f"   📧 Contact: {hotel_info.email or 'N/A'}")
                print(f"   📍 Address: {hotel_info.address or 'N/A'}")
                print(f"   🏨 Amenities: {len(hotel_info.room_amenities or [])} found")
            else:
                print(f"❌ Failed to scrape: {url}")
        except Exception as e:
            print(f"❌ Error scraping {url}: {str(e)}")
    
    print(f"\n📊 Scraping Complete: {len(results)}/{len(test_urls)} successful")
    
    # Test exporter
    if results:
        print("\n📤 Testing Export Functionality...")
        exporter = IntelligentDataExporter()
        
        # Create output directory
        output_dir = Path(__file__).parent / "test_output"
        output_dir.mkdir(exist_ok=True)
        
        # Export in different formats
        for fmt in ['json', 'jsonl', 'rag_text', 'markdown']:
            try:
                # Export each hotel individually (since exporter handles single hotels)
                for i, hotel_info in enumerate(results):
                    if i == 0:  # Just export the first one for testing
                        result_files = exporter.export_hotel_data(hotel_info, [fmt])
                        for format_name, file_path in result_files.items():
                            print(f"✅ Exported to {format_name.upper()}: {file_path}")
                            file_size = Path(file_path).stat().st_size if Path(file_path).exists() else 0
                            print(f"   📁 File size: {file_size} bytes")
                        break
            except Exception as e:
                print(f"❌ Export to {fmt} failed: {str(e)}")
    
    print("\n🎉 Test Complete!")
    return results

if __name__ == "__main__":
    results = test_intelligent_scraper()
