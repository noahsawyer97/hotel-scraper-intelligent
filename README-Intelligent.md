# Intelligent Hotel Scraper - DigitalOcean Deployment

## 🚀 Enhanced Hotel Scraping with AI Intelligence

This is an advanced version of the hotel scraper with AI-powered content extraction, semantic analysis, and cloud deployment capabilities on DigitalOcean App Platform.

### 🆕 New Features

#### AI-Enhanced Extraction
- **Semantic Understanding**: Uses transformer models for better content comprehension
- **Named Entity Recognition**: Automatically identifies contacts, locations, and amenities
- **Sentiment Analysis**: Analyzes content sentiment for quality insights
- **Confidence Scoring**: Provides data quality metrics for each scrape
- **Smart Categorization**: AI-powered classification of amenities and services

#### Cloud Infrastructure
- **DigitalOcean App Platform**: Fully managed deployment
- **Redis Caching**: Fast response times with intelligent caching
- **Background Processing**: Celery workers for intensive scraping tasks
- **Auto-scaling**: Handles multiple concurrent requests
- **Monitoring**: Built-in health checks and metrics

#### Enhanced Data Formats
- **RAG-Optimized Text**: Perfect for AI assistant consumption
- **Structured JSON/JSONL**: Machine-readable formats
- **Rich Markdown**: Human-readable documentation
- **Executive Summaries**: Quick reference formats
- **Multiple Export Options**: CSV, JSON, text, and more

### 📁 Project Structure

```
Hotel Scraping - Hybrid/
├── app.yaml                      # DigitalOcean App Platform config
├── app.py                        # Flask API server
├── intelligent_scraper.py        # AI-enhanced scraper
├── intelligent_exporter.py       # Advanced data export
├── worker.py                     # Background task processor
├── deploy.sh                     # Deployment script
├── requirements-intelligent.txt  # Enhanced dependencies
├── .env.production               # Production environment
├── hotel_scraper.py             # Original scraper (maintained)
├── hotel_scraper_simple.py      # Simple scraper
├── demo.py                       # Demonstration script
└── hotel_data/                   # Output directory
    ├── sample_hotel.json
    └── sample_hotel_rag.txt
```

### 🛠️ Installation & Setup

#### Local Development

1. **Clone and setup environment**:
```bash
cd "Hotel Scraping - Hybrid"
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
pip install -r requirements-intelligent.txt
```

2. **Install spaCy model** (for advanced NLP):
```bash
python -m spacy download en_core_web_sm
```

3. **Set environment variables**:
```bash
export OPENAI_API_KEY="your_openai_key"
export HUGGINGFACE_TOKEN="your_hf_token"  # Optional
export REDIS_URL="redis://localhost:6379"  # If running Redis locally
```

4. **Run locally**:
```bash
# Start the API server
python app.py

# Or run the intelligent scraper directly
python intelligent_scraper.py
```

#### DigitalOcean Deployment

1. **Install DigitalOcean CLI**:
```bash
# macOS
brew install doctl

# Or download from: https://docs.digitalocean.com/reference/doctl/how-to/install/
```

2. **Authenticate**:
```bash
doctl auth init
```

3. **Deploy**:
```bash
./deploy.sh
```

4. **Set environment variables** in DigitalOcean dashboard:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `HUGGINGFACE_TOKEN`: Your Hugging Face token (optional)
   - `SENTRY_DSN`: For error tracking (optional)

### 🔌 API Usage

#### Health Check
```bash
GET /api/v1/health
```

#### Single Hotel Scraping
```bash
POST /api/v1/scrape
Content-Type: application/json

{
  "url": "https://www.hotel-example.com",
  "hotel_name": "Example Hotel"
}
```

#### Batch Scraping
```bash
POST /api/v1/scrape/batch
Content-Type: application/json

{
  "hotels": [
    {"url": "https://hotel1.com", "name": "Hotel 1"},
    {"url": "https://hotel2.com", "name": "Hotel 2"}
  ]
}
```

#### Task Status
```bash
GET /api/v1/task/{task_id}
```

### 🧠 AI Features

#### Intelligent Data Extraction

The AI scraper provides several enhancements over the basic version:

1. **Semantic Analysis**: Understands context and meaning, not just keywords
2. **Entity Recognition**: Automatically identifies:
   - Contact information (phone, email, address)
   - Business hours and policies
   - Amenities and services
   - Nearby attractions and businesses

3. **Content Quality Assessment**: 
   - Confidence scoring based on data completeness
   - Sentiment analysis of website content
   - Freshness indicators

4. **Smart Categorization**:
   - Target audience identification (business, leisure, family)
   - Price range estimation
   - Key selling points extraction

#### Example AI-Enhanced Output

```python
{
  "hotel_name": "Grand Plaza Hotel",
  "confidence_score": 0.85,
  "sentiment_score": 0.78,
  "target_audience": ["Business", "Luxury"],
  "key_selling_points": ["Downtown Location", "Historic Building", "Fine Dining"],
  "price_range_indicator": "Luxury",
  "amenities": {
    "fitness_center": {
      "available": true,
      "hours": "6:00 AM - 10:00 PM",
      "equipment": "Full gym with pool"
    },
    "parking": {
      "available": true,
      "cost": "$25/night",
      "type": "Valet"
    }
  },
  "nearby_attractions": [
    {
      "name": "Art Museum",
      "distance": "0.3 miles",
      "type": "Cultural"
    }
  ]
}
```

### 📊 Data Export Formats

#### RAG-Optimized Text
Perfect for AI assistants and chatbots:
```
HOTEL INFORMATION PROFILE
Hotel Name: Grand Plaza Hotel
Data Quality Score: 0.85/1.0

CONTACT AND LOCATION
Phone: (555) 123-4567
Address: 123 Main Street, Downtown

HOTEL POLICIES
Check-in Time: 3:00 PM
Check-out Time: 11:00 AM
Pet Policy: Pet friendly with fee

AMENITIES
WiFi: Free WiFi available
Fitness Center: Available - Full gym with pool
Pool: Indoor heated pool
```

#### Structured JSON
Machine-readable format with complete data structure.

#### Rich Markdown
Human-readable documentation with formatting.

#### Executive Summary
Quick reference format for key information.

### 🚀 Performance & Scaling

#### Caching Strategy
- Redis caching for frequently requested hotels
- 1-hour cache TTL for data freshness
- Cache invalidation on demand

#### Background Processing
- Celery workers handle intensive scraping
- Prevents API timeouts
- Queue management for high loads

#### Monitoring
- Health check endpoints
- Prometheus metrics
- Error tracking with Sentry
- Comprehensive logging

### 🔒 Security & Best Practices

#### Rate Limiting
- Respectful delays between requests
- User agent rotation
- Anti-detection measures

#### Data Privacy
- No personal data storage
- Temporary processing only
- GDPR compliance considerations

#### Error Handling
- Graceful failure recovery
- Detailed error reporting
- Automatic retries

### 📈 Monitoring & Maintenance

#### Health Monitoring
```bash
# Check app status
doctl apps get $APP_ID

# View logs
doctl apps logs $APP_ID --type run

# Monitor worker processes
doctl apps logs $APP_ID --type worker
```

#### Performance Metrics
- Response times
- Success rates
- Cache hit ratios
- Worker queue status

### 🔧 Troubleshooting

#### Common Issues

1. **AI Models Not Loading**:
   - Ensure sufficient memory allocation
   - Check OpenAI API key configuration
   - Verify internet connectivity for model downloads

2. **Redis Connection Issues**:
   - Verify Redis database is provisioned
   - Check REDIS_URL environment variable
   - Monitor connection limits

3. **Scraping Failures**:
   - Check target website availability
   - Review rate limiting settings
   - Verify Chrome driver compatibility

#### Debugging

```bash
# Check environment variables
doctl apps get $APP_ID --format json | jq '.spec.services[].envs'

# View detailed logs
doctl apps logs $APP_ID --type run --follow

# Test API endpoints
curl https://your-app-url.ondigitalocean.app/api/v1/health
```

### 🎯 Use Cases

#### Front Desk AI Agents
- Real-time hotel information lookup
- Policy and amenity queries
- Guest assistance automation

#### Travel Planning
- Hotel comparison and analysis
- Amenity-based filtering
- Location intelligence

#### Business Intelligence
- Market analysis
- Competitive research
- Pricing insights

#### Content Management
- Website data auditing
- Information standardization
- Quality assessment

### 📚 API Documentation

Visit your deployed app at the root URL to access the interactive API documentation and testing interface.

### 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add comprehensive tests
4. Update documentation
5. Submit a pull request

### 📄 License

MIT License - see LICENSE file for details.

---

**🎉 Your intelligent hotel scraper is now ready for cloud deployment!**

For support or questions, please refer to the troubleshooting section or check the application logs.
