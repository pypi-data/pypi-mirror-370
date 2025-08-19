import asyncio
import functools
import inspect
from typing import Optional
from nadf.exception.not_namuwiki_exception import NotNamuwikiException

def _extract_url(func, args, kwargs, param: str = "url") -> Optional[str]:
    """함수 호출 인자에서 'url' 값을 찾아 반환"""
    try:
        bound = inspect.signature(func).bind_partial(*args, **kwargs)
        return bound.arguments.get(param)
    except TypeError:
        return kwargs.get(param)

def _validate_namuwiki(url: Optional[str]):
    if not url or "namu.wiki" not in str(url):
        raise NotNamuwikiException()

def check_namuwiki_url(param: str = "url"):
    """데코레이터: url 인자가 반드시 namu.wiki 포함해야 함"""
    def wrapper(func):
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def aw(*args, **kwargs):
                url = _extract_url(func, args, kwargs, param)
                _validate_namuwiki(url)
                return await func(*args, **kwargs)
            return aw
        else:
            @functools.wraps(func)
            def sw(*args, **kwargs):
                url = _extract_url(func, args, kwargs, param)
                _validate_namuwiki(url)
                return func(*args, **kwargs)
            return sw
    return wrapper
