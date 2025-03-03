#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Base Client Module.

This module provides the BaseClient abstract class that defines the common interface
for all external service clients used by the Project Architect. It establishes
the contract that specific client implementations like AnthropicClient and GithubClient
must fulfill, ensuring consistent behavior across different external services.
"""

import abc
import logging
import time
from typing import Any, Dict, Optional, Union, List, Callable
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError

from src.utils.logger import setup_logger


class BaseClient(abc.ABC):
    """
    Abstract base class for all external service clients.
    
    This class defines the common interface and shared functionality for clients
    that communicate with external services like Anthropic's Claude API or GitHub API.
    It provides common utilities like rate limiting, retries, and error handling.
    
    Attributes:
        config: Configuration object containing API keys and settings
        logger: Logger instance for the client
        retry_count: Maximum number of retry attempts for failed requests
        retry_delay: Delay between retry attempts in seconds
        timeout: Timeout for requests in seconds
    """
    
    def __init__(self, config: Any):
        """
        Initialize the base client with configuration.
        
        Args:
            config: Configuration object containing API keys and settings
        """
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        setup_logger()
        
        # Default retry settings
        self.retry_count = getattr(config, 'retry_count', 3)
        self.retry_delay = getattr(config, 'retry_delay', 1)
        self.timeout = getattr(config, 'request_timeout', 30)
        
        # Rate limiting settings
        self.rate_limit_enabled = getattr(config, 'rate_limit_enabled', True)
        self.rate_limit_calls = getattr(config, 'rate_limit_calls', 10)
        self.rate_limit_period = getattr(config, 'rate_limit_period', 60)
        self._call_timestamps: List[float] = []
        
        self.logger.debug(f"Initialized {self.__class__.__name__} with config: {config}")
    
    @abc.abstractmethod
    def validate_config(self) -> bool:
        """
        Validate that the configuration has all required fields for this client.
        
        Returns:
            bool: True if configuration is valid, False otherwise
        """
        pass
    
    @abc.abstractmethod
    def test_connection(self) -> bool:
        """
        Test the connection to the external service.
        
        Returns:
            bool: True if connection is successful, False otherwise
        """
        pass
    
    def _handle_rate_limiting(self) -> None:
        """
        Handle rate limiting by tracking API calls and delaying if necessary.
        
        This method implements a sliding window rate limiting algorithm to ensure
        the client doesn't exceed the configured rate limits for the external API.
        """
        if not self.rate_limit_enabled:
            return
        
        current_time = time.time()
        
        # Remove timestamps older than the rate limit period
        self._call_timestamps = [ts for ts in self._call_timestamps 
                                if current_time - ts < self.rate_limit_period]
        
        # If we've reached the rate limit, sleep until we can make another call
        if len(self._call_timestamps) >= self.rate_limit_calls:
            oldest_timestamp = min(self._call_timestamps)
            sleep_time = self.rate_limit_period - (current_time - oldest_timestamp)
            
            if sleep_time > 0:
                self.logger.debug(f"Rate limit reached. Sleeping for {sleep_time:.2f} seconds")
                time.sleep(sleep_time)
        
        # Add current timestamp to the list
        self._call_timestamps.append(time.time())
    
    def _make_request_with_retry(self, request_func: Callable, *args: Any, **kwargs: Any) -> Any:
        """
        Make an HTTP request with automatic retries on failure.
        
        Args:
            request_func: Function to call for making the request
            *args: Positional arguments to pass to the request function
            **kwargs: Keyword arguments to pass to the request function
            
        Returns:
            The response from the request function
            
        Raises:
            Exception: If all retry attempts fail
        """
        self._handle_rate_limiting()
        
        # Set default timeout if not provided
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
        
        last_exception = None
        
        for attempt in range(self.retry_count + 1):
            try:
                if attempt > 0:
                    self.logger.warning(f"Retry attempt {attempt}/{self.retry_count}")
                    # Exponential backoff
                    sleep_time = self.retry_delay * (2 ** (attempt - 1))
                    time.sleep(sleep_time)
                
                return request_func(*args, **kwargs)
                
            except (RequestException, Timeout, ConnectionError) as e:
                self.logger.warning(f"Request failed: {str(e)}")
                last_exception = e
                
                # Don't retry on certain status codes
                if isinstance(e, RequestException) and hasattr(e, 'response'):
                    status_code = e.response.status_code
                    if status_code in [400, 401, 403, 404]:
                        self.logger.error(f"Request failed with status {status_code}, not retrying")
                        raise
        
        # If we get here, all retries failed
        self.logger.error(f"All {self.retry_count} retry attempts failed")
        if last_exception:
            raise last_exception
        else:
            raise Exception("Request failed for unknown reason")
    
    def get(self, url: str, headers: Optional[Dict[str, str]] = None, 
            params: Optional[Dict[str, Any]] = None, **kwargs: Any) -> requests.Response:
        """
        Make a GET request with retries and rate limiting.
        
        Args:
            url: URL to request
            headers: Optional headers to include in the request
            params: Optional query parameters
            **kwargs: Additional arguments to pass to requests.get
            
        Returns:
            Response object from the requests library
        """
        self.logger.debug(f"Making GET request to {url}")
        return self._make_request_with_retry(
            requests.get, url, headers=headers, params=params, **kwargs
        )
    
    def post(self, url: str, headers: Optional[Dict[str, str]] = None, 
             data: Optional[Any] = None, json: Optional[Dict[str, Any]] = None, 
             **kwargs: Any) -> requests.Response:
        """
        Make a POST request with retries and rate limiting.
        
        Args:
            url: URL to request
            headers: Optional headers to include in the request
            data: Optional data to send in the request body
            json: Optional JSON data to send in the request body
            **kwargs: Additional arguments to pass to requests.post
            
        Returns:
            Response object from the requests library
        """
        self.logger.debug(f"Making POST request to {url}")
        return self._make_request_with_retry(
            requests.post, url, headers=headers, data=data, json=json, **kwargs
        )
    
    def put(self, url: str, headers: Optional[Dict[str, str]] = None, 
            data: Optional[Any] = None, **kwargs: Any) -> requests.Response:
        """
        Make a PUT request with retries and rate limiting.
        
        Args:
            url: URL to request
            headers: Optional headers to include in the request
            data: Optional data to send in the request body
            **kwargs: Additional arguments to pass to requests.put
            
        Returns:
            Response object from the requests library
        """
        self.logger.debug(f"Making PUT request to {url}")
        return self._make_request_with_retry(
            requests.put, url, headers=headers, data=data, **kwargs
        )
    
    def delete(self, url: str, headers: Optional[Dict[str, str]] = None, 
               **kwargs: Any) -> requests.Response:
        """
        Make a DELETE request with retries and rate limiting.
        
        Args:
            url: URL to request
            headers: Optional headers to include in the request
            **kwargs: Additional arguments to pass to requests.delete
            
        Returns:
            Response object from the requests library
        """
        self.logger.debug(f"Making DELETE request to {url}")
        return self._make_request_with_retry(
            requests.delete, url, headers=headers, **kwargs
        )
    
    def handle_error_response(self, response: requests.Response) -> None:
        """
        Handle error responses from the API.
        
        Args:
            response: Response object from the requests library
            
        Raises:
            Exception: With details about the error
        """
        status_code = response.status_code
        error_msg = f"API error: {status_code}"
        
        try:
            error_data = response.json()
            if isinstance(error_data, dict):
                error_msg = f"API error {status_code}: {error_data.get('error', '')}"
                if 'message' in error_data:
                    error_msg += f" - {error_data['message']}"
        except (ValueError, KeyError):
            # If response is not JSON or doesn't have expected fields
            error_msg = f"API error {status_code}: {response.text[:100]}"
        
        self.logger.error(error_msg)
        raise Exception(error_msg)
    
    def close(self) -> None:
        """
        Close the client and release any resources.
        
        This method should be called when the client is no longer needed.
        """
        self.logger.debug(f"Closing {self.__class__.__name__}")
        # Base implementation doesn't need to do anything,
        # but subclasses might need to close connections