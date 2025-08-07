from duckduckgo_search import DDGS
from typing import List, Dict, Optional
import logging
from datetime import datetime, timedelta
import json
import hashlib
from pathlib import Path

class WebSearcher:
    def __init__(self, cache_dir: str = ".cache/websearch"):
        """Initializes the WebSearcher with a persistent file-based cache."""
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_expiry = timedelta(hours=1)
        self.trusted_domains = [
            ".gov", ".edu", ".org",
            "sba.gov", "irs.gov", "dol.gov", "wikipedia.org"
        ]
        
    def search(
        self, 
        query: str, 
        max_results: int = 3,
        use_cache: bool = True
    ) -> List[Dict]:
        """
        Performs a web search with domain filtering and persistent caching.
        
        Args:
            query: The search query.
            max_results: Maximum number of results to return.
            use_cache: Whether to use cached results.
            
        Returns:
            A list of search result dictionaries.
        """
        query_hash = hashlib.sha256(query.lower().encode()).hexdigest()
        cache_file = self.cache_dir / f"{query_hash}.json"
        
        # Check cache first
        if use_cache and cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                
                # Check if the cache is still valid
                cached_time = datetime.fromisoformat(cached_data["time"])
                if datetime.now() - cached_time < self.cache_expiry:
                    logging.info(f"Web search cache HIT for query: {query}")
                    return cached_data["results"]
            except Exception as e:
                logging.warning(f"Could not read web search cache file {cache_file}. Error: {e}")

        # If not in cache or expired, perform the search
        logging.info(f"Web search cache MISS for query: {query}. Searching online.")
        try:
            with DDGS() as ddgs:
                # Fetch more results than needed to allow for filtering
                search_results = list(ddgs.text(query, max_results=max_results * 3))
            
            # Filter for trusted domains
            filtered_results = []
            for result in search_results:
                if any(domain in result["href"] for domain in self.trusted_domains):
                    filtered_results.append({
                        "title": result["title"],
                        "url": result["href"],
                        "snippet": result["body"],
                        "timestamp": datetime.now().isoformat()
                    })
                if len(filtered_results) >= max_results:
                    break
            
            # Update cache
            cache_data = {
                "results": filtered_results,
                "time": datetime.now().isoformat()
            }
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
                
            return filtered_results
            
        except Exception as e:
            logging.error(f"Web search failed for query '{query}': {str(e)}")
            return []

    def clear_cache(self) -> None:
        """Clears the entire web search cache by deleting all cache files."""
        logging.info("Clearing web search cache...")
        for item in self.cache_dir.iterdir():
            if item.is_file():
                try:
                    item.unlink()
                except Exception as e:
                    logging.error(f"Failed to delete cache file {item}: {e}")
        logging.info("Web search cache cleared.")
