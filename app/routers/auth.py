from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from passlib.context import CryptContext
from app.db.session import get_db
from app.models.user import User
from app.models.tenant import Tenant
from app.schemas.auth import UserRegister, UserLogin, TokenResponse, TokenRefresh
from app.auth.jwt import create_access_token, create_refresh_token, decode_token
import re

router = APIRouter(prefix="/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def generate_schema_name(name: str) -> str:
    safe = re.sub(r'[^a-zA-Z0-9]', '_', name.lower())
    return f"tenant_{safe}"

@router.post("/register", response_model=TokenResponse)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db)
):
    schema_name = generate_schema_name(user_data.tenant_name)

    # Check if tenant already exists
    result = await db.execute(
        text("SELECT id, schema_name FROM tenants WHERE schema_name = :schema"),
        {"schema": schema_name}
    )
    tenant_row = result.fetchone()

    if not tenant_row:
        # Create tenant schema
        await db.execute(
            text(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"')
        )
        # Register tenant
        tenant = Tenant(
            name=user_data.tenant_name,
            schema_name=schema_name
        )
        db.add(tenant)
        await db.flush()  # flush to get the tenant ID without committing
        tenant_id = str(tenant.id)
    else:
        tenant_id = str(tenant_row.id)

    # Switch to tenant schema to create user
    await db.execute(text(f'SET search_path TO "{schema_name}", public'))

    # Check if user already exists in this tenant
    result = await db.execute(
        text("SELECT id FROM users WHERE email = :email"),
        {"email": user_data.email}
    )
    if result.fetchone():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered in this tenant"
        )

    # Create the user
    user = User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password)
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    access_token = create_access_token(
        subject=user_data.email,
        tenant_id=tenant_id,
        schema_name=schema_name
    )
    refresh_token = create_refresh_token(
        subject=user_data.email,
        tenant_id=tenant_id
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )

@router.post("/login", response_model=TokenResponse)
async def login(
    user_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    # Find tenant by matching user email across tenants
    # In production you'd pass tenant identifier separately
    # For now we find the tenant from a tenant_name field
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Login requires tenant context — use /auth/login-tenant"
    )

@router.post("/login-tenant", response_model=TokenResponse)
async def login_with_tenant(
    tenant_name: str,
    user_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    schema_name = generate_schema_name(tenant_name)

    # Verify tenant exists
    result = await db.execute(
        text("SELECT id FROM tenants WHERE schema_name = :schema"),
        {"schema": schema_name}
    )
    tenant_row = result.fetchone()
    if not tenant_row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )

    tenant_id = str(tenant_row.id)

    # Switch to tenant schema
    await db.execute(text(f'SET search_path TO "{schema_name}", public'))

    # Find user
    result = await db.execute(
        text("SELECT id, email, hashed_password FROM users WHERE email = :email"),
        {"email": user_data.email}
    )
    user_row = result.fetchone()

    if not user_row or not verify_password(user_data.password, user_row.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    access_token = create_access_token(
        subject=user_data.email,
        tenant_id=tenant_id,
        schema_name=schema_name
    )
    refresh_token = create_refresh_token(
        subject=user_data.email,
        tenant_id=tenant_id
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    token_data: TokenRefresh,
    db: AsyncSession = Depends(get_db)
):
    payload = decode_token(token_data.refresh_token)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    # Get tenant schema from DB
    result = await db.execute(
        text("SELECT schema_name FROM tenants WHERE id = :id"),
        {"id": payload.get("tenant_id")}
    )
    tenant_row = result.fetchone()
    if not tenant_row:
        raise HTTPException(status_code=404, detail="Tenant not found")

    access_token = create_access_token(
        subject=payload.get("sub"),
        tenant_id=payload.get("tenant_id"),
        schema_name=tenant_row.schema_name
    )
    new_refresh_token = create_refresh_token(
        subject=payload.get("sub"),
        tenant_id=payload.get("tenant_id")
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token
    )