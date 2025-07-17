"""
Advanced web scraping module for agricultural data
Includes scrapers for disease information, supplier data, and price information
with robust error handling, rate limiting, and caching
"""
import asyncio
import aiohttp
import requests
from bs4 import BeautifulSoup
import logging
import time
import random
from typing import List, Dict, Any, Optional, Union
from urllib.parse import urljoin, urlparse
import json
from datetime import datetime, timedelta

from config.settings import settings
from config.logging import get_logger
from services.cache import get_cache, set_cache

logger = get_logger("scraper")


class RateLimiter:
    """Rate limiter to control scraping frequency"""

    def __init__(self, delay: float = 1.0):
        self.delay = delay
        self.last_request = 0

    async def wait(self):
        """Wait if necessary to respect rate limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request

        if time_since_last < self.delay:
            wait_time = self.delay - time_since_last
            await asyncio.sleep(wait_time)

        self.last_request = time.time()


class WebScraper:
    """Advanced web scraper with error handling and rate limiting"""

    def __init__(self):
        self.rate_limiter = RateLimiter(settings.scraping_delay)
        self.session: Optional[aiohttp.ClientSession] = None
        self.headers = {
            "User-Agent": settings.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=settings.scraping_timeout),
            headers=self.headers
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def fetch_page(self, url: str, retries: int = None) -> Optional[str]:
        """Fetch a web page with retries and error handling"""
        retries = retries or settings.scraping_retries

        for attempt in range(retries + 1):
            try:
                await self.rate_limiter.wait()

                async with self.session.get(url) as response:
                    if response.status == 200:
                        content = await response.text()
                        logger.debug(f"Successfully fetched: {url}")
                        return content
                    elif response.status == 429:  # Rate limited
                        wait_time = 2 ** attempt  # Exponential backoff
                        logger.warning(f"Rate limited, waiting {wait_time}s before retry")
                        await asyncio.sleep(wait_time)
                    else:
                        logger.warning(f"HTTP {response.status} for {url}")

            except asyncio.TimeoutError:
                logger.warning(f"Timeout fetching {url} (attempt {attempt + 1})")
            except Exception as e:
                logger.error(f"Error fetching {url}: {e} (attempt {attempt + 1})")

            if attempt < retries:
                # Wait before retry with jitter
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                await asyncio.sleep(wait_time)

        logger.error(f"Failed to fetch {url} after {retries + 1} attempts")
        return None

    def parse_html(self, html: str) -> BeautifulSoup:
        """Parse HTML content"""
        return BeautifulSoup(html, 'html.parser')


class AgriculturalDataScraper:
    """Specialized scraper for agricultural data sources"""

    def __init__(self):
        self.scraper = WebScraper()

    async def scrape_disease_info(self, disease_name: str, crop_type: str) -> Dict[str, Any]:
        """Scrape disease information from agricultural websites"""
        cache_key = f"scraped_disease:{disease_name}:{crop_type}"

        # Check cache first
        cached_data = await get_cache(cache_key)
        if cached_data:
            return cached_data

        disease_data = {
            "symptoms": [],
            "treatments": [],
            "prevention": [],
            "sources": []
        }

        # List of agricultural information sources
        sources = [
            {
                "name": "CABI Crop Protection Compendium",
                "url": f"https://www.cabi.org/cpc/search/?q={disease_name}+{crop_type}",
                "parser": self._parse_cabi_data
            },
            {
                "name": "Ghana Ministry of Food and Agriculture",
                "url": f"https://mofa.gov.gh/site/agriculture/crop-diseases",
                "parser": self._parse_mofa_data
            },
            {
                "name": "FAO Plant Health",
                "url": f"http://www.fao.org/plant-health/en/",
                "parser": self._parse_fao_data
            }
        ]

        async with self.scraper:
            for source in sources:
                try:
                    html = await self.scraper.fetch_page(source["url"])
                    if html:
                        parsed_data = await source["parser"](html, disease_name, crop_type)
                        if parsed_data:
                            disease_data["symptoms"].extend(parsed_data.get("symptoms", []))
                            disease_data["treatments"].extend(parsed_data.get("treatments", []))
                            disease_data["prevention"].extend(parsed_data.get("prevention", []))
                            disease_data["sources"].append(source["name"])

                except Exception as e:
                    logger.error(f"Error scraping {source['name']}: {e}")

        # Remove duplicates
        disease_data["symptoms"] = list(set(disease_data["symptoms"]))
        disease_data["treatments"] = list(set(disease_data["treatments"]))
        disease_data["prevention"] = list(set(disease_data["prevention"]))

        # Cache the result
        await set_cache(cache_key, disease_data, ttl=settings.cache_ttl_disease_info)

        logger.info(f"Scraped disease info for {disease_name} from {len(disease_data['sources'])} sources")
        return disease_data

    async def scrape_supplier_data(self, location: str, product_type: str) -> List[Dict[str, Any]]:
        """Scrape supplier information from various sources"""
        cache_key = f"scraped_suppliers:{location}:{product_type}"

        # Check cache first
        cached_data = await get_cache(cache_key)
        if cached_data:
            return cached_data

        suppliers = []

        # Ghana-specific agricultural supplier sources
        sources = [
            {
                "name": "Ghana Agricultural Directory",
                "url": f"https://ghana.agridirectory.com/search?location={location}&category={product_type}",
                "parser": self._parse_agri_directory
            },
            {
                "name": "Ghana Business Directory",
                "url": f"https://www.ghanabusinessdirectory.com/agriculture",
                "parser": self._parse_business_directory
            }
        ]

        async with self.scraper:
            for source in sources:
                try:
                    html = await self.scraper.fetch_page(source["url"])
                    if html:
                        parsed_suppliers = await source["parser"](html, location, product_type)
                        suppliers.extend(parsed_suppliers)

                except Exception as e:
                    logger.error(f"Error scraping suppliers from {source['name']}: {e}")

        # Remove duplicates based on name and location
        unique_suppliers = []
        seen = set()
        for supplier in suppliers:
            key = (supplier.get("name", ""), supplier.get("location", ""))
            if key not in seen:
                seen.add(key)
                unique_suppliers.append(supplier)

        # Cache the result
        await set_cache(cache_key, unique_suppliers, ttl=settings.cache_ttl_suppliers)

        logger.info(f"Scraped {len(unique_suppliers)} suppliers for {location}")
        return unique_suppliers

    async def scrape_price_data(self, product_name: str, location: str) -> List[Dict[str, Any]]:
        """Scrape price information from agricultural marketplaces"""
        cache_key = f"scraped_prices:{product_name}:{location}"

        # Check cache first
        cached_data = await get_cache(cache_key)
        if cached_data:
            return cached_data

        prices = []

        # Price sources (would be real agricultural marketplaces)
        sources = [
            {
                "name": "Ghana Agricultural Market Prices",
                "url": f"https://ghana.agrimarket.com/prices?product={product_name}&location={location}",
                "parser": self._parse_market_prices
            },
            {
                "name": "West Africa Agricultural Prices",
                "url": f"https://westafrica.agriprices.com/search?q={product_name}",
                "parser": self._parse_regional_prices
            }
        ]

        async with self.scraper:
            for source in sources:
                try:
                    html = await self.scraper.fetch_page(source["url"])
                    if html:
                        parsed_prices = await source["parser"](html, product_name, location)
                        prices.extend(parsed_prices)

                except Exception as e:
                    logger.error(f"Error scraping prices from {source['name']}: {e}")

        # Cache the result
        await set_cache(cache_key, prices, ttl=settings.cache_ttl_prices)

        logger.info(f"Scraped {len(prices)} price entries for {product_name}")
        return prices

    # Parser methods (these would contain actual parsing logic for each source)
    async def _parse_cabi_data(self, html: str, disease_name: str, crop_type: str) -> Dict[str, Any]:
        """Parse CABI Crop Protection Compendium data"""
        # This would contain actual parsing logic for CABI website
        # For now, return mock data
        return {
            "symptoms": [f"CABI symptom 1 for {disease_name}", f"CABI symptom 2 for {disease_name}"],
            "treatments": [f"CABI treatment 1 for {disease_name}"],
            "prevention": [f"CABI prevention method for {disease_name}"]
        }

    async def _parse_mofa_data(self, html: str, disease_name: str, crop_type: str) -> Dict[str, Any]:
        """Parse Ghana MOFA data"""
        # Mock implementation
        return {
            "symptoms": [f"MOFA symptom for {disease_name}"],
            "treatments": [f"MOFA recommended treatment for {disease_name}"],
            "prevention": [f"MOFA prevention advice for {disease_name}"]
        }

    async def _parse_fao_data(self, html: str, disease_name: str, crop_type: str) -> Dict[str, Any]:
        """Parse FAO Plant Health data"""
        # Mock implementation
        return {
            "symptoms": [f"FAO symptom description for {disease_name}"],
            "treatments": [f"FAO treatment recommendation for {disease_name}"],
            "prevention": [f"FAO prevention strategy for {disease_name}"]
        }

    async def _parse_agri_directory(self, html: str, location: str, product_type: str) -> List[Dict[str, Any]]:
        """Parse agricultural directory data"""
        # Mock implementation
        return [
            {
                "name": f"Agricultural Supplier 1 - {location}",
                "address": f"123 Farm Street, {location}",
                "phone": "+233-XXX-XXX-XXX",
                "products": [product_type, "fertilizers", "seeds"],
                "verified": False
            }
        ]

    async def _parse_business_directory(self, html: str, location: str, product_type: str) -> List[Dict[str, Any]]:
        """Parse business directory data"""
        # Mock implementation
        return [
            {
                "name": f"Business Directory Supplier - {location}",
                "address": f"456 Business Ave, {location}",
                "phone": "+233-YYY-YYY-YYY",
                "products": [product_type],
                "verified": True
            }
        ]

    async def _parse_market_prices(self, html: str, product_name: str, location: str) -> List[Dict[str, Any]]:
        """Parse market price data"""
        # Mock implementation
        return [
            {
                "product": product_name,
                "price_ghs": 45.50,
                "quantity": "1kg",
                "supplier": f"Market Supplier - {location}",
                "date": datetime.now().isoformat(),
                "location": location
            }
        ]

    async def _parse_regional_prices(self, html: str, product_name: str, location: str) -> List[Dict[str, Any]]:
        """Parse regional price data"""
        # Mock implementation
        return [
            {
                "product": product_name,
                "price_ghs": 42.00,
                "quantity": "1kg",
                "supplier": f"Regional Supplier",
                "date": datetime.now().isoformat(),
                "location": "West Africa"
            }
        ]


# Global scraper instance
agricultural_scraper = AgriculturalDataScraper()


# Legacy function for backward compatibility
def scrape_products(query: str) -> List[str]:
    """Legacy function for backward compatibility"""
    try:
        # Use async scraper in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Mock implementation for now
        products = [
            f"Product 1 for {query}",
            f"Product 2 for {query}",
            f"Product 3 for {query}"
        ]

        loop.close()
        return products

    except Exception as e:
        logger.error(f"Error in legacy scrape_products: {e}")
        return [f"Mock Product 1 for {query}", f"Mock Product 2 for {query}"]


# Async functions for new code
async def scrape_disease_information(disease_name: str, crop_type: str) -> Dict[str, Any]:
    """Scrape comprehensive disease information"""
    return await agricultural_scraper.scrape_disease_info(disease_name, crop_type)


async def scrape_supplier_information(location: str, product_type: str) -> List[Dict[str, Any]]:
    """Scrape supplier information"""
    return await agricultural_scraper.scrape_supplier_data(location, product_type)


async def scrape_price_information(product_name: str, location: str) -> List[Dict[str, Any]]:
    """Scrape price information"""
    return await agricultural_scraper.scrape_price_data(product_name, location)
