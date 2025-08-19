from http.client import HTTPException

from nadf.exception.not_namuwiki_exception import NotNamuwikiException


def check_namuwiki_url(func):
    def wrapper(*args, **kwargs):
        try:
            url = kwargs.get("url")

            if not url or "namu.wiki" not in url:
                raise NotNamuwikiException()

            return func(*args, **kwargs)
        except NotNamuwikiException as e:
            print("error : ", e.message)
            print("status code:", e.status_code)
    return wrapper
