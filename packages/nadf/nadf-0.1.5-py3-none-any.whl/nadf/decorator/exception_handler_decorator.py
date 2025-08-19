# from typing import Callable
# from nadf.exception.business_exception import BaseException
#
# def exception_handler(func: Callable) -> Callable:
#     def inner(*args, **kwargs):
#         try:
#             return func(*args, **kwargs)
#         except BaseException as e:
#             print("error : ", e.message)
#             print("status code:", e.status_code)
#         except Exception as e:
#             print("error : ", str(e))
#     return inner
