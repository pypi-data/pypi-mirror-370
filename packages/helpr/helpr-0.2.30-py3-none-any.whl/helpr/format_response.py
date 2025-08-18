from typing import Optional, Union
from fastapi.responses import JSONResponse
from fastapi import status as HTTPStatus

def create_response(data: dict, message: str, status: str, status_code: int, error_code: Optional[int] = None) -> JSONResponse:
    return JSONResponse(
        content={
            "data": data,
            "message": message,
            "status": status,
            "error_code": error_code
        },
        status_code=status_code
    )

def jsonify_success(data: Optional[Union[dict, list]] = None, message: Optional[str] = None, status_code: int = 200):
    return create_response(data=data if data else {}, message=message, status="success", status_code=status_code)

def jsonify_failure(data: Optional[Union[dict, list]] = None, message: Optional[str] = None, error_code: Optional[int] = None, status_code: int = 400):
    return create_response(data=data if data else {}, message=message, status="failed", status_code=status_code, error_code=error_code)