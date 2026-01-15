from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.sql import func
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import logging
import time

from api.database.connection import get_database, AsyncSessionLocal
from api.models.image_stack import ImageStack
from api.models.analysis_result import AnalysisResult
from core.processing.analyzer import ZStackAnalyzer
from api.websocket.manager import connection_manager
from api.websocket.events import (
    ProcessingStarted,
    ProcessingProgress,
    ProcessingComplete,
    ProcessingFailed,
    ValidationRequired,
)

router = APIRouter()
logger = logging.getLogger(__name__)

class AnalysisRequest(BaseModel):
    algorithm: str
    parameters: Optional[Dict[str, Any]] = {}

class ValidationRequest(BaseModel):
    validated: bool
    notes: Optional[str] = None
    validator_id: Optional[str] = None

@router.post("/{image_id}/analyze")
async def analyze_image(
    image_id: str,
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_database)
):
    # Check if image exists
    result = await db.execute(
        select(ImageStack).where(ImageStack.id == image_id)
    )
    image_stack = result.scalar_one_or_none()
    
    if not image_stack:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image stack not found"
        )
    
    # Update processing status
    image_stack.processing_status = "processing"
    await db.commit()
    
    # Start analysis in background
    background_tasks.add_task(
        run_analysis,
        image_id,
        request.algorithm,
        request.parameters
    )
    
    return {
        "message": "Analysis started",
        "image_id": image_id,
        "algorithm": request.algorithm,
        "status": "processing"
    }

async def run_analysis(
    image_id: str,
    algorithm: str,
    parameters: Dict[str, Any],
    session_id: Optional[str] = None
):
    start_time = time.time()

    async with AsyncSessionLocal() as db:
        try:
            # Get image stack
            result = await db.execute(
                select(ImageStack).where(ImageStack.id == image_id)
            )
            image_stack = result.scalar_one_or_none()

            if not image_stack:
                logger.error(f"Image stack {image_id} not found during analysis")
                return

            # Emit processing started event
            started_event = ProcessingStarted(
                image_id=image_id,
                algorithm=algorithm,
                estimated_time_seconds=5.0,  # Estimated based on algorithm
                parameters=parameters,
                session_id=session_id,
            )
            if session_id:
                await connection_manager.send_to_session(session_id, started_event)
            else:
                await connection_manager.broadcast(started_event)

            # Create progress callback for real-time updates
            async def progress_callback(progress: float, step: str, eta: Optional[float]):
                elapsed = time.time() - start_time
                progress_event = ProcessingProgress(
                    image_id=image_id,
                    progress=progress,
                    current_step=step,
                    eta_seconds=eta if eta is not None else max(0, 5.0 - elapsed),
                    session_id=session_id,
                )
                if session_id:
                    await connection_manager.send_to_session(session_id, progress_event)
                else:
                    await connection_manager.broadcast(progress_event)

            # Run analysis with progress callback
            analyzer = ZStackAnalyzer(progress_callback=progress_callback)
            analysis_result = await analyzer.analyze(
                image_stack.file_path,
                algorithm,
                parameters
            )

            # Save results
            db_result = AnalysisResult(
                stack_id=image_id,
                algorithm_name=algorithm,
                algorithm_version=analysis_result.get("version", "1.0.0"),
                gpu_device=analysis_result.get("gpu_device"),
                processing_time_ms=analysis_result.get("processing_time_ms", 0),
                results=analysis_result.get("results", {}),
                confidence_score=analysis_result.get("confidence_score")
            )

            db.add(db_result)
            await db.flush()  # Get the ID

            # Update image stack status
            image_stack.processing_status = "completed"

            await db.commit()

            processing_time = time.time() - start_time

            # Emit processing complete event
            complete_event = ProcessingComplete(
                image_id=image_id,
                result_id=str(db_result.id),
                summary=analysis_result.get("results", {}),
                processing_time_seconds=processing_time,
                confidence_score=analysis_result.get("confidence_score"),
                session_id=session_id,
            )
            if session_id:
                await connection_manager.send_to_session(session_id, complete_event)
            else:
                await connection_manager.broadcast(complete_event)

            # Check if validation is required (low confidence)
            confidence = analysis_result.get("confidence_score", 1.0)
            if confidence and confidence < 0.7:
                validation_event = ValidationRequired(
                    result_id=str(db_result.id),
                    confidence=confidence,
                    reason="Confidence score below threshold (0.7)",
                    suggested_actions=["Review segmentation boundaries", "Adjust algorithm parameters"],
                    session_id=session_id,
                )
                if session_id:
                    await connection_manager.send_to_session(session_id, validation_event)
                else:
                    await connection_manager.broadcast(validation_event)

            logger.info(f"Analysis completed for image {image_id}")

        except Exception as e:
            logger.error(f"Analysis failed for image {image_id}: {e}")

            # Emit processing failed event
            failed_event = ProcessingFailed(
                image_id=image_id,
                error=str(e),
                error_code="ANALYSIS_ERROR",
                retry_available=True,
                session_id=session_id,
            )
            if session_id:
                await connection_manager.send_to_session(session_id, failed_event)
            else:
                await connection_manager.broadcast(failed_event)

            # Update status to failed
            result = await db.execute(
                select(ImageStack).where(ImageStack.id == image_id)
            )
            image_stack = result.scalar_one_or_none()
            if image_stack:
                image_stack.processing_status = "failed"
                await db.commit()

@router.get("/{image_id}/results", response_model=List[dict])
async def get_analysis_results(
    image_id: str,
    db: AsyncSession = Depends(get_database)
):
    result = await db.execute(
        select(AnalysisResult).where(AnalysisResult.stack_id == image_id)
    )
    results = result.scalars().all()
    return [result.to_dict() for result in results]

@router.get("/results/{result_id}", response_model=dict)
async def get_analysis_result(
    result_id: str,
    db: AsyncSession = Depends(get_database)
):
    result = await db.execute(
        select(AnalysisResult).where(AnalysisResult.id == result_id)
    )
    analysis_result = result.scalar_one_or_none()
    
    if not analysis_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis result not found"
        )
    
    return analysis_result.to_dict()

@router.put("/results/{result_id}/validate")
async def validate_result(
    result_id: str,
    request: ValidationRequest,
    db: AsyncSession = Depends(get_database)
):
    result = await db.execute(
        select(AnalysisResult).where(AnalysisResult.id == result_id)
    )
    analysis_result = result.scalar_one_or_none()
    
    if not analysis_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis result not found"
        )
    
    # Update validation status
    analysis_result.human_validated = request.validated
    analysis_result.validation_notes = request.notes
    analysis_result.validator_id = request.validator_id
    analysis_result.validation_timestamp = func.now()
    
    await db.commit()
    
    return {
        "message": "Validation updated successfully",
        "result_id": result_id,
        "validated": request.validated
    }