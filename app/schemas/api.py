from enum import Enum
from typing import Optional

from pydantic import BaseModel

class ResponseStatus(Enum):
    SUCCESS = "SUCCESS"
    DATA_NOT_FOUND = "DATA_NOT_FOUND"
    BAD_REQUEST = "BAD_REQUEST"
    ALREADY_EXIST = "ALREADY_EXIST"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    CREATED = "CREATED"
    UPDATED = "UPDATED"
    DELETED = "DELETED"
    FAILED = "FAILED"
    RETRIEVED = "RETRIEVED"
    ACCEPTED = "ACCEPTED"

class Response:
    def __init__(self, message: str, success: bool, status: ResponseStatus, data: any):
        self.message = message
        self.success = success
        self.status = status
        self.data = data

    def to_dict(self):
        return {
            "message": self.message,
            "success": self.success,
            "status": self.status.value,  # Return the enum value, not the enum itself
            "data": self.data,
        }
        
        
class FilterRequest(BaseModel):
    filter: list[dict] = []