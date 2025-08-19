from fastapi import HTTPException
from typing import Union


class ErrorHTTPException(HTTPException):
    def __init__(
            self, status_code=501,
            detail: str = 'General error',
            code: Union[int, str] = 'Unknown',
            description: str = 'General error'):
        super().__init__(status_code=status_code, detail=detail)
        self.code = code
        self.description = description

    def __iter__(self):
        dict_ = {
            'description': self.description,
            'content': {
                'application/json': {
                    'example': {
                        'detail': self.detail,
                        'code': self.code
                    }
                }
            }
        }
        for key in dict_:
            yield key, dict_[key]


class BadRequest(ErrorHTTPException):
    def __init__(self, detail: str = None, code: int = None):
        if not detail:
            detail = 'Error bad request'
        if not code:
            code = 1502

        super().__init__(
            status_code=502,
            description='Error bad request',
            detail=detail,
            code=code
        )
