from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db.session import get_db
from app.auth.jwt import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user_payload(
    token: str = Depends(oauth2_scheme)
) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(token)

    if payload is None:
        raise credentials_exception

    if payload.get("type") != "access":
        raise credentials_exception

    if not payload.get("sub") or not payload.get("schema"):
        raise credentials_exception

    return payload

async def get_tenant_db(
    payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db),
) -> AsyncSession:
    schema_name = payload.get("schema")

    # This is the core of tenant isolation
    # Every query after this line runs in the tenant's schema
    await db.execute(text(f'SET search_path TO "{schema_name}", public'))

    return db