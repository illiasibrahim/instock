from rest_framework.exceptions import APIException
from rest_framework import status


class BaseAPIException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = 5000
    message = "An API error occurred."

    def __init__(self, code=None, message=None):
        if message:
            self.message = message
        if code:
            self.code = code
        self.default_detail = {
            "code": self.code,
            "message": self.message
        }
        super().__init__()


class LocationOutOfBoundException(BaseAPIException):

    def __init__(self):
        code = 5001
        message = "No active stores available near your location."
        super().__init__(code=code, message=message)


class MedicinesRequiredException(BaseAPIException):

    def __init__(self):
        code = 5002
        message = "Medicines list cannot be blank."
        super().__init__(code=code, message=message)


class MedicineUnavailableException(BaseAPIException):

    def __init__(self, medicine):
        code = 5003
        message = f"{medicine} not available at your location."
        super().__init__(code=code, message=message)
