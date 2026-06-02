import time
import logging

logger = logging.getLogger(__name__)

def with_retry(func, retries=3, delay=1, returnBoolean=False, *args, **kwargs):
    """Call *func* up to *retries* times, pausing *delay* seconds between attempts.

    :param func: The callable to execute.
    :param retries: Maximum number of attempts before giving up.
    :param delay: Seconds to wait between consecutive attempts.
    :param returnBoolean: When True, return a bool (success/failure) instead of
        the function's own return value.
    :return: The function's return value on success; ``None`` (or ``False`` when
        *returnBoolean* is True) if every attempt raises an exception.
    """
    for attempt in range(retries):
        try:
            result = func(*args, **kwargs)
            if returnBoolean:
                return True
            return result
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed with error: {e}")
            if attempt < retries - 1:
                logger.info(f"Retrying function {func.__name__} in {delay} seconds (attempt {attempt + 2}/{retries})")
                time.sleep(delay)
    logger.error(f"Function {func.__name__} failed after {retries} attempts.")
    if returnBoolean:
        return False
    return None