"""
Flask API for Intelligent Hotel Scraper

This module provides a REST API for the intelligent hotel scraper,
designed for deployment on DigitalOcean App Platform.
"""

import os
import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import traceback

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import redis
from celery import Celery
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from prometheus_flask_exporter import PrometheusMetrics

from intelligent_scraper import IntelligentHotelScraper, IntelligentHotelInfo
from dataclasses import asdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Sentry for error tracking
if os.getenv('SENTRY_DSN'):
    sentry_sdk.init(
        dsn=os.getenv('SENTRY_DSN'),
        integrations=[FlaskIntegration()],
        traces_sample_rate=1.0
    )

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize Prometheus metrics
metrics = PrometheusMetrics(app)
metrics.info('app_info', 'Application info', version='1.0.0')

# Configure Redis for caching
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
try:
    redis_client = redis.from_url(redis_url)
    redis_client.ping()
    logger.info("Redis connection established")
except Exception as e:
    logger.warning(f"Redis connection failed: {e}")
    redis_client = None

# Configure Celery for background tasks
celery_broker = os.getenv('CELERY_BROKER_URL', redis_url)
celery_backend = os.getenv('CELERY_RESULT_BACKEND', redis_url)

celery = Celery(
    app.import_name,
    broker=celery_broker,
    backend=celery_backend
)

# API Configuration
API_VERSION = "v1"
MAX_CONCURRENT_SCRAPES = 5
CACHE_TTL = 3600  # 1 hour

# HTML template for simple web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Intelligent Hotel Scraper API</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        .endpoint { background: #ecf0f1; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #3498db; }
        .method { background: #e74c3c; color: white; padding: 3px 8px; border-radius: 3px; font-size: 12px; }
        .method.get { background: #27ae60; }
        .method.post { background: #e74c3c; }
        code { background: #34495e; color: #ecf0f1; padding: 2px 5px; border-radius: 3px; }
        .status { padding: 10px; border-radius: 5px; margin: 10px 0; }
        .status.healthy { background: #d5f4e6; border: 1px solid #27ae60; }
        .status.unhealthy { background: #fadbd8; border: 1px solid #e74c3c; }
        .form-group { margin: 15px 0; }
        input, textarea { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
        button { background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #2980b9; }
        .result { background: #f8f9fa; border: 1px solid #dee2e6; padding: 15px; border-radius: 5px; margin-top: 15px; max-height: 400px; overflow-y: auto; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏨 Intelligent Hotel Scraper API</h1>
        
        <div class="status {{ status_class }}">
            <strong>Service Status:</strong> {{ status_message }}
        </div>
        
        <h2>📊 System Information</h2>
        <ul>
            <li><strong>API Version:</strong> {{ version }}</li>
        <li><strong>AI Models:</strong> {{ ai_status }}</li>
        <li><strong>Redis Cache:</strong> {{ redis_status }}</li>
        <li><strong>Background Tasks:</strong> {{ celery_status }}</li>
    </ul>
    
    <h2>🤖 Free AI Features</h2>
    <ul>
        <li><strong>🧠 Semantic Understanding:</strong> Sentence transformers for content analysis</li>
        <li><strong>🔍 Named Entity Recognition:</strong> Free Hugging Face models</li>
        <li><strong>😊 Sentiment Analysis:</strong> No-cost sentiment scoring</li>
        <li><strong>⭐ Confidence Scoring:</strong> AI-powered data quality assessment</li>
        <li><strong>🎯 Smart Categorization:</strong> Intelligent content classification</li>
    </ul>        <h2>🔗 API Endpoints</h2>
        
        <div class="endpoint">
            <span class="method get">GET</span> <code>/api/v1/health</code>
            <p>Health check endpoint</p>
        </div>
        
        <div class="endpoint">
            <span class="method post">POST</span> <code>/api/v1/scrape</code>
            <p>Scrape a single hotel URL</p>
            <strong>Body:</strong> <code>{"url": "https://hotel-website.com", "hotel_name": "Hotel Name"}</code>
        </div>
        
        <div class="endpoint">
            <span class="method post">POST</span> <code>/api/v1/scrape/batch</code>
            <p>Scrape multiple hotels</p>
            <strong>Body:</strong> <code>{"hotels": [{"url": "...", "name": "..."}]}</code>
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span> <code>/api/v1/task/{task_id}</code>
            <p>Get task status and results</p>
        </div>
        
        <h2>🧪 Test the API</h2>
        <form id="scrapeForm">
            <div class="form-group">
                <label><strong>Hotel URL:</strong></label>
                <input type="url" id="hotelUrl" placeholder="https://www.example-hotel.com" required>
            </div>
            <div class="form-group">
                <label><strong>Hotel Name (optional):</strong></label>
                <input type="text" id="hotelName" placeholder="Example Hotel">
            </div>
            <button type="submit">🚀 Scrape Hotel</button>
        </form>
        
        <div id="result" class="result" style="display:none;">
            <h3>Result:</h3>
            <pre id="resultContent"></pre>
        </div>
    </div>
    
    <script>
        document.getElementById('scrapeForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const url = document.getElementById('hotelUrl').value;
            const name = document.getElementById('hotelName').value;
            
            const resultDiv = document.getElementById('result');
            const resultContent = document.getElementById('resultContent');
            
            resultDiv.style.display = 'block';
            resultContent.textContent = 'Scraping in progress... This may take 30-60 seconds.';
            
            try {
                const response = await fetch('/api/v1/scrape', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        url: url,
                        hotel_name: name || null
                    })
                });
                
                const data = await response.json();
                resultContent.textContent = JSON.stringify(data, null, 2);
            } catch (error) {
                resultContent.textContent = 'Error: ' + error.message;
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Serve the main interface"""
    try:
        # Check system status
        ai_status = "✅ Free AI Enabled" if os.getenv('USE_FREE_AI', 'true').lower() == 'true' else "❌ Disabled"
        redis_status = "✅ Connected" if redis_client and redis_client.ping() else "❌ Disconnected"
        celery_status = "✅ Running" if celery_broker else "❌ Not configured"
        
        status_class = "healthy"
        status_message = "All systems operational"
        
        if not redis_client:
            status_class = "unhealthy"
            status_message = "Cache unavailable"
    
    except Exception as e:
        status_class = "unhealthy"
        status_message = f"System error: {str(e)}"
        ai_status = "❌ Unknown"
        redis_status = "❌ Unknown"
        celery_status = "❌ Unknown"
    
    return render_template_string(HTML_TEMPLATE,
        version=API_VERSION,
        status_class=status_class,
        status_message=status_message,
        ai_status=ai_status,
        redis_status=redis_status,
        celery_status=celery_status
    )

@app.route(f'/api/{API_VERSION}/health')
def health_check():
    """Health check endpoint"""
    try:
        # Test Redis connection
        redis_healthy = False
        if redis_client:
            redis_client.ping()
            redis_healthy = True
        
        # Test AI model availability
        ai_healthy = os.getenv('USE_FREE_AI', 'true').lower() == 'true'
        
        status = {
            "status": "healthy" if redis_healthy and ai_healthy else "degraded",
            "timestamp": datetime.now().isoformat(),
            "version": API_VERSION,
            "components": {
                "redis": "healthy" if redis_healthy else "unhealthy",
                "ai_models": "healthy" if ai_healthy else "degraded",
                "scraper": "healthy"
            }
        }
        
        return jsonify(status), 200 if status["status"] == "healthy" else 503
        
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 503

@app.route(f'/api/{API_VERSION}/scrape', methods=['POST'])
def scrape_hotel():
    """Scrape a single hotel"""
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({"error": "URL is required"}), 400
        
        url = data['url']
        hotel_name = data.get('hotel_name')
        use_cache = data.get('use_cache', True)
        
        # Check cache first
        cache_key = f"hotel_scrape:{hash(url)}"
        if use_cache and redis_client:
            try:
                cached_result = redis_client.get(cache_key)
                if cached_result:
                    logger.info(f"Cache hit for {url}")
                    return jsonify({
                        "status": "success",
                        "data": json.loads(cached_result),
                        "cached": True,
                        "timestamp": datetime.now().isoformat()
                    })
            except Exception as e:
                logger.warning(f"Cache read error: {e}")
        
        # Start background scraping task
        task = scrape_hotel_task.delay(url, hotel_name)
        
        return jsonify({
            "status": "processing",
            "task_id": task.id,
            "estimated_time": "30-60 seconds",
            "check_status_url": f"/api/{API_VERSION}/task/{task.id}"
        }), 202
        
    except Exception as e:
        logger.error(f"Scraping error: {e}")
        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500

@app.route(f'/api/{API_VERSION}/scrape/batch', methods=['POST'])
def scrape_hotels_batch():
    """Scrape multiple hotels"""
    try:
        data = request.get_json()
        
        if not data or 'hotels' not in data or not isinstance(data['hotels'], list):
            return jsonify({"error": "Hotels list is required"}), 400
        
        hotels = data['hotels']
        
        if len(hotels) > 10:  # Limit batch size
            return jsonify({"error": "Maximum 10 hotels per batch"}), 400
        
        # Start batch scraping task
        task = scrape_hotels_batch_task.delay(hotels)
        
        return jsonify({
            "status": "processing",
            "task_id": task.id,
            "hotel_count": len(hotels),
            "estimated_time": f"{len(hotels) * 45} seconds",
            "check_status_url": f"/api/{API_VERSION}/task/{task.id}"
        }), 202
        
    except Exception as e:
        logger.error(f"Batch scraping error: {e}")
        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500

@app.route(f'/api/{API_VERSION}/task/<task_id>')
def get_task_status(task_id):
    """Get task status and results"""
    try:
        task = celery.AsyncResult(task_id)
        
        if task.state == 'PENDING':
            response = {
                "status": "pending",
                "message": "Task is waiting to be processed"
            }
        elif task.state == 'PROGRESS':
            response = {
                "status": "processing",
                "progress": task.info.get('progress', 0),
                "message": task.info.get('message', 'Processing...')
            }
        elif task.state == 'SUCCESS':
            response = {
                "status": "completed",
                "data": task.result,
                "timestamp": datetime.now().isoformat()
            }
        else:  # FAILURE
            response = {
                "status": "failed",
                "error": str(task.info),
                "timestamp": datetime.now().isoformat()
            }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

# Celery tasks
@celery.task(bind=True)
def scrape_hotel_task(self, url: str, hotel_name: str = None):
    """Background task for scraping a single hotel"""
    try:
        self.update_state(state='PROGRESS', meta={'progress': 0, 'message': 'Initializing scraper...'})
        
        # Initialize scraper
        scraper = IntelligentHotelScraper(headless=True, use_ai=True)
        
        try:
            self.update_state(state='PROGRESS', meta={'progress': 25, 'message': 'Scraping hotel data...'})
            
            # Run the async scraping function
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            hotel_data = loop.run_until_complete(
                scraper.scrape_hotel_intelligent(url, hotel_name)
            )
            
            self.update_state(state='PROGRESS', meta={'progress': 80, 'message': 'Processing results...'})
            
            # Convert to dict for JSON serialization
            result = asdict(hotel_data)
            
            # Cache the result
            if redis_client:
                try:
                    cache_key = f"hotel_scrape:{hash(url)}"
                    redis_client.setex(cache_key, CACHE_TTL, json.dumps(result))
                except Exception as e:
                    logger.warning(f"Cache write error: {e}")
            
            self.update_state(state='PROGRESS', meta={'progress': 100, 'message': 'Completed'})
            
            return {
                "hotel_data": result,
                "metadata": {
                    "scraped_at": datetime.now().isoformat(),
                    "confidence_score": hotel_data.confidence_score,
                    "ai_enhanced": True
                }
            }
            
        finally:
            scraper.close()
            
    except Exception as e:
        logger.error(f"Task error for {url}: {e}")
        self.update_state(
            state='FAILURE',
            meta={'error': str(e), 'traceback': traceback.format_exc()}
        )
        raise

@celery.task(bind=True)
def scrape_hotels_batch_task(self, hotels: List[Dict[str, str]]):
    """Background task for scraping multiple hotels"""
    try:
        results = []
        total_hotels = len(hotels)
        
        scraper = IntelligentHotelScraper(headless=True, use_ai=True)
        
        try:
            for i, hotel in enumerate(hotels):
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'progress': int((i / total_hotels) * 100),
                        'message': f'Scraping {hotel.get("name", hotel["url"])} ({i+1}/{total_hotels})'
                    }
                )
                
                try:
                    # Run the async scraping function
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    hotel_data = loop.run_until_complete(
                        scraper.scrape_hotel_intelligent(hotel['url'], hotel.get('name'))
                    )
                    
                    results.append({
                        "url": hotel['url'],
                        "status": "success",
                        "data": asdict(hotel_data)
                    })
                    
                except Exception as e:
                    logger.error(f"Failed to scrape {hotel['url']}: {e}")
                    results.append({
                        "url": hotel['url'],
                        "status": "failed",
                        "error": str(e)
                    })
                
                # Rate limiting
                if i < total_hotels - 1:  # Don't wait after the last hotel
                    asyncio.sleep(2)
            
            return {
                "results": results,
                "summary": {
                    "total": total_hotels,
                    "successful": len([r for r in results if r["status"] == "success"]),
                    "failed": len([r for r in results if r["status"] == "failed"]),
                    "completion_time": datetime.now().isoformat()
                }
            }
            
        finally:
            scraper.close()
            
    except Exception as e:
        logger.error(f"Batch task error: {e}")
        self.update_state(
            state='FAILURE',
            meta={'error': str(e), 'traceback': traceback.format_exc()}
        )
        raise

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    # For development only
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    app.run(host='0.0.0.0', port=port, debug=debug)
