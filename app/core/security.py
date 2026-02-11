from fastapi import Security
from fastapi.security import APIKeyHeader
from app.core.config import settings
from app.core.exceptions import UnauthorizedException

api_key_header = APIKeyHeader(name="X-Admin-Key", auto_error=False)

async def get_admin_user(api_key_header: str = Security(api_key_header)):
    if api_key_header == settings.API_SECRET_KEY:
        return True
    raise UnauthorizedException(detail="Admin privileges required")
