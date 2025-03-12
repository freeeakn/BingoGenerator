from loguru import logger
import sentry_sdk
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi import FastAPI
import sys
import os
from dotenv import load_dotenv

# Загружаем .env файл
load_dotenv()

class LogConfig:
    @staticmethod
    def setup_logging():
        """Configure logging settings"""
        # Remove default handler
        logger.remove()
        
        # Add console handler
        logger.add(
            sys.stderr,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
            level="INFO"
        )
        
        # Add file handler
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        logger.add(
            "logs/bingo.log",
            rotation="500 MB",
            retention="10 days",
            level="INFO"
        )

    @staticmethod
    def setup_monitoring(app: FastAPI):
        """Configure Prometheus monitoring"""
        Instrumentator().instrument(app).expose(app)

    @staticmethod
    def setup_sentry():
        """Configure Sentry error tracking"""
        sentry_dsn = os.getenv("SENTRY_DSN")
        if sentry_dsn:
            sentry_sdk.init(
                dsn=sentry_dsn,
                traces_sample_rate=1.0,
                profiles_sample_rate=1.0,
            )
        else:
            logger.warning("Sentry DSN not configured, error tracking disabled")

    @staticmethod
    def log_error(error: Exception, context: dict = None):
        """Log error with context"""
        logger.error(f"Error: {str(error)}")
        if context:
            logger.error(f"Context: {context}")
        
        # Capture exception in Sentry only if it's configured
        if sentry_sdk.Hub.current.client:
            sentry_sdk.capture_exception(error) 