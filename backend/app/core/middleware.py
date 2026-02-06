import time
import logging
import traceback
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings

logger = logging.getLogger("app.middleware")

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        path = request.url.path
        
        logger.info(f"Request started: {method} {path} from {client_ip}")
        
        try:
            response = await call_next(request)
            process_time = (time.time() - start_time) * 1000
            formatted_process_time = "{0:.2f}".format(process_time)
            
            logger.info(
                f"Request completed: {method} {path} - Status: {response.status_code} - "
                f"Duration: {formatted_process_time}ms"
            )
            
            response.headers["X-Process-Time"] = formatted_process_time
            return response
            
        except Exception as e:
            process_time = (time.time() - start_time) * 1000
            formatted_process_time = "{0:.2f}".format(process_time)
            
            # Global exception handling for middleware level
            if settings.ENVIRONMENT == "development":
                stack_trace = traceback.format_exc()
                logger.error(
                    f"Request failed: {method} {path} - Error: {str(e)}\n{stack_trace}"
                )
            else:
                logger.error(
                    f"Request failed: {method} {path} - Error: {str(e)}"
                )
            
            # Re-raise to be caught by the global exception handler in main.py
            raise e
