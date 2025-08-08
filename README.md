# Hotel Website Scraper for Front Desk AI Agent

A Python tool that scrapes hotel websites to extract relevant information for front desk AI agents. The data is formatted and optimized for RAG (Retrieval Augmented Generation) systems.

## Features

### Data Extraction
- **Contact Information**: Phone numbers, addresses
- **Policies**: Check-in/out times, cancellation policies
- **Parking**: Availability, costs, types (valet, self-park)
- **Amenities**: WiFi, fitness center, pool, pet policies
- **Dining**: Restaurants, room service, breakfast information
- **Services**: Concierge, laundry, luggage storage
- **Nearby Attractions**: Points of interest, shopping, dining

### Output Formats
- **JSON**: Structured data for programmatic access
- **JSONL**: Line-delimited JSON for easy RAG ingestion
- **Text**: Clean format optimized for RAG systems
- **Markdown**: Human-readable documentation
- **CSV**: Tabular format for analysis

## Installation

1. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

### Basic Usage (Simple Scraper)

```python
from hotel_scraper_simple import scrape_hotels

# Define hotel URLs and names
hotels = [
    ("https://www.hotel-example.com", "Example Hotel"),
    ("https://www.another-hotel.com", "Another Hotel")
]

# Scrape and save in JSON format
results = scrape_hotels(hotels, output_format="json")
```

### Advanced Usage (Full Scraper)

```python
from hotel_scraper import HotelScraper, HotelDataExporter

scraper = HotelScraper(headless=True)
exporter = HotelDataExporter()

# Scrape a single hotel
hotel_data = scraper.scrape_hotel("https://hotel-website.com", "Hotel Name")

# Display summary
exporter.display_summary(hotel_data)

# Save in multiple formats
exporter.save_hotel_data(hotel_data, "all")  # Saves JSON, JSONL, CSV, and RAG text

scraper.close()
```

## Output Structure

### Sample RAG-Optimized Text Output
```
HOTEL INFORMATION
Hotel Name: Example Hotel
Website: https://example-hotel.com
Last Updated: 2024-01-15T10:30:00

CONTACT INFORMATION
Phone: (555) 123-4567

CHECK-IN AND CHECK-OUT
Check-in time: 3:00 PM
Check-out time: 11:00 AM

PARKING AND TRANSPORTATION
Parking: Available
Parking cost: Free
Parking type: Self-park

AMENITIES AND SERVICES
WiFi: Free WiFi available
Fitness center: Available
Pool: Available
Pet policy: Pet friendly

DINING OPTIONS
- Main Restaurant: Fine dining, open 6 AM - 10 PM
- Sports Bar: Casual dining, open 11 AM - 12 AM
```

### JSON Schema
```json
{
  "hotel_name": "string",
  "website_url": "string",
  "scraped_at": "ISO datetime",
  "phone": "string",
  "address": "string",
  "checkin_time": "string",
  "checkout_time": "string",
  "parking_available": "boolean",
  "parking_cost": "string",
  "parking_type": "string",
  "wifi_info": "string",
  "fitness_center": "boolean",
  "pool": "boolean",
  "pet_policy": "string",
  "restaurants": [
    {
      "name": "string",
      "type": "string",
      "hours": "string",
      "details": "string"
    }
  ],
  "room_service": "string",
  "breakfast_info": "string",
  "nearby_attractions": ["string"],
  "concierge_services": ["string"]
}
```

## RAG Integration

The scraped data is optimized for RAG systems:

1. **Clean Text Format**: Information is structured in clear, readable sections
2. **Semantic Chunking**: Data is organized by logical categories
3. **Consistent Schema**: Standardized field names and formats
4. **Metadata Inclusion**: Timestamps and source URLs for provenance

### Using with Popular RAG Frameworks

#### LangChain Example
```python
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Load RAG-formatted text files
loader = TextLoader("hotel_data/Hotel_Name_20240115_rag.txt")
documents = loader.load()

# Split for vector storage
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", " "]
)
splits = text_splitter.split_documents(documents)
```

#### LlamaIndex Example
```python
from llama_index import SimpleDirectoryReader, GPTVectorStoreIndex

# Load all hotel data files
documents = SimpleDirectoryReader("hotel_data").load_data()

# Create searchable index
index = GPTVectorStoreIndex.from_documents(documents)

# Query for front desk questions
query_engine = index.as_query_engine()
response = query_engine.query("What time is check-in and what parking options are available?")
```

## DigitalOcean Deployment

### App Platform Deployment

1. Create `app.yaml`:
```yaml
name: hotel-scraper
services:
- name: web
  source_dir: /
  github:
    repo: your-username/hotel-scraper
    branch: main
  run_command: python -m flask run --host=0.0.0.0 --port=8080
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  routes:
  - path: /
  envs:
  - key: FLASK_ENV
    value: production
```

2. Deploy using CLI:
```bash
doctl apps create --spec app.yaml
```

### Environment Variables
Set these in your DigitalOcean App Platform:
- `HOTEL_URLS`: Comma-separated list of hotel URLs to scrape
- `SCRAPE_INTERVAL`: How often to scrape (in hours)
- `OUTPUT_FORMAT`: Default output format (json, txt, markdown)

## Configuration

### Environment Variables
Create a `.env` file:
```env
# Scraping settings
HEADLESS_BROWSER=true
SCRAPE_TIMEOUT=30
MAX_RETRIES=3

# Output settings
OUTPUT_DIR=hotel_data
DEFAULT_FORMAT=json

# Optional: For advanced features
OPENAI_API_KEY=your_openai_key
HUGGINGFACE_TOKEN=your_hf_token
```

## File Structure
```
hotel_scraper/
├── hotel_scraper.py          # Full-featured scraper with Selenium
├── hotel_scraper_simple.py   # Basic scraper with requests only
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables
├── hotel_data/              # Output directory
│   ├── *.json              # Structured data files
│   ├── *_rag.txt           # RAG-optimized text files
│   └── *.md                # Markdown documentation
└── README.md
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure all dependencies are installed
   ```bash
   pip install -r requirements.txt
   ```

2. **Chrome Driver Issues**: The scraper will auto-download ChromeDriver
   ```bash
   # If issues persist, install manually:
   brew install chromedriver  # macOS
   ```

3. **Website Blocking**: Some sites may block automated requests
   - Use longer delays between requests
   - Rotate user agents
   - Consider using residential proxies

### Performance Tips

1. **Use Simple Scraper First**: Try `hotel_scraper_simple.py` for basic extraction
2. **Batch Processing**: Process multiple hotels in one session
3. **Caching**: Save successful results to avoid re-scraping
4. **Rate Limiting**: Add delays between requests to be respectful

## Legal Considerations

- Always check a website's `robots.txt` file
- Respect rate limits and don't overload servers
- Consider reaching out to hotels for API access
- Ensure compliance with data protection regulations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License - see LICENSE file for details
