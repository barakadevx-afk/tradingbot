"""AI model management endpoints."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_user, get_current_superuser
from app.models.user import User
from app.repositories.system import ModelRepository
from app.schemas.system import ModelResponse
from app.services.ai_engine import AIEngine

router = APIRouter()


@router.get("", response_model=List[ModelResponse])
async def get_models(
    model_type: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    is_approved: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[ModelResponse]:
    """Get all AI models."""
    model_repo = ModelRepository(db)
    models = await model_repo.get_models(
        model_type=model_type,
        is_active=is_active,
        is_approved=is_approved,
    )
    return models


@router.get("/active", response_model=ModelResponse)
async def get_active_model(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ModelResponse:
    """Get the currently active model."""
    model_repo = ModelRepository(db)
    model = await model_repo.get_active_model()
    if not model:
        raise HTTPException(status_code=404, detail="No active model found")
    return model


@router.get("/{model_id}", response_model=ModelResponse)
async def get_model(
    model_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ModelResponse:
    """Get a specific model by ID."""
    model_repo = ModelRepository(db)
    model = await model_repo.get_by_id(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return model


@router.post("/train")
async def train_model(
    model_type: str = Query(..., description="Model type to train"),
    symbol: str = Query(..., description="Symbol to train on"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
) -> dict:
    """Train a new AI model."""
    ai_engine = AIEngine(db)
    result = await ai_engine.train_model(
        model_type=model_type,
        symbol=symbol,
    )
    return result


@router.post("/{model_id}/approve")
async def approve_model(
    model_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
) -> ModelResponse:
    """Approve a model for production use."""
    model_repo = ModelRepository(db)
    model = await model_repo.get_by_id(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    # Deactivate all other models of same type
    await model_repo.deactivate_all_by_type(model.model_type)

    # Approve and activate this model
    updated = await model_repo.update(
        model_id,
        {
            "is_approved": True,
            "is_active": True,
            "approved_by": current_user.email,
            "approved_at": "now()",
        },
    )
    return updated


@router.post("/{model_id}/activate")
async def activate_model(
    model_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
) -> ModelResponse:
    """Activate a model for predictions."""
    model_repo = ModelRepository(db)
    model = await model_repo.get_by_id(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    # Deactivate all other models of same type
    await model_repo.deactivate_all_by_type(model.model_type)

    updated = await model_repo.update(model_id, {"is_active": True})
    return updated


@router.post("/{model_id}/deactivate")
async def deactivate_model(
    model_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
) -> ModelResponse:
    """Deactivate a model."""
    model_repo = ModelRepository(db)
    model = await model_repo.get_by_id(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    updated = await model_repo.update(model_id, {"is_active": False})
    return updated


@router.delete("/{model_id}")
async def delete_model(
    model_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
) -> dict:
    """Delete a model."""
    model_repo = ModelRepository(db)
    model = await model_repo.get_by_id(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    await model_repo.delete(model_id)
    return {"message": "Model deleted successfully"}
