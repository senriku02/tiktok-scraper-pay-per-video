import logging

logger = logging.getLogger(__name__)

class CaptchaDetected(Exception):
    """Raised when a captcha or similar block is detected."""

def handle_captcha(context: str) -> None:
    """
    Simple captcha handler used as a hook for real-world integration.
    For the local demo this just logs a warning and raises `CaptchaDetected`.
    """
    message = f"Captcha detected while processing: {context}"
    logger.warning(message)
    raise CaptchaDetected(message)