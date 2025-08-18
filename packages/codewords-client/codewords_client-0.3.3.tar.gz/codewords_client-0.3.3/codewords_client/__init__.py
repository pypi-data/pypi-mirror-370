import logging
import os
import uuid
from typing import Any
from urllib.parse import urljoin

import httpx
import starlette.exceptions
import structlog
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from structlog.contextvars import bind_contextvars, clear_contextvars, get_contextvars

from .codewords_client import (
    AsyncCodewordsClient,
    AsyncCodewordsResponse,
    CodewordsClient,
    CodewordsResponse,
)


def _setup_logging():
    """Configure structlog logging."""
    logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(sort_keys=True)
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

class RequestIdMiddleware(BaseHTTPMiddleware):
    """Middleware to handle request IDs and correlation IDs."""
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        request_id = request.headers.get("X-Request-Id", str(uuid.uuid4()))
        correlation_id = request.headers.get("X-Correlation-Id", request_id)
        caller_id = request.headers.get("Codewords-Caller-Id", "")
        bind_contextvars(request_id=request_id, correlation_id=correlation_id, caller_id=caller_id)

        response = await call_next(request)
        response.headers["X-Request-Id"] = request_id
        response.headers["X-Correlation-Id"] = correlation_id
        response.headers["Codewords-Caller-Id"] = caller_id

        clear_contextvars()
        return response

def _setup_exception_handlers(app: FastAPI):
    """Set up standard exception handlers."""
    logger = structlog.get_logger()

    app.exception_handlers.pop(starlette.exceptions.HTTPException, None)

    @app.exception_handler(starlette.exceptions.HTTPException)
    async def http_exception_handler(request: Request, exc: starlette.exceptions.HTTPException):
        """Handles expected client errors (4xx) and re-raises custom HTTPExceptions."""
        logger.exception("HTTP exception caught", path=str(request.url), status_code=exc.status_code, detail=exc.detail)
        headers = dict(exc.headers or {})
        headers.setdefault("Error-Origin", "service")
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail}, headers=headers)

    @app.exception_handler(httpx.HTTPStatusError)
    async def http_status_error_handler(request: Request, exc: httpx.HTTPStatusError):
        """Handles upstream httpx HTTPStatusError by mapping to an HTTP response."""
        status_code = getattr(getattr(exc, "response", None), "status_code", 500)
        # Try to extract a useful detail from the upstream response
        detail: Any
        response = getattr(exc, "response", None)
        if response is not None:
            try:
                payload = response.json()
                if isinstance(payload, dict) and "detail" in payload:
                    detail = payload.get("detail")
                else:
                    detail = payload
            except Exception:
                try:
                    detail = response.text
                except Exception:
                    detail = str(exc)
        else:
            detail = str(exc)

        logger.exception(
            "HTTPStatusError caught",
            path=str(request.url),
            upstream_url=str(getattr(getattr(exc, "request", None), "url", "")),
            status_code=status_code,
            detail=str(detail) if not isinstance(detail, (str, int, float, bool, type(None))) else detail,
        )

        headers = {"Error-Origin": "service"}
        return JSONResponse(status_code=status_code, content={"detail": detail}, headers=headers)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handles FastAPI request-validation errors (422)."""
        logger.exception("Request validation failed", path=str(request.url), errors=exc.errors())
        return JSONResponse(status_code=422, content={"detail": jsonable_encoder(exc.errors())}, headers={"Error-Origin": "service"})

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        """Catch-all handler for unhandled errors, returning a 500 response."""
        logger.error("Unhandled exception", path=str(request.url), error_type=exc.__class__.__name__)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error:\n" + str(exc)},
            headers={"Error-Origin": "service"},
        )

if not hasattr(FastAPI, '_codewords_patched'):
    _original_fastapi_init = FastAPI.__init__

    def _enhanced_fastapi_init(self, auto_setup: bool = True, **kwargs: Any) -> None:
        """Enhanced FastAPI constructor that auto-configures CodeWords infrastructure."""
        
        # Call original constructor
        _original_fastapi_init(self, **kwargs)
        
        if auto_setup:
            self.add_middleware(RequestIdMiddleware)
            _setup_exception_handlers(self)

    # Apply the monkey patch
    FastAPI.__init__ = _enhanced_fastapi_init
    FastAPI._codewords_patched = True

def run_service(app: FastAPI, **kwargs):
    """Convenience function to run the service with sensible defaults."""
    import uvicorn
    logger = structlog.get_logger()
    
    defaults = {'host': '0.0.0.0', 'port': int(os.environ.get("PORT", 8000)), 'loop': 'uvloop'}
    defaults.update(kwargs)
    
    logger.info("Starting CodeWords service...")
    uvicorn.run(app, **defaults)

# Setup logging when module is imported
_setup_logging()

# Create logger instance for export
logger = structlog.get_logger()

def _patch_firecrawl():
    """Monkey patch FirecrawlApp to auto-inject correlation IDs and CodeWords proxy settings."""
    try:
        from firecrawl import FirecrawlApp as OriginalFirecrawlApp
        if hasattr(OriginalFirecrawlApp, '_codewords_patched'):
            return
        
        _original_init = OriginalFirecrawlApp.__init__
        _original_prepare_headers = OriginalFirecrawlApp._prepare_headers
        
        def _enhanced_init(self, api_key=None, api_url=None, correlation_id=None, **kwargs):
            api_key = api_key or os.environ.get('CODEWORDS_API_KEY')
            api_url = api_url or urljoin(os.environ.get('CODEWORDS_RUNTIME_URI', 'https://runtime.codewords.ai'), "run/firecrawl")
            correlation_id = correlation_id or get_contextvars().get("correlation_id")
            _original_init(self, api_key=api_key, api_url=api_url, **kwargs)
            self.correlation_id = correlation_id
        
        def _enhanced_prepare_headers(self):
            headers = _original_prepare_headers(self)
            if hasattr(self, 'correlation_id') and self.correlation_id:
                headers['X-Correlation-Id'] = self.correlation_id
            return headers
        
        OriginalFirecrawlApp.__init__ = _enhanced_init
        OriginalFirecrawlApp._prepare_headers = _enhanced_prepare_headers
        OriginalFirecrawlApp._codewords_patched = True
        logger.debug("FirecrawlApp successfully patched for CodeWords auto-configuration")
        
    except ImportError:
        pass
    except Exception as e:
        logger.warning("Failed to patch FirecrawlApp", error=str(e))

def _patch_openai():
    """Monkey patch AsyncOpenAI to auto-inject CodeWords proxy settings and correlation IDs."""
    try:
        from openai import AsyncOpenAI
        if hasattr(AsyncOpenAI, '_codewords_patched'):
            return
        
        _original_init = AsyncOpenAI.__init__
        
        def _enhanced_init(self, api_key=None, base_url=None, default_headers=None, **kwargs):
            api_key = api_key or os.environ.get('CODEWORDS_API_KEY')
            base_url = base_url or urljoin(os.environ.get('CODEWORDS_RUNTIME_URI', 'https://runtime.codewords.ai'), "run/openai/v1")
            default_headers = dict(default_headers or {})
            
            if 'X-Correlation-Id' not in default_headers:
                correlation_id = get_contextvars().get("correlation_id")
                if correlation_id:
                    default_headers['X-Correlation-Id'] = correlation_id
            
            _original_init(self, api_key=api_key, base_url=base_url, default_headers=default_headers, **kwargs)
        
        AsyncOpenAI.__init__ = _enhanced_init
        AsyncOpenAI._codewords_patched = True
        logger.debug("AsyncOpenAI successfully patched for CodeWords auto-configuration")
        
    except ImportError:
        pass
    except Exception as e:
        logger.warning("Failed to patch AsyncOpenAI", error=str(e))

def _patch_anthropic():
    """Monkey patch AsyncAnthropic to auto-inject CodeWords proxy settings and correlation IDs."""
    try:
        from anthropic import AsyncAnthropic
        if hasattr(AsyncAnthropic, '_codewords_patched'):
            return
        
        _original_init = AsyncAnthropic.__init__
        
        def _enhanced_init(self, api_key=None, base_url=None, default_headers=None, **kwargs):
            api_key = api_key or os.environ.get('CODEWORDS_API_KEY')
            base_url = base_url or urljoin(os.environ.get('CODEWORDS_RUNTIME_URI', 'https://runtime.codewords.ai'), "run/anthropic")
            default_headers = dict(default_headers or {})
            
            if 'X-Correlation-Id' not in default_headers:
                correlation_id = get_contextvars().get("correlation_id")
                if correlation_id:
                    default_headers['X-Correlation-Id'] = correlation_id
            
            _original_init(self, api_key=api_key, base_url=base_url, default_headers=default_headers, **kwargs)
        
        AsyncAnthropic.__init__ = _enhanced_init
        AsyncAnthropic._codewords_patched = True
        logger.debug("AsyncAnthropic successfully patched for CodeWords auto-configuration")
        
    except ImportError:
        pass
    except Exception as e:
        logger.warning("Failed to patch AsyncAnthropic", error=str(e))

# Import redis_client from separate module (lazy loading)
from .redis import redis_client

# Apply all monkey patches
_patch_firecrawl()
_patch_openai()
_patch_anthropic()

# Export everything
__all__ = [
    'AsyncCodewordsClient', 
    'CodewordsClient', 
    'AsyncCodewordsResponse', 
    'CodewordsResponse',
    'logger', 
    'run_service', 
    'RequestIdMiddleware',
    'redis_client'
]
