"""
Web Search Service for MSA Reasoning Engine
Provides ground knowledge through Google Search and web content extraction
"""

from typing import Any, Dict, List, Optional


try:
    from googlesearch import search
    import trafilatura
    SEARCH_AVAILABLE = True
except ImportError:
    SEARCH_AVAILABLE = False
    
import httpx


logger = logging.getLogger(__name__)

class WebSearchService:
    """Service for searching web content and extracting ground knowledge"""
    
    def __init__(self):
        self.max_search_results = 5
        self.max_content_length = 2000
        
    async def search_ground_knowledge(self, scenario: str, search_terms: List[str]) -> Dict[str, Any]:
        """
        Search for ground knowledge related to a scenario
        
        Args:
            scenario: The scenario being analyzed
            search_terms: List of terms to search for
            
        Returns:
            Dictionary containing search results and extracted content
        """
        if not SEARCH_AVAILABLE:
            logger.warning("Web search not available - missing dependencies")
            return {
                "search_performed": False,
                "reason": "Web search dependencies not installed",
                "ground_knowledge": []
            }
        
        try:
            logger.info(f"Searching for ground knowledge: {search_terms}")
            
            # Perform searches for each term
            all_results = []
            for term in search_terms[:3]:  # Limit to 3 terms to avoid rate limiting
                try:
                    search_query = f"{term} research analysis facts"
                    urls = list(search(search_query, num_results=3, lang='en'))
                    
                    for url in urls:
                        content = await self._extract_web_content(url)
                        if content:
                            all_results.append({
                                "search_term": term,
                                "url": url,
                                "content": content,
                                "relevance": "high" if term.lower() in content.lower() else "medium"
                            })
                            
                except Exception as e:
                    sanitized_term = sanitize_for_log(term)
                    logger.warning(f"Search failed for term '{sanitized_term}': {e}")
                    continue
            
            # Filter and rank results
            filtered_results = self._filter_and_rank_results(all_results, scenario)
            
            return {
                "search_performed": True,
                "scenario": scenario,
                "search_terms": search_terms,
                "total_results_found": len(all_results),
                "filtered_results": len(filtered_results),
                "ground_knowledge": filtered_results
            }
            
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return {
                "search_performed": False,
                "error": str(e),
                "ground_knowledge": []
            }
    
    async def _extract_web_content(self, url: str) -> Optional[str]:
        """Extract clean text content from a web page"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                # Extract main content using trafilatura
                if SEARCH_AVAILABLE:
                    text = trafilatura.extract(response.text)
                    if text and len(text) > 100:  # Minimum content length
                        # Truncate to max length
                        return text[:self.max_content_length] + ("..." if len(text) > self.max_content_length else "")
                
                return None
                
        except Exception as e:
            sanitized_url = url.replace('\r', '').replace('\n', '')
            logger.debug(f"Failed to extract content from {sanitized_url}: {e}")
            return None
    
    def _filter_and_rank_results(self, results: List[Dict[str, Any]], scenario: str) -> List[Dict[str, Any]]:
        """Filter and rank search results by relevance to scenario"""
        # Simple ranking based on content relevance
        scenario_words = set(scenario.lower().split())
        
        for result in results:
            content_words = set(result["content"].lower().split())
            overlap = len(scenario_words.intersection(content_words))
            result["relevance_score"] = overlap / len(scenario_words) if scenario_words else 0
        
        # Sort by relevance score and return top results
        sorted_results = sorted(results, key=lambda x: x["relevance_score"], reverse=True)
        return sorted_results[:self.max_search_results]
    
    def generate_search_terms(self, scenario: str) -> List[str]:
        """Generate search terms from scenario for ground knowledge gathering"""
        # Extract key terms from scenario
        # This is a simple implementation - could be enhanced with NLP
        words = scenario.lower().split()
        
        # Filter out common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could'}
        
        meaningful_words = [word for word in words if word not in stop_words and len(word) > 3]
        
        # Take top 5 meaningful words as search terms
        return meaningful_words[:5]