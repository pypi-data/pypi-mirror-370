"""
HTTP communication management for OpenRouter Client.

This module handles HTTP requests, response handling, rate limiting, and
error handling for all API interactions.

Exported:
- HTTPManager: HTTP request and response manager with rate limiting
"""

import logging
import time
from typing import Dict, Optional, Any, Union, Tuple

import requests
from smartsurge.client import SmartSurgeClient

from .exceptions import APIError, RateLimitExceeded, OpenRouterError
from .types import RequestMethod


class HTTPManager:
    """
    Manages HTTP communications with the OpenRouter API.
    
    Attributes:
        client (SmartSurgeClient or requests.Session): HTTP client with rate limiting.
        base_url (str): Base URL for API requests.
        logger (logging.Logger): HTTP communication logger.
    """
    
    def __init__(self, 
                 base_url: Optional[str] = None,
                 client: Optional[SmartSurgeClient] = None,
                 **kwargs):
        """
        Initialize the HTTP manager.
        
        Args:
            base_url (str): Base URL for API requests. If None, uses the URL from pre-configured client.
            client (Optional[SmartSurgeClient]): Pre-configured HTTP client. If None, one is created.
            kwargs: Additional arguments for SmartSurgeClient.
            
        Raises:
            OpenRouterError: If neither base_url nor client is provided.
        """
        if base_url is None and client is None:
            raise OpenRouterError("Either base_url or client must be provided")
        
        # Set up logger for HTTP operations
        self.logger = logging.getLogger("openrouter_client.http")
        
        # Store base_url for forming full request URLs
        if base_url is None and client is not None:
            # Extract base_url from client or set a default
            self.base_url = getattr(client, "base_url", "")
        else:
            self.base_url = base_url.rstrip("/") if base_url else ""
        
        if client:
            # Use the provided client
            self.client = client
            self.logger.debug("Using provided HTTP client")
            if base_url is not None:
                self.logger.warning("base_url is ignored when using a pre-configured client")
        else:
            # Create a SmartSurgeClient with appropriate configuration
            self.client = SmartSurgeClient(
                base_url=self.base_url,
                **kwargs
            )
            self.logger.debug("Created SmartSurgeClient with rate limiting")
        
        self.logger.info(f"HTTP manager initialized with base_url={base_url}")

    def request(self,
                method: RequestMethod,
                endpoint: str,
                headers: Optional[Dict[str, str]] = None,
                params: Optional[Dict[str, Any]] = None,
                json: Optional[Dict[str, Any]] = None,
                data: Optional[Union[Dict[str, Any], str, bytes]] = None,
                files: Optional[Dict[str, Any]] = None,
                stream: bool = False,
                timeout: Optional[Union[float, Tuple[float, float]]] = None) -> requests.Response:
        """
        Make an HTTP request to the OpenRouter API.
        
        Args:
            method (RequestMethod): HTTP method to use.
            endpoint (str): API endpoint to call (will be combined with base_url).
            headers (Optional[Dict[str, str]]): HTTP headers to include.
            params (Optional[Dict[str, Any]]): URL query parameters.
            json (Optional[Dict[str, Any]]): JSON body to send.
            data (Optional[Union[Dict[str, Any], str, bytes]]): Form data or raw data to send.
            files (Optional[Dict[str, Any]]): Files to upload.
            stream (bool): Whether to stream the response. Defaults to False.
            timeout (Optional[Union[float, Tuple[float, float]]]): Request timeout override.
            
        Returns:
            Response: API response.
            
        Raises:
            APIError: For API-related errors.
            RateLimitExceeded: When rate limits are exceeded.
            requests.RequestException: For network-related errors.
        """
        # Check if the method is a valid RequestMethod value
        if not isinstance(method, RequestMethod):
            raise TypeError(f"'method' must be a RequestMethod enum, not {type(method).__name__}")
        
        # Check if endpoint is a valid string
        if not isinstance(endpoint, str):
            raise TypeError(f"'endpoint' must be a string, not {type(endpoint).__name__}")
        
        # Check if headers is a dictionary or None
        if headers is not None and not isinstance(headers, dict):
            raise TypeError(f"'headers' must be a dictionary, not {type(headers).__name__}")

        # Check if params is a dictionary or None
        if params is not None and not isinstance(params, dict):
            raise TypeError(f"'params' must be a dictionary, not {type(params).__name__}")

        # Check if json is a dictionary or None
        if json is not None and not isinstance(json, dict):
            raise TypeError(f"'json' must be a dictionary, not {type(json).__name__}")
        
        # Form the full URL by combining base_url and endpoint
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        # If headers are None, initialize as empty dictionary
        if headers is None:
            headers = {}
        
        # Generate a request ID for logging and correlation
        request_id = f"req_{int(time.time() * 1000)}_{id(self)}"
        
        # Log the outgoing request details (sanitize sensitive information)
        sanitized_json = None
        if json:
            # Create a shallow copy to avoid modifying the original
            sanitized_json = {**json}
            # Sanitize sensitive fields like API keys if present
            if 'api_key' in sanitized_json:
                sanitized_json['api_key'] = '***'
            if 'Authorization' in sanitized_json:
                sanitized_json['Authorization'] = '***'
        
        self.logger.debug(
            f"Request {request_id}: {method.value} {url} | "
            f"Headers: {headers} | Params: {params} | "
            f"JSON: {sanitized_json} | Stream: {stream}"
        )
        
        # Determine the appropriate timeout to use (given or a reasonable default)
        actual_timeout = timeout if timeout is not None else 60.0
        
        # Record the start time for performance tracking
        start_time = time.time()
        
        try:
            try:
                response = self.client.request(
                    method=method.value,
                    endpoint=url,
                    headers=headers,
                    params=params,
                    json=json,
                    data=data,
                    files=files,
                    stream=stream,
                    timeout=actual_timeout
                )
            except Exception as e:
                raise
            
            # Calculate request duration for logging
            duration = time.time() - start_time
            
            # Log response details including status code and duration
            self.logger.debug(
                f"Response {request_id}: Status {response.status_code} | "
                f"Duration: {duration:.2f}s"
            )
            
            # Handle error responses (non-2xx status codes)
            if not 200 <= response.status_code < 300:
                if 300 <= response.status_code < 400:
                    # Handle redirects by retrying with allow_redirects=True
                    self.logger.info(f"Received {response.status_code} redirect, retrying with allow_redirects=True")
                    try:
                        response = self.client.request(
                            method=method.value,
                            endpoint=url,
                            headers=headers,
                            params=params,
                            json=json,
                            data=data,
                            files=files,
                            stream=stream,
                            timeout=actual_timeout,
                            allow_redirects=True
                        )
                    except Exception as e:
                        self.logger.error(f"Error when following redirect: {str(e)}")
                        raise
                elif response.status_code == 429:
                    # Rate limit exceeded
                    retry_after = response.headers.get('Retry-After')
                    raise RateLimitExceeded(
                        message="Rate limit exceeded",
                        retry_after=retry_after,
                        response=response
                    )

                elif 400 <= response.status_code < 500:
                    # Client error
                    error_detail = {}
                    error_message = f"API Error: {response.status_code}"
                    
                    try:
                        response_data = response.json()
                        
                        # Check if response has OpenRouter's error structure
                        if 'error' in response_data:
                            error_info = response_data['error']
                            error_message = error_info.get('message', error_message)
                            error_detail = error_info
                        else:
                            # Fallback to using the whole response as error detail
                            error_detail = response_data
                            error_message = response_data.get('message', error_message)
                            
                    except Exception:
                        # If JSON parsing fails, use the raw response text
                        if response.text.strip():
                            error_message = f"API Error {response.status_code}: {response.text}"
                        error_detail = {'message': error_message}
                    
                    # Log the full error for debugging
                    self.logger.error(f"API Error {response.status_code}: {error_message}")
                    
                    raise APIError(
                        message=error_message,
                        code=error_detail.get('code', response.status_code),
                        param=error_detail.get('param'),
                        type=error_detail.get('type'),
                        status_code=response.status_code,
                        response=response
                    )
                elif 500 <= response.status_code < 600:
                    # Server error
                    raise APIError(
                        message=f"Server error: {response.status_code}",
                        status_code=response.status_code,
                        response=response
                    )
            
            return response
            
        except (RateLimitExceeded, APIError):
            # Re-raise our custom exceptions
            raise
        except requests.RequestException as e:
            # Convert requests exceptions to APIError
            self.logger.error(f"Request error: {str(e)}")
            raise APIError(
                message=f"Request failed: {str(e)}"
            ) from e

    def get(self, endpoint: str, **kwargs) -> requests.Response:
        """
        Make a GET request to the OpenRouter API.
        
        Args:
            endpoint (str): API endpoint to call.
            **kwargs: Additional parameters to pass to request().
            
        Returns:
            Response: API response.
        """
        return self.request(method=RequestMethod.GET, endpoint=endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs) -> requests.Response:
        """
        Make a POST request to the OpenRouter API.
        
        Args:
            endpoint (str): API endpoint to call.
            **kwargs: Additional parameters to pass to request().
            
        Returns:
            Response: API response.
        """
        return self.request(method=RequestMethod.POST, endpoint=endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs) -> requests.Response:
        """
        Make a PUT request to the OpenRouter API.
        
        Args:
            endpoint (str): API endpoint to call.
            **kwargs: Additional parameters to pass to request().
            
        Returns:
            Response: API response.
        """
        return self.request(method=RequestMethod.PUT, endpoint=endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        """
        Make a DELETE request to the OpenRouter API.
        
        Args:
            endpoint (str): API endpoint to call.
            **kwargs: Additional parameters to pass to request().
            
        Returns:
            Response: API response.
        """
        return self.request(method=RequestMethod.DELETE, endpoint=endpoint, **kwargs)

    def patch(self, endpoint: str, **kwargs) -> requests.Response:
        """
        Make a PATCH request to the OpenRouter API.
        
        Args:
            endpoint (str): API endpoint to call.
            **kwargs: Additional parameters to pass to request().
            
        Returns:
            Response: API response.
        """
        return self.request(method=RequestMethod.PATCH, endpoint=endpoint, **kwargs)

    def stream_request(self, method: RequestMethod, endpoint: str, **kwargs) -> requests.Response:
        """
        Make a streaming request to the OpenRouter API.
        
        Args:
            method (RequestMethod): HTTP method to use.
            endpoint (str): API endpoint to call.
            **kwargs: Additional parameters to pass to request().
            
        Returns:
            Response: Streaming API response.
        """
        # Force stream=True in kwargs to ensure streaming behavior
        kwargs['stream'] = True
        return self.request(method=method, endpoint=endpoint, **kwargs)

    def set_rate_limit(self, 
                       endpoint: str,
                       method: Union[str, RequestMethod],
                       max_requests: int, 
                       time_period: float,
                       cooldown: Optional[float] = None) -> None:
        """
        Set the rate limit for a specific API endpoint and method.
        
        This method passes through to SmartSurgeClient.set_rate_limit to dynamically
        adjust rate limiting parameters for a specific endpoint/method combination.
        
        Args:
            endpoint (str): The API endpoint to set rate limit for.
            method (Union[str, RequestMethod]): HTTP method (GET, POST, etc.).
            max_requests (int): Maximum number of requests allowed per time period.
            time_period (float): Time period in seconds for the rate limit.
            cooldown (Optional[float]): Cooldown period in seconds after hitting the limit.
            
        Raises:
            AttributeError: If the client doesn't support set_rate_limit.
            ValueError: If invalid rate limit parameters are provided.
        """
        if not hasattr(self.client, 'set_rate_limit'):
            raise AttributeError(
                "The HTTP client does not support dynamic rate limit configuration. "
                "Ensure you're using SmartSurgeClient."
            )
        
        # Convert RequestMethod enum to string if needed
        if isinstance(method, RequestMethod):
            method = method.value
        
        # Log the rate limit change
        self.logger.info(
            f"Setting rate limit for {method} {endpoint}: "
            f"max_requests={max_requests}, time_period={time_period}s, cooldown={cooldown}s"
        )
        
        try:
            # Pass through to SmartSurgeClient
            self.client.set_rate_limit(
                endpoint=endpoint,
                method=method,
                max_requests=max_requests,
                time_period=time_period,
                cooldown=cooldown
            )
            self.logger.debug(f"Rate limit successfully updated for {method} {endpoint}")
        except Exception as e:
            self.logger.error(f"Failed to set rate limit: {str(e)}")
            raise
    
    def set_global_rate_limit(self,
                            max_requests: int,
                            time_period: float,
                            cooldown: Optional[float] = None) -> None:
        """
        Set a global rate limit for all common OpenRouter API endpoints.
        
        This is a convenience method that applies the same rate limit to all
        standard OpenRouter endpoints. For fine-grained control, use set_rate_limit().
        
        Args:
            max_requests (int): Maximum number of requests allowed per time period.
            time_period (float): Time period in seconds for the rate limit.
            cooldown (Optional[float]): Cooldown period in seconds after hitting the limit.
        """
        # Common OpenRouter endpoints
        common_endpoints = [
            ('/chat/completions', 'POST'),
            ('/completions', 'POST'),
            ('/models', 'GET'),
            ('/credits', 'GET'),
            ('/generation', 'GET'),
            ('/auth/key', 'GET'),
            ('/auth/keys', 'POST'),
            ('/keys', 'POST'),
        ]
        
        self.logger.info(
            f"Setting global rate limit: max_requests={max_requests}, "
            f"time_period={time_period}s, cooldown={cooldown}s"
        )
        
        for endpoint, method in common_endpoints:
            try:
                self.set_rate_limit(
                    endpoint=endpoint,
                    method=method,
                    max_requests=max_requests,
                    time_period=time_period,
                    cooldown=cooldown
                )
            except Exception as e:
                self.logger.warning(
                    f"Failed to set rate limit for {method} {endpoint}: {str(e)}"
                )
    
    def close(self) -> None:
        """
        Close the HTTP manager and release resources.
        """
        if hasattr(self.client, 'close'):
            self.client.close()
            self.logger.debug("HTTP manager closed and resources released")
