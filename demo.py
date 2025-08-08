"""
Example script demonstrating hotel scraping for RAG data
Run this after installing dependencies
"""

def demo_scraper():
    """Demonstrate the hotel scraper with example data"""
    print("🏨 Hotel Scraper Demo")
    print("=" * 50)
    
    # Create sample hotel data structure
    from datetime import datetime
    
    sample_hotel = {
        "hotel_name": "Grand Example Hotel",
        "website_url": "https://example-hotel.com",
        "scraped_at": datetime.now().isoformat(),
        "phone": "(555) 123-4567",
        "address": "123 Main Street, Downtown, NY 10001",
        "checkin_time": "3:00 PM",
        "checkout_time": "11:00 AM",
        "parking_available": True,
        "parking_cost": "Free",
        "parking_type": "Self-park",
        "wifi_info": "Free WiFi available",
        "fitness_center": True,
        "pool": True,
        "pet_policy": "Pet friendly - $50 fee",
        "restaurants": [
            {
                "name": "Main Dining Room",
                "type": "Fine dining",
                "hours": "6:00 AM - 10:00 PM",
                "details": "American cuisine with seasonal menu"
            },
            {
                "name": "Lobby Bar",
                "type": "Bar",
                "hours": "4:00 PM - 12:00 AM",
                "details": "Craft cocktails and light appetizers"
            }
        ],
        "room_service": "Available 24/7",
        "breakfast_info": "Continental breakfast included",
        "nearby_attractions": [
            "Central Park (0.2 miles)",
            "Metropolitan Museum (0.5 miles)",
            "Times Square (1.2 miles)"
        ],
        "concierge_services": [
            "Tour booking",
            "Restaurant reservations",
            "Transportation arrangement"
        ]
    }
    
    # Display the data structure
    print("Sample Hotel Data Structure:")
    print("-" * 30)
    
    import json
    print(json.dumps(sample_hotel, indent=2))
    
    # Create RAG-formatted text
    print("\n" + "=" * 50)
    print("RAG-Optimized Format:")
    print("=" * 50)
    
    rag_text = f"""HOTEL INFORMATION
Hotel Name: {sample_hotel['hotel_name']}
Website: {sample_hotel['website_url']}
Last Updated: {sample_hotel['scraped_at']}

CONTACT INFORMATION
Phone: {sample_hotel['phone']}
Address: {sample_hotel['address']}

CHECK-IN AND CHECK-OUT
Check-in time: {sample_hotel['checkin_time']}
Check-out time: {sample_hotel['checkout_time']}

PARKING AND TRANSPORTATION
Parking: Available
Parking cost: {sample_hotel['parking_cost']}
Parking type: {sample_hotel['parking_type']}

AMENITIES AND SERVICES
WiFi: {sample_hotel['wifi_info']}
Fitness center: Available
Pool: Available
Pet policy: {sample_hotel['pet_policy']}

DINING OPTIONS"""
    
    for restaurant in sample_hotel['restaurants']:
        rag_text += f"\n- {restaurant['name']}: {restaurant['details']} (Hours: {restaurant['hours']})"
    
    rag_text += f"""

Room service: {sample_hotel['room_service']}
Breakfast: {sample_hotel['breakfast_info']}

NEARBY ATTRACTIONS"""
    
    for attraction in sample_hotel['nearby_attractions']:
        rag_text += f"\n- {attraction}"
    
    rag_text += "\n\nADDITIONAL SERVICES"
    for service in sample_hotel['concierge_services']:
        rag_text += f"\n- {service}"
    
    print(rag_text)
    
    # Save sample files
    import os
    os.makedirs("hotel_data", exist_ok=True)
    
    # Save JSON
    with open("hotel_data/sample_hotel.json", "w") as f:
        json.dump(sample_hotel, f, indent=2)
    
    # Save RAG text
    with open("hotel_data/sample_hotel_rag.txt", "w") as f:
        f.write(rag_text)
    
    print(f"\n✅ Sample files saved to hotel_data/")
    print(f"   - sample_hotel.json (structured data)")
    print(f"   - sample_hotel_rag.txt (RAG-optimized text)")
    
    print(f"\n📝 Next Steps:")
    print(f"   1. Install dependencies: pip install requests beautifulsoup4")
    print(f"   2. Replace example URLs in hotel_scraper_simple.py")
    print(f"   3. Run: python hotel_scraper_simple.py")
    print(f"   4. Check hotel_data/ folder for results")

if __name__ == "__main__":
    demo_scraper()
