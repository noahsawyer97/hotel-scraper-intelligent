"""
Background worker for processing hotel scraping tasks

This module runs as a separate process to handle intensive scraping tasks
using Celery for task queue management.
"""

import os
import logging
import asyncio
from celery import Celery
from intelligent_scraper import IntelligentHotelScraper

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Celery
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
celery_app = Celery(
    'hotel_scraper_worker',
    broker=redis_url,
    backend=redis_url
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_routes={
        'worker.scrape_single_hotel': {'queue': 'scraping'},
        'worker.scrape_multiple_hotels': {'queue': 'batch_scraping'},
    },
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=10,
)

@celery_app.task(bind=True, name='worker.scrape_single_hotel')
def scrape_single_hotel(self, url: str, hotel_name: str = None):
    """Celery task for scraping a single hotel"""
    scraper = None
    try:
        logger.info(f"Starting scrape task for {url}")
        
        # Update task state
        self.update_state(
            state='PROGRESS',
            meta={'progress': 10, 'message': 'Initializing scraper...'}
        )
        
        scraper = IntelligentHotelScraper(headless=True, use_ai=True)
        
        self.update_state(
            state='PROGRESS',
            meta={'progress': 30, 'message': 'Loading website...'}
        )
        
        # Run the async scraping function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            hotel_data = loop.run_until_complete(
                scraper.scrape_hotel_intelligent(url, hotel_name)
            )
        finally:
            loop.close()
        
        self.update_state(
            state='PROGRESS',
            meta={'progress': 90, 'message': 'Processing results...'}
        )
        
        # Convert to dict for JSON serialization
        from dataclasses import asdict
        result = asdict(hotel_data)
        
        logger.info(f"Successfully scraped {url} with confidence {hotel_data.confidence_score:.2f}")
        
        return {
            'status': 'success',
            'data': result,
            'metadata': {
                'confidence_score': hotel_data.confidence_score,
                'scraped_fields': len([k for k, v in result.items() if v is not None])
            }
        }
        
    except Exception as e:
        logger.error(f"Error scraping {url}: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'url': url
        }
    finally:
        if scraper:
            scraper.close()

@celery_app.task(bind=True, name='worker.scrape_multiple_hotels')
def scrape_multiple_hotels(self, hotels_list):
    """Celery task for scraping multiple hotels"""
    scraper = None
    try:
        logger.info(f"Starting batch scrape for {len(hotels_list)} hotels")
        
        scraper = IntelligentHotelScraper(headless=True, use_ai=True)
        results = []
        
        for i, hotel in enumerate(hotels_list):
            url = hotel['url']
            name = hotel.get('name', 'Unknown Hotel')
            
            # Update progress
            progress = int((i / len(hotels_list)) * 100)
            self.update_state(
                state='PROGRESS',
                meta={
                    'progress': progress,
                    'message': f'Scraping {name} ({i+1}/{len(hotels_list)})'
                }
            )
            
            try:
                # Run the async scraping function
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    hotel_data = loop.run_until_complete(
                        scraper.scrape_hotel_intelligent(url, name)
                    )
                finally:
                    loop.close()
                
                from dataclasses import asdict
                results.append({
                    'url': url,
                    'status': 'success',
                    'data': asdict(hotel_data),
                    'confidence_score': hotel_data.confidence_score
                })
                
                logger.info(f"Successfully scraped {name}")
                
            except Exception as e:
                logger.error(f"Failed to scrape {name}: {str(e)}")
                results.append({
                    'url': url,
                    'status': 'error',
                    'error': str(e)
                })
            
            # Rate limiting between requests
            if i < len(hotels_list) - 1:
                asyncio.sleep(3)
        
        successful = len([r for r in results if r['status'] == 'success'])
        failed = len([r for r in results if r['status'] == 'error'])
        
        logger.info(f"Batch scraping completed: {successful} successful, {failed} failed")
        
        return {
            'status': 'completed',
            'results': results,
            'summary': {
                'total': len(hotels_list),
                'successful': successful,
                'failed': failed
            }
        }
        
    except Exception as e:
        logger.error(f"Batch scraping error: {str(e)}")
        return {
            'status': 'error',
            'error': str(e)
        }
    finally:
        if scraper:
            scraper.close()

if __name__ == '__main__':
    # Start the Celery worker
    celery_app.start()
