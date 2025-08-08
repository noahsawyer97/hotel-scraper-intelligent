"""
Intelligent Hotel Scraper with AI Enhancement

This module provides an advanced hotel scraper with AI-powered content extraction,
semantic analysis, and intelligent data structuring for RAG systems.
"""

import json
import logging
import asyncio
import aiohttp
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union
from dataclasses import dataclass, asdict
import re
import time
import random

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, WebDriverException

# Heavy AI libraries - optional imports for disk space optimization
try:
    from transformers import pipeline, AutoTokenizer, AutoModel
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("⚠️  PyTorch/Transformers not available - using lightweight AI mode")

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("⚠️  Sentence Transformers not available - using basic semantic analysis")

import spacy
from textstat import flesch_reading_ease
import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
console = Console()

# Free AI configuration
USE_FREE_AI = os.getenv('USE_FREE_AI', 'true').lower() == 'true'
HUGGINGFACE_TOKEN = os.getenv('HUGGINGFACE_TOKEN')  # Optional for free models

# Conditional OpenAI import
try:
    import openai
    OPENAI_AVAILABLE = True
    # Configure OpenAI client
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if openai_api_key:
        openai.api_key = openai_api_key
        USE_OPENAI_API = os.getenv('USE_OPENAI_API', 'false').lower() == 'true'
    else:
        USE_OPENAI_API = False
        logger.warning("OPENAI_API_KEY not found in environment variables")
except ImportError:
    OPENAI_AVAILABLE = False
    USE_OPENAI_API = False
    if not USE_FREE_AI:
        logger.warning("OpenAI not available, falling back to free AI models")

@dataclass
class IntelligentHotelInfo:
    """Enhanced hotel information with AI-extracted insights"""
    # Basic info
    hotel_name: str
    website_url: str
    scraped_at: str
    confidence_score: float = 0.0
    
    # Contact & Location (AI-enhanced)
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    coordinates: Optional[Dict[str, float]] = None  # lat, lng
    
    # Policies (AI-extracted)
    checkin_time: Optional[str] = None
    checkout_time: Optional[str] = None
    early_checkin_policy: Optional[str] = None
    late_checkout_policy: Optional[str] = None
    cancellation_policy: Optional[str] = None
    deposit_policy: Optional[str] = None
    age_restrictions: Optional[str] = None
    
    # Parking & Transportation (semantic analysis)
    parking_available: Optional[bool] = None
    parking_cost: Optional[str] = None
    parking_type: Optional[str] = None
    parking_spaces: Optional[int] = None
    shuttle_service: Optional[str] = None
    public_transit_info: Optional[str] = None
    distance_to_airport: Optional[str] = None
    
    # Amenities (AI-categorized)
    wifi_info: Optional[str] = None
    fitness_center: Optional[Dict[str, str]] = None  # hours, equipment, etc.
    pool: Optional[Dict[str, str]] = None  # type, hours, seasonal
    spa_services: Optional[List[str]] = None
    business_center: Optional[Dict[str, str]] = None
    pet_policy: Optional[Dict[str, str]] = None  # fees, restrictions, amenities
    smoking_policy: Optional[str] = None
    accessibility_features: Optional[List[str]] = None
    
    # Dining (AI-structured)
    restaurants: List[Dict[str, str]] = None
    room_service: Optional[Dict[str, str]] = None  # hours, menu type, etc.
    breakfast_info: Optional[Dict[str, str]] = None  # type, cost, hours
    bars_lounges: Optional[List[Dict[str, str]]] = None
    
    # Room Information (AI-extracted)
    room_types: Optional[List[Dict[str, str]]] = None
    room_amenities: Optional[List[str]] = None
    room_sizes: Optional[Dict[str, str]] = None
    
    # Location Intelligence
    nearby_attractions: List[Dict[str, str]] = None  # name, distance, type
    nearby_restaurants: List[Dict[str, str]] = None
    nearby_shopping: List[Dict[str, str]] = None
    nearby_transportation: List[Dict[str, str]] = None
    walkability_score: Optional[float] = None
    
    # Services (AI-categorized)
    concierge_services: List[str] = None
    laundry_service: Optional[Dict[str, str]] = None
    luggage_storage: Optional[str] = None
    meeting_facilities: Optional[Dict[str, str]] = None
    event_services: Optional[List[str]] = None
    
    # AI-generated insights
    sentiment_score: Optional[float] = None  # Overall sentiment of content
    key_selling_points: Optional[List[str]] = None
    target_audience: Optional[List[str]] = None  # business, leisure, family, etc.
    price_range_indicator: Optional[str] = None  # budget, mid-range, luxury
    unique_features: Optional[List[str]] = None
    
    # Content quality metrics
    content_completeness_score: Optional[float] = None
    data_freshness_indicators: Optional[List[str]] = None
    
    def __post_init__(self):
        """Initialize list fields"""
        list_fields = [
            'restaurants', 'spa_services', 'accessibility_features', 'bars_lounges',
            'room_types', 'room_amenities', 'nearby_attractions', 'nearby_restaurants',
            'nearby_shopping', 'nearby_transportation', 'concierge_services',
            'event_services', 'key_selling_points', 'target_audience', 'unique_features',
            'data_freshness_indicators'
        ]
        
        for field in list_fields:
            if getattr(self, field) is None:
                setattr(self, field, [])

class IntelligentHotelScraper:
    """AI-enhanced hotel scraper with semantic understanding"""
    
    def __init__(self, headless: bool = True, use_ai: bool = True):
        self.headless = headless
        self.use_ai = use_ai
        self.driver = None
        
        # Initialize AI models
        if self.use_ai:
            self._initialize_ai_models()
    
    def _initialize_ai_models(self):
        """Initialize AI models with fallbacks for missing libraries"""
        try:
            logger.info("Initializing AI models in lightweight mode...")
            
            # Check available AI libraries
            if not TORCH_AVAILABLE:
                logger.warning("PyTorch not available - advanced text generation disabled")
                self.text_generator = None
            else:
                # Check for GPU availability
                device = "cuda" if torch.cuda.is_available() else "cpu"
                logger.info(f"Using device: {device}")
                
                # Try to initialize text generation model
                try:
                    if torch.cuda.is_available():
                        # GPU available - use full model with GPU acceleration
                        self.text_generator = pipeline(
                            "text-generation",
                            model="openai/gpt-oss-20b",
                            token=HUGGINGFACE_TOKEN,
                            device_map="auto",
                            torch_dtype=torch.float16,
                            max_length=2048,
                            do_sample=True,
                            temperature=0.7,
                            pad_token_id=50256
                        )
                        logger.info("✅ GPT-oss-20b loaded successfully")
                    else:
                        # Use smaller CPU-friendly model
                        self.text_generator = pipeline(
                            "text-generation",
                            model="distilgpt2",
                            device=-1,  # CPU
                            max_length=512
                        )
                        logger.info("✅ DistilGPT2 loaded for CPU")
                        
                except Exception as e:
                    logger.warning(f"Text generation model failed: {e}")
                    self.text_generator = None
            
            # Sentence transformer for embeddings
            if not SENTENCE_TRANSFORMERS_AVAILABLE:
                logger.warning("Sentence Transformers not available - using basic similarity")
                self.sentence_transformer = None
            else:
                try:
                    device_for_st = "cuda" if TORCH_AVAILABLE and torch.cuda.is_available() else "cpu"
                    self.sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2', device=device_for_st)
                    logger.info(f"✅ Sentence transformer loaded on {device_for_st}")
                except Exception as e:
                    logger.warning(f"Sentence transformer failed: {e}")
                    self.sentence_transformer = None
            
            # Simple NER with spaCy (lightweight)
            try:
                self.nlp = spacy.load("en_core_web_sm")
                logger.info("✅ spaCy NER loaded")
            except OSError:
                logger.warning("spaCy model not found. Using basic text processing")
                self.nlp = None
            
            # Text statistics (lightweight)
            try:
                import textstat
                self.textstat = textstat
                logger.info("✅ Text statistics available")
            except ImportError:
                self.textstat = None
                logger.info("Text statistics not available (optional)")
            
            logger.info("🎉 AI models initialized (lightweight mode)")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI models: {e}")
            logger.info("Continuing with basic extraction (no AI features)")
            self.use_ai = False
            self.text_generator = None
            self.sentence_transformer = None
            self.nlp = None
            self.textstat = None
    
    def setup_driver(self):
        """Initialize Chrome WebDriver with enhanced options"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        
        # Enhanced Chrome options for better scraping
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")  # Faster loading
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Rotate user agents
        user_agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        chrome_options.add_argument(f"--user-agent={random.choice(user_agents)}")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Execute script to hide automation
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return self.driver
    
    async def scrape_hotel_intelligent(self, url: str, hotel_name: str = None) -> IntelligentHotelInfo:
        """Intelligently scrape hotel with AI enhancement"""
        if not self.driver:
            self.setup_driver()
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                
                task = progress.add_task(f"Scraping {url}...", total=None)
                
                # Load page with retry mechanism
                for attempt in range(3):
                    try:
                        progress.update(task, description=f"Loading page (attempt {attempt + 1})...")
                        self.driver.get(url)
                        
                        # Wait for content to load
                        WebDriverWait(self.driver, 15).until(
                            EC.presence_of_element_located((By.TAG_NAME, "body"))
                        )
                        
                        # Additional wait for dynamic content
                        await asyncio.sleep(2)
                        
                        # Scroll to load lazy content
                        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        await asyncio.sleep(1)
                        self.driver.execute_script("window.scrollTo(0, 0);")
                        
                        break
                        
                    except TimeoutException:
                        if attempt == 2:
                            raise
                        await asyncio.sleep(2)
                
                progress.update(task, description="Parsing page content...")
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                
                # Initialize hotel info
                hotel_info = IntelligentHotelInfo(
                    hotel_name=hotel_name or await self._extract_hotel_name_ai(soup),
                    website_url=url,
                    scraped_at=datetime.now().isoformat()
                )
                
                # AI-enhanced extraction with parallel processing
                extraction_tasks = [
                    self._extract_contact_info_ai(soup, hotel_info),
                    self._extract_policies_ai(soup, hotel_info),
                    self._extract_amenities_ai(soup, hotel_info),
                    self._extract_dining_info_ai(soup, hotel_info),
                    self._extract_nearby_info_ai(soup, hotel_info),
                    self._extract_services_ai(soup, hotel_info),
                    self._extract_room_info_ai(soup, hotel_info)
                ]
                
                progress.update(task, description="AI-enhanced content extraction...")
                await asyncio.gather(*extraction_tasks)
                
                if self.use_ai:
                    progress.update(task, description="Generating AI insights...")
                    await self._generate_ai_insights(soup, hotel_info)
                
                progress.update(task, description="Calculating confidence score...")
                hotel_info.confidence_score = self._calculate_confidence_score(hotel_info)
                
                return hotel_info
                
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            raise
    
    def scrape_hotel(self, url: str, hotel_name: str = None) -> IntelligentHotelInfo:
        """Synchronous wrapper for scrape_hotel_intelligent"""
        return asyncio.run(self.scrape_hotel_intelligent(url, hotel_name))
    
    async def _extract_with_openai(self, content: str, extraction_type: str, context: str = "") -> Dict:
        """Use OpenAI API for intelligent content extraction"""
        if not USE_OPENAI_API or not OPENAI_AVAILABLE:
            return {}
            
        try:
            # Create extraction prompts based on type
            prompts = {
                "hotel_info": f"""
Extract hotel information from this webpage content. Return a JSON object with these fields:
- hotel_name: The official name of the hotel
- phone: Phone number (format: clean, no extra text)
- email: Email address if found
- address: Full street address
- city: City name
- state: State/province
- zip_code: ZIP or postal code

Content: {content[:3000]}

Return only valid JSON:""",

                "policies": f"""
Extract hotel policies from this content. Return JSON with these fields:
- checkin_time: Check-in time (e.g., "3:00 PM")
- checkout_time: Check-out time (e.g., "11:00 AM")
- cancellation_policy: Brief summary of cancellation rules
- deposit_policy: Information about deposits or holds
- age_restrictions: Any age-related policies
- early_checkin_policy: Early check-in information
- late_checkout_policy: Late check-out information

Content: {content[:3000]}

Return only valid JSON:""",

                "amenities": f"""
Extract hotel amenities and services from this content. Return JSON with these fields:
- amenities: Array of amenity names (pool, gym, wifi, etc.)
- business_services: Array of business-related services
- recreational_services: Array of recreational activities
- accessibility_features: Array of accessibility features

Content: {content[:3000]}

Return only valid JSON:""",

                "dining": f"""
Extract dining information from this content. Return JSON with these fields:
- restaurants: Array of restaurant names and descriptions
- bars_lounges: Array of bar/lounge information
- room_service: Room service information
- breakfast_info: Breakfast details and hours

Content: {content[:3000]}

Return only valid JSON:"""
            }
            
            prompt = prompts.get(extraction_type, "")
            if not prompt:
                return {}
                
            # Call OpenAI API
            client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a hotel information extraction expert. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.1
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Try to parse JSON response
            try:
                # Clean up response (remove markdown formatting if present)
                if result_text.startswith("```json"):
                    result_text = result_text.split("```json")[1].split("```")[0]
                elif result_text.startswith("```"):
                    result_text = result_text.split("```")[1].split("```")[0]
                    
                return json.loads(result_text)
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse OpenAI JSON response for {extraction_type}")
                return {}
                
        except Exception as e:
            logger.error(f"OpenAI extraction failed for {extraction_type}: {e}")
            return {}

    async def _extract_hotel_name_ai(self, soup: BeautifulSoup) -> str:
        """AI-enhanced hotel name extraction"""
        # Multiple strategies for finding hotel name
        strategies = [
            # Direct selectors
            lambda: soup.select_one('h1').get_text(strip=True) if soup.select_one('h1') else None,
            lambda: soup.select_one('[data-testid*="hotel"]').get_text(strip=True) if soup.select_one('[data-testid*="hotel"]') else None,
            lambda: soup.select_one('.hotel-name, .property-name').get_text(strip=True) if soup.select_one('.hotel-name, .property-name') else None,
            
            # Meta tags
            lambda: soup.select_one('meta[property="og:title"]').get('content') if soup.select_one('meta[property="og:title"]') else None,
            lambda: soup.select_one('meta[name="twitter:title"]').get('content') if soup.select_one('meta[name="twitter:title"]') else None,
            lambda: soup.select_one('title').get_text(strip=True) if soup.select_one('title') else None,
            
            # Schema.org markup
            lambda: soup.select_one('[itemtype*="Hotel"] [itemprop="name"]').get_text(strip=True) if soup.select_one('[itemtype*="Hotel"] [itemprop="name"]') else None,
        ]
        
        for strategy in strategies:
            try:
                name = strategy()
                if name and len(name) > 3:
                    # Clean the name using AI if available
                    if self.use_ai and self.nlp:
                        doc = self.nlp(name)
                        # Extract proper nouns that might be hotel names
                        entities = [ent.text for ent in doc.ents if ent.label_ in ["ORG", "GPE"]]
                        if entities:
                            return entities[0]
                    return name
            except:
                continue
        
        return "Unknown Hotel"
    
    async def _extract_contact_info_ai(self, soup: BeautifulSoup, hotel_info: IntelligentHotelInfo):
        """AI-enhanced contact information extraction"""
        # Try OpenAI first if available
        if USE_OPENAI_API and OPENAI_AVAILABLE:
            content = self._extract_meaningful_content(soup)
            openai_result = await self._extract_with_openai(content, "hotel_info")
            
            if openai_result:
                # Update hotel info with OpenAI results
                for field in ['phone', 'email', 'address', 'city', 'state', 'zip_code']:
                    if field in openai_result and openai_result[field]:
                        setattr(hotel_info, field, openai_result[field])
                
                # Also update hotel name if found
                if 'hotel_name' in openai_result and openai_result['hotel_name']:
                    hotel_info.hotel_name = openai_result['hotel_name']
                
                return  # OpenAI extraction successful, skip fallback
        
        # Fallback to traditional extraction methods
        text = soup.get_text()
        
        if self.use_ai and self.nlp:
            # Use NER to find contact information
            doc = self.nlp(text[:2000])  # Limit text for performance
            
            for ent in doc.ents:
                if ent.label_ == "PERSON" and '@' in ent.text:
                    hotel_info.email = ent.text
                elif ent.label_ in ["GPE", "LOC"] and not hotel_info.address:
                    hotel_info.address = ent.text
        
        # Phone number extraction with improved patterns
        phone_patterns = [
            r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b',
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            r'\(\d{3}\)\s*\d{3}[-.]?\d{4}'
        ]
        
        for pattern in phone_patterns:
            match = re.search(pattern, text)
            if match:
                hotel_info.phone = match.group()
                break
        
        # Email extraction
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match and not hotel_info.email:
            hotel_info.email = email_match.group()
    
    async def _extract_policies_ai(self, soup: BeautifulSoup, hotel_info: IntelligentHotelInfo):
        """AI-enhanced policy extraction"""
        # Try OpenAI first if available
        if USE_OPENAI_API and OPENAI_AVAILABLE:
            content = self._extract_meaningful_content(soup)
            openai_result = await self._extract_with_openai(content, "policies")
            
            if openai_result:
                # Update hotel info with OpenAI results
                policy_fields = [
                    'checkin_time', 'checkout_time', 'cancellation_policy', 
                    'deposit_policy', 'age_restrictions', 'early_checkin_policy', 
                    'late_checkout_policy'
                ]
                for field in policy_fields:
                    if field in openai_result and openai_result[field]:
                        setattr(hotel_info, field, openai_result[field])
                return  # OpenAI extraction successful, skip fallback
        
        # Fallback to traditional extraction
        text = soup.get_text().lower()
        
        # Enhanced time extraction with context understanding
        time_patterns = {
            'checkin': [
                r'check[- ]?in(?:\s+time)?:?\s*(\d{1,2}:?\d{0,2}\s*[ap]m)',
                r'arrival(?:\s+time)?:?\s*(\d{1,2}:?\d{0,2}\s*[ap]m)',
                r'checkin\s+(?:starts?|begins?)\s+(?:at\s+)?(\d{1,2}:?\d{0,2}\s*[ap]m)'
            ],
            'checkout': [
                r'check[- ]?out(?:\s+time)?:?\s*(\d{1,2}:?\d{0,2}\s*[ap]m)',
                r'departure(?:\s+time)?:?\s*(\d{1,2}:?\d{0,2}\s*[ap]m)',
                r'checkout\s+(?:is\s+)?(?:by\s+)?(\d{1,2}:?\d{0,2}\s*[ap]m)'
            ]
        }
        
        for policy_type, patterns in time_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text)
                if match:
                    if policy_type == 'checkin':
                        hotel_info.checkin_time = match.group(1)
                    else:
                        hotel_info.checkout_time = match.group(1)
                    break
        
        # Enhanced parking analysis
        parking_context = self._extract_context_around_keyword(text, 'parking', 100)
        if parking_context:
            hotel_info.parking_available = True
            
            if any(word in parking_context for word in ['free', 'complimentary', 'no charge']):
                hotel_info.parking_cost = "Free"
            elif 'valet' in parking_context:
                hotel_info.parking_type = "Valet"
            elif any(word in parking_context for word in ['self-park', 'self park', 'self service']):
                hotel_info.parking_type = "Self-park"
            
            # Extract parking cost if mentioned
            cost_match = re.search(r'\$(\d+(?:\.\d{2})?)', parking_context)
            if cost_match:
                hotel_info.parking_cost = f"${cost_match.group(1)}"
    
    def _extract_context_around_keyword(self, text: str, keyword: str, context_size: int = 50) -> str:
        """Extract text context around a keyword"""
        keyword_pos = text.find(keyword.lower())
        if keyword_pos == -1:
            return ""
        
        start = max(0, keyword_pos - context_size)
        end = min(len(text), keyword_pos + len(keyword) + context_size)
        return text[start:end]
    
    async def _extract_amenities_ai(self, soup: BeautifulSoup, hotel_info: IntelligentHotelInfo):
        """AI-enhanced amenities extraction with categorization"""
        text = soup.get_text().lower()
        
        # Define amenity categories with keywords
        amenity_categories = {
            'wifi': ['wifi', 'wi-fi', 'internet', 'wireless'],
            'fitness': ['fitness', 'gym', 'exercise', 'workout'],
            'pool': ['pool', 'swimming', 'aquatic'],
            'spa': ['spa', 'massage', 'wellness', 'treatment'],
            'business': ['business center', 'meeting room', 'conference'],
            'pets': ['pet', 'dog', 'cat', 'animal'],
            'accessibility': ['accessible', 'wheelchair', 'ada', 'disability']
        }
        
        # Enhanced amenity extraction
        for category, keywords in amenity_categories.items():
            for keyword in keywords:
                if keyword in text:
                    context = self._extract_context_around_keyword(text, keyword, 80)
                    
                    if category == 'wifi':
                        if any(term in context for term in ['free', 'complimentary']):
                            hotel_info.wifi_info = "Free WiFi available"
                        else:
                            hotel_info.wifi_info = "WiFi available"
                    
                    elif category == 'fitness':
                        hours_match = re.search(r'(\d{1,2}:?\d{0,2}\s*[ap]m.*?\d{1,2}:?\d{0,2}\s*[ap]m)', context)
                        hotel_info.fitness_center = {
                            'available': True,
                            'hours': hours_match.group(1) if hours_match else 'Check with hotel',
                            'details': context[:100]
                        }
                    
                    elif category == 'pool':
                        pool_types = ['indoor', 'outdoor', 'heated', 'seasonal']
                        pool_type = next((ptype for ptype in pool_types if ptype in context), 'Standard')
                        hotel_info.pool = {
                            'available': True,
                            'type': pool_type,
                            'details': context[:100]
                        }
                    
                    elif category == 'spa':
                        if not hotel_info.spa_services:
                            hotel_info.spa_services = []
                        spa_services = ['massage', 'facial', 'manicure', 'pedicure', 'sauna']
                        found_services = [service for service in spa_services if service in context]
                        hotel_info.spa_services.extend(found_services)
                    
                    elif category == 'pets':
                        if 'friendly' in context or 'welcome' in context:
                            hotel_info.pet_policy = {'allowed': True, 'details': context[:100]}
                        elif 'not allowed' in context or 'no pets' in context:
                            hotel_info.pet_policy = {'allowed': False, 'details': context[:100]}
                    
                    break
    
    async def _extract_dining_info_ai(self, soup: BeautifulSoup, hotel_info: IntelligentHotelInfo):
        """AI-enhanced dining information extraction"""
        # Look for structured restaurant data
        restaurant_elements = soup.find_all(['div', 'section'], class_=re.compile(r'restaurant|dining|food'))
        
        restaurants = []
        for element in restaurant_elements[:5]:  # Limit results
            restaurant_text = element.get_text(strip=True)
            
            if len(restaurant_text) > 20:  # Filter out noise
                # Extract restaurant name
                name_element = element.find(['h1', 'h2', 'h3', 'h4'])
                name = name_element.get_text(strip=True) if name_element else "Restaurant"
                
                # Extract cuisine type using AI
                cuisine_keywords = ['italian', 'asian', 'american', 'french', 'mexican', 'seafood', 'steakhouse']
                cuisine = next((cuisine for cuisine in cuisine_keywords if cuisine in restaurant_text.lower()), 'International')
                
                # Extract hours
                hours_match = re.search(r'(\d{1,2}:?\d{0,2}\s*[ap]m.*?\d{1,2}:?\d{0,2}\s*[ap]m)', restaurant_text.lower())
                hours = hours_match.group(1) if hours_match else 'Check with hotel'
                
                restaurants.append({
                    'name': name,
                    'cuisine': cuisine,
                    'hours': hours,
                    'details': restaurant_text[:200]
                })
        
        hotel_info.restaurants = restaurants
        
        # Room service extraction
        text = soup.get_text().lower()
        if 'room service' in text:
            room_service_context = self._extract_context_around_keyword(text, 'room service', 100)
            hours_match = re.search(r'(\d{1,2}:?\d{0,2}\s*[ap]m.*?\d{1,2}:?\d{0,2}\s*[ap]m)', room_service_context)
            
            hotel_info.room_service = {
                'available': True,
                'hours': hours_match.group(1) if hours_match else '24 hours',
                'details': room_service_context[:100]
            }
        
        # Breakfast information
        breakfast_keywords = ['breakfast', 'morning meal', 'continental breakfast']
        for keyword in breakfast_keywords:
            if keyword in text:
                breakfast_context = self._extract_context_around_keyword(text, keyword, 100)
                breakfast_type = 'Continental'
                
                if 'complimentary' in breakfast_context or 'free' in breakfast_context:
                    cost = 'Complimentary'
                elif 'buffet' in breakfast_context:
                    breakfast_type = 'Buffet'
                    cost = 'Additional charge'
                else:
                    cost = 'Check with hotel'
                
                hotel_info.breakfast_info = {
                    'available': True,
                    'type': breakfast_type,
                    'cost': cost,
                    'details': breakfast_context[:100]
                }
                break
    
    async def _extract_nearby_info_ai(self, soup: BeautifulSoup, hotel_info: IntelligentHotelInfo):
        """AI-enhanced nearby attractions extraction with categorization"""
        text = soup.get_text()
        
        if self.use_ai and self.nlp:
            # Use spaCy for location and organization extraction
            doc = self.nlp(text[:3000])  # Limit for performance
            
            attractions = []
            restaurants = []
            shopping = []
            
            for ent in doc.ents:
                if ent.label_ in ["ORG", "GPE", "FAC"]:
                    entity_text = ent.text.lower()
                    
                    # Categorize based on keywords
                    if any(keyword in entity_text for keyword in ['museum', 'park', 'theater', 'gallery', 'center']):
                        attractions.append({
                            'name': ent.text,
                            'type': 'Attraction',
                            'distance': 'Unknown'
                        })
                    elif any(keyword in entity_text for keyword in ['restaurant', 'cafe', 'bar', 'bistro']):
                        restaurants.append({
                            'name': ent.text,
                            'type': 'Restaurant',
                            'distance': 'Unknown'
                        })
                    elif any(keyword in entity_text for keyword in ['mall', 'shop', 'market', 'store']):
                        shopping.append({
                            'name': ent.text,
                            'type': 'Shopping',
                            'distance': 'Unknown'
                        })
            
            hotel_info.nearby_attractions = attractions[:10]
            hotel_info.nearby_restaurants = restaurants[:10]
            hotel_info.nearby_shopping = shopping[:10]
    
    async def _extract_services_ai(self, soup: BeautifulSoup, hotel_info: IntelligentHotelInfo):
        """AI-enhanced services extraction"""
        text = soup.get_text().lower()
        
        service_categories = {
            'concierge': ['concierge', 'guest services', 'front desk'],
            'laundry': ['laundry', 'dry cleaning', 'valet service'],
            'luggage': ['luggage storage', 'baggage', 'bell hop'],
            'transportation': ['shuttle', 'car service', 'taxi', 'uber'],
            'meeting': ['meeting room', 'conference', 'event space'],
            'wellness': ['spa', 'massage', 'wellness center']
        }
        
        services = []
        for category, keywords in service_categories.items():
            for keyword in keywords:
                if keyword in text:
                    context = self._extract_context_around_keyword(text, keyword, 60)
                    services.append(f"{keyword.title()} - {context[:50]}...")
                    break
        
        hotel_info.concierge_services = services
    
    async def _extract_room_info_ai(self, soup: BeautifulSoup, hotel_info: IntelligentHotelInfo):
        """AI-enhanced room information extraction"""
        # Look for room-related sections
        room_elements = soup.find_all(['div', 'section'], class_=re.compile(r'room|suite|accommodation'))
        
        room_types = []
        amenities = []
        
        for element in room_elements[:5]:
            room_text = element.get_text(strip=True).lower()
            
            # Extract room types
            room_type_keywords = ['standard', 'deluxe', 'suite', 'premium', 'executive', 'junior suite']
            for room_type in room_type_keywords:
                if room_type in room_text:
                    room_types.append({
                        'type': room_type.title(),
                        'description': room_text[:150]
                    })
                    break
            
            # Extract amenities
            amenity_keywords = ['air conditioning', 'minibar', 'coffee maker', 'safe', 'balcony', 'view']
            for amenity in amenity_keywords:
                if amenity in room_text and amenity not in amenities:
                    amenities.append(amenity.title())
        
        hotel_info.room_types = room_types
        hotel_info.room_amenities = amenities
    
    async def _generate_ai_insights(self, soup: BeautifulSoup, hotel_info: IntelligentHotelInfo):
        """Generate AI-powered insights using GPT-oss-20b"""
        if not self.use_ai or not self.text_generator:
            return
        
        # Get clean text content (avoid navigation menus)
        content_text = self._extract_meaningful_content(soup)
        
        try:
            # Use GPT-oss-20b to extract structured hotel information
            prompt = f"""
Extract hotel information from this webpage content and return as structured data:

Content: {content_text[:1500]}

Please extract and return ONLY the following information in this exact format:
HOTEL_NAME: [hotel name]
ADDRESS: [full address]
PHONE: [phone number]
EMAIL: [email address]
CHECK_IN: [check-in time]
CHECK_OUT: [check-out time]
AMENITIES: [list amenities separated by commas]
DINING: [restaurant/dining options]
SPA_SERVICES: [spa services available]
NEARBY: [nearby attractions]
POLICIES: [important policies]
"""

            # Generate response using GPT-oss-20b
            logger.info("Generating AI insights with GPT-oss-20b...")
            response = self.text_generator(prompt, max_length=len(prompt) + 500, num_return_sequences=1)
            
            if response and len(response) > 0:
                generated_text = response[0]['generated_text']
                # Extract the response part (after the prompt)
                ai_response = generated_text[len(prompt):].strip()
                
                # Parse the structured response
                self._parse_ai_response(ai_response, hotel_info)
                
            logger.info("✅ AI insights generated successfully")
            
        except Exception as e:
            logger.error(f"Error generating AI insights: {str(e)}")
            # Fallback to basic extraction
            self._basic_content_extraction(soup, hotel_info)
    
    def _extract_meaningful_content(self, soup: BeautifulSoup) -> str:
        """Extract meaningful content, avoiding navigation menus and headers"""
        # Remove navigation, headers, footers, and script elements
        for element in soup(['nav', 'header', 'footer', 'script', 'style', 'aside']):
            element.decompose()
        
        # Focus on main content areas
        main_content = soup.find('main') or soup.find('div', class_=['content', 'main']) or soup
        
        # Get text from paragraphs, divs with meaningful content
        content_elements = main_content.find_all(['p', 'div', 'section', 'article'], string=True)
        
        meaningful_text = []
        for element in content_elements:
            text = element.get_text(strip=True)
            # Filter out menu items and navigation text
            if len(text) > 20 and not any(nav_word in text.lower() for nav_word in 
                                        ['overview', 'menu', 'click here', 'read more', 'view all']):
                meaningful_text.append(text)
        
        return ' '.join(meaningful_text[:10])  # Limit to first 10 meaningful sentences
    
    def _parse_ai_response(self, ai_response: str, hotel_info: IntelligentHotelInfo):
        """Parse GPT-oss-20b structured response"""
        lines = ai_response.split('\n')
        
        for line in lines:
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                if key == 'HOTEL_NAME' and value != '[hotel name]':
                    hotel_info.hotel_name = value
                elif key == 'ADDRESS' and value != '[full address]':
                    hotel_info.address = value
                elif key == 'PHONE' and value != '[phone number]':
                    hotel_info.phone = value
                elif key == 'EMAIL' and value != '[email address]':
                    hotel_info.email = value
                elif key == 'CHECK_IN' and value != '[check-in time]':
                    hotel_info.checkin_time = value
                elif key == 'CHECK_OUT' and value != '[check-out time]':
                    hotel_info.checkout_time = value
                elif key == 'AMENITIES' and value != '[list amenities separated by commas]':
                    hotel_info.room_amenities = [a.strip() for a in value.split(',')]
                elif key == 'DINING' and value != '[restaurant/dining options]':
                    hotel_info.restaurants = [value]
                elif key == 'SPA_SERVICES' and value != '[spa services available]':
                    hotel_info.spa_services = [a.strip() for a in value.split(',')]
                elif key == 'NEARBY' and value != '[nearby attractions]':
                    hotel_info.nearby_attractions = [a.strip() for a in value.split(',')]
                elif key == 'POLICIES' and value != '[important policies]':
                    if not hotel_info.cancellation_policy:
                        hotel_info.cancellation_policy = value
    
    def _basic_content_extraction(self, soup: BeautifulSoup, hotel_info: IntelligentHotelInfo):
        """Fallback basic extraction if AI fails"""
        logger.info("Using basic content extraction as fallback")
        
        # Extract contact information using simple patterns
        text = soup.get_text()
        
        # Phone number pattern
        import re
        phone_pattern = r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b'
        phone_match = re.search(phone_pattern, text)
        if phone_match and not hotel_info.phone:
            hotel_info.phone = phone_match.group()
        
        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match and not hotel_info.email:
            hotel_info.email = email_match.group()
        
        # Basic amenities extraction
        amenity_keywords = ['pool', 'wifi', 'parking', 'gym', 'spa', 'restaurant', 'bar', 'fitness']
        found_amenities = []
        text_lower = text.lower()
        for amenity in amenity_keywords:
            if amenity in text_lower:
                found_amenities.append(amenity.title())
        
        if found_amenities and not hotel_info.room_amenities:
            hotel_info.room_amenities = found_amenities
    
    def _calculate_confidence_score(self, hotel_info: IntelligentHotelInfo) -> float:
        """Calculate confidence score based on data completeness"""
        # Define weights for different data categories
        field_weights = {
            'hotel_name': 0.1,
            'phone': 0.08,
            'address': 0.08,
            'checkin_time': 0.07,
            'checkout_time': 0.07,
            'parking_available': 0.05,
            'wifi_info': 0.05,
            'restaurants': 0.1,
            'nearby_attractions': 0.08,
            'room_types': 0.08,
            'amenities_count': 0.1,
            'policies_count': 0.08,
            'services_count': 0.06
        }
        
        score = 0.0
        
        # Basic fields
        if hotel_info.hotel_name and hotel_info.hotel_name != "Unknown Hotel":
            score += field_weights['hotel_name']
        if hotel_info.phone:
            score += field_weights['phone']
        if hotel_info.address:
            score += field_weights['address']
        if hotel_info.checkin_time:
            score += field_weights['checkin_time']
        if hotel_info.checkout_time:
            score += field_weights['checkout_time']
        if hotel_info.parking_available is not None:
            score += field_weights['parking_available']
        if hotel_info.wifi_info:
            score += field_weights['wifi_info']
        
        # Complex fields
        if hotel_info.restaurants:
            score += field_weights['restaurants'] * min(len(hotel_info.restaurants) / 3, 1.0)
        if hotel_info.nearby_attractions:
            score += field_weights['nearby_attractions'] * min(len(hotel_info.nearby_attractions) / 5, 1.0)
        if hotel_info.room_types:
            score += field_weights['room_types'] * min(len(hotel_info.room_types) / 3, 1.0)
        
        # Count-based scores
        amenities_count = sum([
            bool(hotel_info.fitness_center),
            bool(hotel_info.pool),
            bool(hotel_info.spa_services),
            bool(hotel_info.business_center),
            bool(hotel_info.pet_policy)
        ])
        score += field_weights['amenities_count'] * min(amenities_count / 5, 1.0)
        
        policies_count = sum([
            bool(hotel_info.cancellation_policy),
            bool(hotel_info.deposit_policy),
            bool(hotel_info.age_restrictions)
        ])
        score += field_weights['policies_count'] * min(policies_count / 3, 1.0)
        
        services_count = len(hotel_info.concierge_services) if hotel_info.concierge_services else 0
        score += field_weights['services_count'] * min(services_count / 5, 1.0)
        
        return min(score, 1.0)  # Cap at 1.0
    
    def close(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()

# Example usage and testing
if __name__ == "__main__":
    async def main():
        scraper = IntelligentHotelScraper(headless=True, use_ai=True)
        
        try:
            # Example hotel URLs for testing
            test_urls = [
                ("https://www.marriott.com", "Marriott Hotels"),
                # Add more URLs for testing
            ]
            
            for url, hotel_name in test_urls:
                try:
                    console.print(f"\n[bold blue]Scraping: {hotel_name}[/bold blue]")
                    hotel_data = await scraper.scrape_hotel_intelligent(url, hotel_name)
                    
                    console.print(f"[green]✅ Successfully scraped {hotel_name}[/green]")
                    console.print(f"[yellow]Confidence Score: {hotel_data.confidence_score:.2f}[/yellow]")
                    
                    # Display key insights
                    if hotel_data.key_selling_points:
                        console.print(f"[cyan]Key Features: {', '.join(hotel_data.key_selling_points)}[/cyan]")
                    
                except Exception as e:
                    console.print(f"[red]❌ Failed to scrape {hotel_name}: {str(e)}[/red]")
        
        finally:
            scraper.close()
    
    # Run the async main function
    asyncio.run(main())
