import time
import requests
def retry_with_backoff(max_retries=3, base_delay=1, max_delay=5):
    def decorator(func):
        def wrapper(*args, **kwargs):
            retry_count = 0
            delay = base_delay
            while retry_count < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    time.sleep(delay)
                    retry_count += 1
                    delay = min(delay * 1.5, max_delay)
                    if retry_count == max_retries:
                        print(f"error happend when {func.__name__} ,msg: {e}")
            raise Exception(
                f"function {func.__name__} failed after {max_retries} retries."
            )
        return wrapper
    return decorator