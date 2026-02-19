import asyncio
import httpx
from typing import Dict
from app.services.artic_place_fetcher.models.models import ArticResponse
from app.core.logger.logger import AppLogger
from app.services.artic_place_fetcher.errors.errors import *
import random

class ArticPlaceFetcher:
    _instance = None
    _logger = AppLogger("ARTICFETCHER", "artic_fetcher.log")

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._logger.logger.info("Creating Singleton instance of ArticPlaceFetcher")
            cls._instance = super(ArticPlaceFetcher, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    #TODO get url from config
    def __init__(self, base_url: str = "https://api.artic.edu/api/v1/places"):
        if self._initialized:
            return
        
        self._logger.logger.info(f"Initialized artic fetcher with url : {base_url}")
        self.base_url = base_url
        self._places: Dict[int, str] = {}

        self._initialized = True

    def get_random_place_name(self) -> str:
        """For debug purposes: returns a random place name from the cache."""
        if not self._places:
            return "No places cached yet"

        # random.choice works on sequences (lists/tuples)
        # so we convert the dictionary values into a list first
        return random.choice(list(self._places.values()))
    
    async def fetch_all_places(self, limit: int = 100) -> Dict[int, str]:
        """Public method to orchestrate the full fetch."""
        self._logger.logger.info(f"Trying to fetch all places")
        async with httpx.AsyncClient() as client:
            # 1. Fetch the first page to get total_pages info
            first_page_url = f"{self.base_url}?limit={limit}&page=1"
            first_data = await self._fetch_single_page(client, first_page_url)
            
            if not first_data:
                self._logger.logger.error(f"Can't fetch first page, url = {first_page_url}")
                return {}

            total_pages = first_data.pagination.total_pages
            self._logger.logger.info(f"Fetched first page successfully")
            
            # 2. Create tasks for all remaining pages
            tasks = []
            for page in range(2, total_pages + 1):
                url = f"{self.base_url}?limit={limit}&page={page}"
                self._logger.logger.info(f"Fetching page {page}")
                tasks.append(self._fetch_single_page(client, url))
            
            # 3. Wait for all pages to finish concurrently
            results = await asyncio.gather(*tasks)
            self._logger.logger.info(f"All pages fetched!")

            
            # 4. Merge results (skipping None if a page failed)
            for page_data in [first_data] + list(results):
                if page_data:
                    self._places.update({p.id: p.title for p in page_data.data})
                else:
                    self._logger.logger.warning(f"Page data is empty!")
                    
        return self._places

    async def _fetch_single_page(self, client: httpx.AsyncClient, url: str) -> ArticResponse | None:
        """Private helper to fetch and parse a single page."""
        try:
            response = await client.get(url, timeout=60.0)
            response.raise_for_status()
            return ArticResponse(**response.json())
        except Exception as e:
            self._logger.logger.error(f"Error fetching {url}: {e}")
            return None

    def get_place_id(self, name: str) -> int | None:
        """
        Returns the first ID found matching the given name.
        Returns None if no match is found.
        """
        for p_id, p_name in self._places.items(): 
            if p_name == name:
                return p_id

        return None
        #raise PlaceNotFoundError(name)
        