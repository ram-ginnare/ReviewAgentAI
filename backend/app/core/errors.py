from fastapi import HTTPException


def api_error(status_code: int, message: str, code: str, headers: dict[str, str] | None = None) -> HTTPException:
    return HTTPException(
        status_code=status_code,
        detail=message,
        headers={**(headers or {}), "X-Error-Code": code},
    )
