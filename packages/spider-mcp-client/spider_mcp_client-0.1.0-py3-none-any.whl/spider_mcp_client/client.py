"""
Spider MCP Client - Main client class
"""

import time
import requests
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin

from .exceptions import (
    SpiderMCPError,
    AuthenticationError,
    ParserNotFoundError,
    RateLimitError,
    ServerError,
    TimeoutError,
    ConnectionError,
)


class SpiderMCPClient:
    """
    Official Python client for Spider MCP web scraping API.
    
    Provides easy access to Spider MCP's powerful web scraping capabilities
    with built-in error handling, rate limiting, and retry logic.
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "http://localhost:8003",
        timeout: int = 30,
        max_retries: int = 3,
        rate_limit_delay: float = 1.0
    ):
        """
        Initialize Spider MCP client.
        
        Args:
            api_key: Your Spider MCP API key
            base_url: Base URL of Spider MCP server (default: http://localhost:8003)
            timeout: Request timeout in seconds (default: 30)
            max_retries: Maximum number of retry attempts (default: 3)
            rate_limit_delay: Minimum delay between requests in seconds (default: 1.0)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.rate_limit_delay = rate_limit_delay
        self.last_request_time = None
        
        # Setup session with default headers
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'X-API-Key': self.api_key,
            'User-Agent': f'spider-mcp-client/{self._get_version()}'
        })
    
    def _get_version(self) -> str:
        """Get client version"""
        try:
            from . import __version__
            return __version__
        except ImportError:
            return "unknown"
    
    def _wait_if_needed(self):
        """Ensure minimum delay between requests for rate limiting"""
        if self.last_request_time and self.rate_limit_delay > 0:
            elapsed = time.time() - self.last_request_time
            if elapsed < self.rate_limit_delay:
                time.sleep(self.rate_limit_delay - elapsed)
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make HTTP request with error handling and retries.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            **kwargs: Additional arguments for requests
            
        Returns:
            Response JSON data
            
        Raises:
            Various SpiderMCPError subclasses based on error type
        """
        self._wait_if_needed()
        
        url = urljoin(self.base_url + '/', endpoint.lstrip('/'))
        
        for attempt in range(self.max_retries):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    timeout=self.timeout,
                    **kwargs
                )
                
                self.last_request_time = time.time()
                
                # Handle different status codes
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 401:
                    raise AuthenticationError("Invalid API key")
                elif response.status_code == 404:
                    raise ServerError("Endpoint not found")
                elif response.status_code == 429:
                    raise RateLimitError("Rate limit exceeded")
                elif response.status_code >= 500:
                    raise ServerError(f"Server error: {response.status_code}")
                else:
                    # Try to get error message from response
                    try:
                        error_data = response.json()
                        error_msg = error_data.get('detail', f'HTTP {response.status_code}')
                    except:
                        error_msg = f'HTTP {response.status_code}: {response.text}'
                    raise SpiderMCPError(error_msg)
                    
            except requests.exceptions.Timeout:
                if attempt == self.max_retries - 1:
                    raise TimeoutError(f"Request timed out after {self.timeout} seconds")
                    
            except requests.exceptions.ConnectionError:
                if attempt == self.max_retries - 1:
                    raise ConnectionError(f"Failed to connect to {self.base_url}")
                    
            except (AuthenticationError, ParserNotFoundError, RateLimitError) as e:
                # Don't retry these errors
                raise e
                
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise SpiderMCPError(f"Unexpected error: {str(e)}")
            
            # Wait before retry (exponential backoff)
            if attempt < self.max_retries - 1:
                wait_time = (2 ** attempt) * self.rate_limit_delay
                time.sleep(wait_time)
        
        raise SpiderMCPError("Max retries exceeded")
    
    def parse_url(
        self,
        url: str,
        download_images: bool = False,
        app_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Parse a URL and extract structured data.
        
        Args:
            url: URL to parse
            download_images: Whether to download and localize images (default: False)
            app_name: Session isolation name (optional)
            
        Returns:
            Dictionary containing extracted data
            
        Raises:
            ParserNotFoundError: If no parser exists for the URL
            AuthenticationError: If API key is invalid
            SpiderMCPError: For other errors
        """
        data = {
            'url': url,
            'download_images': download_images
        }
        
        if app_name:
            data['app_name'] = app_name
        
        try:
            result = self._make_request('POST', '/api/parse_url', json=data)
            
            # Check if result contains an error
            if isinstance(result, dict) and result.get('error'):
                if result.get('status') == 'noparser':
                    raise ParserNotFoundError(f"No parser found for URL: {url}")
                else:
                    raise SpiderMCPError(result['error'])
            
            return result
            
        except (AuthenticationError, ParserNotFoundError, RateLimitError, 
                ServerError, TimeoutError, ConnectionError):
            raise
        except Exception as e:
            raise SpiderMCPError(f"Failed to parse URL: {str(e)}")
    
    def check_parser(self, url: str) -> Dict[str, Any]:
        """
        Check if a parser exists for the given URL.
        
        Args:
            url: URL to check
            
        Returns:
            Dictionary with parser information or availability status
        """
        try:
            result = self._make_request('POST', '/parsers/by_url', json={'url': url})
            return result
        except Exception as e:
            raise SpiderMCPError(f"Failed to check parser: {str(e)}")
    
    def get_parsers(self) -> List[Dict[str, Any]]:
        """
        Get list of all available parsers.
        
        Returns:
            List of parser dictionaries
        """
        try:
            result = self._make_request('GET', '/parsers')
            return result.get('parsers', [])
        except Exception as e:
            raise SpiderMCPError(f"Failed to get parsers: {str(e)}")
    
    def close(self):
        """Close the HTTP session"""
        if hasattr(self, 'session'):
            self.session.close()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
