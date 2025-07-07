import time
import asyncio

from functools import wraps


def rate_limited(min_interval_seconds=1.0):
    """Evita que una función se ejecute más de una vez cada X segundos."""
    def decorator(func):
        last_called = [0.0]

        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            wait_time = min_interval_seconds - elapsed
            if wait_time > 0:
                print(f"⏳ Esperando {wait_time:.2f}s para respetar el rate limit...")
                time.sleep(wait_time)
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        return wrapper
    return decorator

def async_rate_limited(min_interval_seconds=1.0):
    """Versión async del rate limit decorador."""
    def decorator(func):
        last_called = [0.0]

        @wraps(func)
        async def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            wait_time = min_interval_seconds - elapsed
            if wait_time > 0:
                print(f"⏳ (async) Esperando {wait_time:.2f}s para respetar el rate limit...")
                await asyncio.sleep(wait_time)
            result = await func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        return wrapper
    return decorator

def rate_limited_with_retries(min_interval_seconds=1.0, max_retries=3, retry_on_codes=("ApiCallLimit",)):
    """Decorador para limitar frecuencia de llamadas y reintentar si hay errores específicos."""
    def decorator(func):
        last_called = [0.0]

        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_retries + 1):
                elapsed = time.time() - last_called[0]
                wait_time = min_interval_seconds - elapsed
                if wait_time > 0:
                    print(f"⏳ Esperando {wait_time:.2f}s para rate limit...")
                    time.sleep(wait_time)

                result = func(*args, **kwargs)
                last_called[0] = time.time()

                # Reintentar si hay error conocido
                if isinstance(result, dict) and "error_response" in result:
                    code = result["error_response"].get("code")
                    if code in retry_on_codes:
                        print(f"⚠️ API rate limited (code: {code}). Intento {attempt}/{max_retries}")
                        time.sleep(min_interval_seconds)
                        continue  # reintentar
                return result  # éxito o error no controlado

            print("❌ Se alcanzó el número máximo de reintentos.")
            return result  # último intento, aunque fallido

        return wrapper
    return decorator