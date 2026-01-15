from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from pydantic import BaseModel
import logging

from api.database.connection import get_database
from api.models.analysis_result import AnalysisResult

router = APIRouter()
logger = logging.getLogger(__name__)

class ValidationStats(BaseModel):
    total_results: int
    validated_results: int
    pending_validation: int
    validation_rate: float

@router.get("/queue", response_model=List[dict])
async def get_validation_queue(
    limit: int = 50,
    algorithm: Optional[str] = None,
    db: AsyncSession = Depends(get_database)
):
    query = select(AnalysisResult).where(
        AnalysisResult.human_validated == False
    )
    
    if algorithm:
        query = query.where(AnalysisResult.algorithm_name == algorithm)
    
    query = query.limit(limit).order_by(AnalysisResult.created_at.desc())
    
    result = await db.execute(query)
    pending_results = result.scalars().all()
    
    return [result.to_dict() for result in pending_results]

@router.get("/stats", response_model=ValidationStats)
async def get_validation_stats(
    algorithm: Optional[str] = None,
    db: AsyncSession = Depends(get_database)
):
    base_query = select(AnalysisResult)
    
    if algorithm:
        base_query = base_query.where(AnalysisResult.algorithm_name == algorithm)
    
    # Total results
    total_result = await db.execute(base_query)
    total_results = len(total_result.scalars().all())
    
    # Validated results
    validated_query = base_query.where(AnalysisResult.human_validated == True)
    validated_result = await db.execute(validated_query)
    validated_results = len(validated_result.scalars().all())
    
    # Pending validation
    pending_validation = total_results - validated_results
    
    # Validation rate
    validation_rate = (validated_results / total_results * 100) if total_results > 0 else 0
    
    return ValidationStats(
        total_results=total_results,
        validated_results=validated_results,
        pending_validation=pending_validation,
        validation_rate=round(validation_rate, 2)
    )

@router.get("/algorithms", response_model=List[str])
async def get_algorithms_for_validation(
    db: AsyncSession = Depends(get_database)
):
    result = await db.execute(
        select(AnalysisResult.algorithm_name).distinct()
    )
    algorithms = [row[0] for row in result.fetchall()]
    return algorithms