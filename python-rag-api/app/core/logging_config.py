"""
Logging configuration for the application
"""
import logging
import sys
from typing import Callable
from fastapi import Request, Response
from fastapi.routing import APIRoute
import time

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger("document_rag_api")


class LoggingRouteHandler(APIRoute):
    """Custom route handler that logs requests and responses"""
    
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()
        
        async def custom_route_handler(request: Request) -> Response:
            # Log request
            start_time = time.time()
            client_ip = request.client.host if request.client else "unknown"
            
            # Log request details (without consuming body to avoid issues)
            logger.info(
                f"Request: {request.method} {request.url.path} | "
                f"Client: {client_ip} | "
                f"Query params: {dict(request.query_params)}"
            )
            
            # Process request
            try:
                response = await original_route_handler(request)
                
                # Log successful response
                process_time = time.time() - start_time
                logger.info(
                    f"Response: {request.method} {request.url.path} | "
                    f"Status: {response.status_code} | "
                    f"Time: {process_time:.3f}s"
                )
                
                return response
            except Exception as e:
                # Log error with full details
                process_time = time.time() - start_time
                logger.error(
                    f"Error: {request.method} {request.url.path} | "
                    f"Client: {client_ip} | "
                    f"Error: {type(e).__name__}: {str(e)} | "
                    f"Time: {process_time:.3f}s",
                    exc_info=True,  # Include full traceback
                )
                raise
        
        return custom_route_handler

