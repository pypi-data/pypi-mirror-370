from nadf.exception.business_exception import BaseException


class SSLInvalidException(BaseException):
    def __init__(self):
        message = "SSL 인증 실패입니다."
        status_code = 500
        super().__init__(message=message, status_code=status_code)