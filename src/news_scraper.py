import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsHeadline:
    """Represents a news headline with source information"""
    def __init__(self, title: str, source: str, url: str = None):
        self.title = title
        self.source = source
        self.url = url
    
    def __str__(self):
        return f"[{self.source}] {self.title}"


class BusinessNewsScraper:
    """Scrapes business news from multiple sources using RSS feeds"""
    
    # User agent to avoid being blocked
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # RSS Feed URLs for reliable news sources
    RSS_FEEDS = {
        'Yahoo Finance': [
            'https://finance.yahoo.com/news/rssindex',
        ],
        'New York Times': [
            'https://feeds.nytimes.com/services/xml/rss/nyt/Business.xml',
            'https://rss.nytimes.com/services/xml/rss/nyt/Economy.xml',
        ],
        'CNBC': [
            'https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10001147', 
            'https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000664',
        ],
        'Forbes': [
            'https://www.forbes.com/business/feed2/',
        ],
    }
    
    # Timeout for requests
    TIMEOUT = 10
    
    @staticmethod
    def parse_rss_feed(feed_url: str, source: str) -> List[NewsHeadline]:
        """Parse an RSS feed and extract headlines"""
        try:
            response = requests.get(feed_url, headers=BusinessNewsScraper.HEADERS, timeout=BusinessNewsScraper.TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html5lib')
            headlines = []
            
            # Parse RSS items
            items = soup.find_all('item', limit=5)
            logger.info(f"[{source}] Found {len(items)} items in feed")
            
            for item in items:
                # Try different title tags
                title_tag = item.find('title')
                if title_tag:
                    text = title_tag.get_text(strip=True)
                    
                    # Extract URL from link tag
                    link_tag = item.find('link')
                    url = link_tag.get_text(strip=True) if link_tag else None
                    
                    if text and len(text) > 10:
                        headlines.append(NewsHeadline(text, source, url))
            
            logger.info(f"[{source}] Extracted {len(headlines)} headlines")
            return headlines
        except Exception as e:
            logger.warning(f"Error scraping {source} RSS feed ({feed_url}): {e}")
            return []
    
    @staticmethod
    def scrape_yahoo_finance() -> List[NewsHeadline]:
        """Scrape headlines from Yahoo Finance RSS feed"""
        headlines = []
        for feed_url in BusinessNewsScraper.RSS_FEEDS['Yahoo Finance']:
            headlines.extend(BusinessNewsScraper.parse_rss_feed(feed_url, 'Yahoo Finance'))
        return headlines
    
    @staticmethod
    def scrape_nytimes() -> List[NewsHeadline]:
        """Scrape headlines from New York Times Business RSS feed"""
        headlines = []
        for feed_url in BusinessNewsScraper.RSS_FEEDS['New York Times']:
            headlines.extend(BusinessNewsScraper.parse_rss_feed(feed_url, 'New York Times'))
        return headlines
    
    @staticmethod
    def scrape_cnbc() -> List[NewsHeadline]:
        """Scrape headlines from CNBC RSS feed"""
        headlines = []
        for feed_url in BusinessNewsScraper.RSS_FEEDS['CNBC']:
            headlines.extend(BusinessNewsScraper.parse_rss_feed(feed_url, 'CNBC'))
        return headlines
    
    @staticmethod
    def scrape_forbes() -> List[NewsHeadline]:
        """Scrape headlines from Forbes RSS feed"""
        headlines = []
        for feed_url in BusinessNewsScraper.RSS_FEEDS['Forbes']:
            headlines.extend(BusinessNewsScraper.parse_rss_feed(feed_url, 'Forbes'))
        return headlines
    
    @staticmethod
    async def fetch_all_news() -> List[NewsHeadline]:
        """Fetch news from all sources concurrently"""
        loop = asyncio.get_event_loop()
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            tasks = [
                loop.run_in_executor(executor, BusinessNewsScraper.scrape_yahoo_finance),
                loop.run_in_executor(executor, BusinessNewsScraper.scrape_nytimes),
                loop.run_in_executor(executor, BusinessNewsScraper.scrape_cnbc),
                loop.run_in_executor(executor, BusinessNewsScraper.scrape_forbes),
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine all results
        all_headlines = []
        for result in results:
            if isinstance(result, list):
                all_headlines.extend(result)
            elif isinstance(result, Exception):
                logger.warning(f"Task failed: {result}")
        
        return all_headlines
    
    @staticmethod
    def get_headlines_text(headlines: List[NewsHeadline]) -> str:
        """Convert headlines list to formatted text for OpenAI"""
        if not headlines:
            return "No headlines found."
        
        text = "Business News Headlines:\n\n"
        for headline in headlines:
            if headline.url:
                text += f"- [{headline.source}] {headline.title}\n  Link: {headline.url}\n"
            else:
                text += f"- [{headline.source}] {headline.title}\n"
        
        return text
    
    @staticmethod
    def balance_headlines_by_source(headlines: List[NewsHeadline], total_headlines: int = 12) -> List[NewsHeadline]:
        """Balance headlines evenly across all sources"""
        if not headlines:
            return []
        
        # Group headlines by source
        source_groups = {}
        for headline in headlines:
            if headline.source not in source_groups:
                source_groups[headline.source] = []
            source_groups[headline.source].append(headline)
        
        # Calculate how many headlines per source
        num_sources = len(source_groups)
        headlines_per_source = max(1, total_headlines // num_sources)
        
        # Distribute headlines evenly across sources
        balanced = []
        for source in source_groups:
            balanced.extend(source_groups[source][:headlines_per_source])
        
        # If we still have room, add any remaining headlines
        if len(balanced) < total_headlines:
            for source in source_groups:
                for headline in source_groups[source][headlines_per_source:]:
                    if len(balanced) < total_headlines:
                        balanced.append(headline)
        
        return balanced[:total_headlines]
