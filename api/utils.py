import time
from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache

def ratelimit(num_requests=5, timeframe=60):
    """
    A decorator for rate-limiting API views.
    
    Args:
        num_requests (int): Maximum number of requests allowed within the timeframe
        timeframe (int): Time window in seconds
        
    Returns:
        Response with 429 status code if rate limit is exceeded
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(view_instance, request, *args, **kwargs):
            # Get client IP address
            ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))
            
            # Create a unique cache key based on the IP and view function
            cache_key = f"ratelimit_{ip}_{view_func.__name__}"
            
            # Get the list of timestamps for this client from cache
            timestamps = cache.get(cache_key, [])
            
            # Get current timestamp
            now = time.time()
            
            # Filter out timestamps that are outside of our timeframe
            timestamps = [t for t in timestamps if now - t < timeframe]
            
            # Check if request limit is exceeded
            if len(timestamps) >= num_requests:
                return Response(
                    {"error": "Rate limit exceeded. Please try again later."},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )
            
            # Add current timestamp to the list and update cache
            timestamps.append(now)
            cache.set(cache_key, timestamps, timeout=timeframe)
            
            # Proceed with the view execution
            return view_func(view_instance, request, *args, **kwargs)
        return _wrapped_view
    return decorator 