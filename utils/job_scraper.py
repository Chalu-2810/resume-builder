"""Web scraper for extracting job details from URLs."""
import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional


class JobScraper:
    """Extracts job title and description from a given URL."""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def extract_job_details(self, url: str) -> Optional[Dict]:
        """Attempt to extract job title and description from a URL."""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Generic extraction logic (works for most job boards)
            title = self._find_title(soup)
            description = self._find_description(soup)
            
            if title and description:
                return {"title": title, "description": description}
            else:
                return None
                
        except Exception as e:
            raise ValueError(f"Could not fetch job details: {str(e)}")
    
    def _find_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Heuristic search for job title."""
        # Look for common title tags
        selectors = [
            'h1', 
            'meta[property="og:title"]', 
            '.job-title', 
            '[data-test="job-title"]'
        ]
        
        for selector in selectors:
            if selector.startswith('meta'):
                tag = soup.find('meta', attrs={'property': 'og:title'})
                if tag and tag.get('content'):
                    return tag['content']
            else:
                tag = soup.find(selector)
                if tag and tag.text.strip():
                    return tag.text.strip()
        
        return "Job Title Not Found"
    
    def _find_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Heuristic search for job description."""
        # Look for common description containers
        selectors = [
            '.job-description', 
            '[data-test="job-description"]', 
            '.description', 
            '#job-details',
            'article'
        ]
        
        for selector in selectors:
            tag = soup.find(class_=selector.replace('.', '')) or soup.find(id=selector.replace('#', '')) or soup.find(selector)
            if tag:
                # Clean up the text
                text = tag.get_text(separator='\n', strip=True)
                if len(text) > 100: # Ensure it's substantial
                    return text
        
        # Fallback: get all paragraph text if specific tags aren't found
        paragraphs = soup.find_all('p')
        full_text = '\n'.join([p.get_text(strip=True) for p in paragraphs])
        return full_text if len(full_text) > 100 else None