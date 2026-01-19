"""
Export API Routes

This module provides API endpoints for exporting reports in PDF and DOCX formats.
"""

import logging
import io
import time
from typing import Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, status, BackgroundTasks, UploadFile
from pydantic import BaseModel, Field
from fastapi.responses import FileResponse, Response

from app.services.export_service import create_export_service

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/export", tags=["Export"])

# Initialize export service
export_service = create_export_service()


# Pydantic models
class ExportRequest(BaseModel):
    """Request model for report export"""
    task_id: str = Field(..., description="Task ID of the analysis")
    format: str = Field(default="pdf", description="Export format: pdf or docx")
    include_charts: bool = Field(default=False, description="Include evaluation charts")


class ExportResponse(BaseModel):
    """Response model for export request"""
    export_id: str
    status: str
    message: str
    download_url: Optional[str] = None


class ExportStatusResponse(BaseModel):
    """Response model for export status check"""
    export_id: str
    status: str
    message: str
    download_url: Optional[str] = None
    file_size: Optional[int] = None
    error: Optional[str] = None


# In-memory export storage (for production, use database)
export_store: Dict[str, Dict[str, Any]] = {}


def _generate_export_id() -> str:
    """Generate unique export ID"""
    import uuid
    timestamp = int(time.time())
    short_uuid = str(uuid.uuid4())[:8]
    return f"export-{timestamp}-{short_uuid}"


@router.post("/pdf", response_model=ExportResponse, status_code=status.HTTP_202_ACCEPTED)
async def export_pdf(
    request: ExportRequest,
    background_tasks: BackgroundTasks
):
    """
    Export report as PDF.
    
    This endpoint generates a PDF report and stores it for download.
    """
    try:
        # Generate export ID
        export_id = _generate_export_id()
        
        # Start export in background
        background_tasks.add_task(
            _generate_pdf_background,
            export_id,
            request.task_id,
            request.include_charts
        )
        
        return ExportResponse(
            export_id=export_id,
            status="queued",
            message="PDF export queued for generation"
        )
        
    except Exception as e:
        logger.error(f"Failed to queue PDF export: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to queue PDF export: {str(e)}"
        )


@router.post("/docx", response_model=ExportResponse, status_code=status.HTTP_202_ACCEPTED)
async def export_docx(
    request: ExportRequest,
    background_tasks: BackgroundTasks
):
    """
    Export report as DOCX.
    
    This endpoint generates a DOCX report and stores it for download.
    """
    try:
        # Generate export ID
        export_id = _generate_export_id()
        
        # Start export in background
        background_tasks.add_task(
            _generate_docx_background,
            export_id,
            request.task_id,
            request.include_charts
        )
        
        return ExportResponse(
            export_id=export_id,
            status="queued",
            message="DOCX export queued for generation"
        )
        
    except Exception as e:
        logger.error(f"Failed to queue DOCX export: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to queue DOCX export: {str(e)}"
        )


@router.get("/status/{export_id}", response_model=ExportStatusResponse)
async def get_export_status(export_id: str) -> ExportStatusResponse:
    """
    Get export status and download URL.
    
    Returns the current status of an export request.
    """
    try:
        export_data = export_store.get(export_id)
        
        if not export_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Export {export_id} not found"
            )
        
        return ExportStatusResponse(
            export_id=export_id,
            status=export_data.get("status", "unknown"),
            message=export_data.get("message", "Unknown status"),
            download_url=export_data.get("download_url"),
            file_size=export_data.get("file_size"),
            error=export_data.get("error")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get export status: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get export status: {str(e)}"
        )


@router.get("/download/{export_id}")
async def download_export_file(export_id: str):
    """
    Download exported file.
    
    Returns the generated file for download.
    """
    try:
        export_data = export_store.get(export_id)
        
        if not export_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Export {export_id} not found"
            )
        
        if export_data.get("status") != "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Export not ready. Status: {export_data.get('status')}"
            )
        
        if not export_data.get("file_path"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="File path not available"
            )
        
        # Determine content type
        if export_data.get("format") == "docx":
            media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            filename = export_data.get("file_name", f"report-{export_id}.docx")
        else:
            media_type = "application/pdf"
            filename = export_data.get("file_name", f"report-{export_id}.pdf")
        
        # Read file content
        try:
            with open(export_data["file_path"], 'rb') as f:
                content = f.read()
        except FileNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File not found"
            )
        
        # Return file response
        return FileResponse(
            content=content,
            media_type=media_type,
            filename=filename,
            headers={
                "Content-Disposition": f"attachment; filename=\"{filename}\""
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to download export file: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download file: {str(e)}"
        )


async def _generate_pdf_background(
    export_id: str,
    task_id: str,
    include_charts: bool
):
    """Background task to generate PDF export"""
    try:
        logger.info(f"Starting PDF export for task {task_id}, export_id: {export_id}")
        
        # Update status to processing
        export_store[export_id] = {
            "status": "processing",
            "message": "Generating PDF report...",
            "created_at": datetime.now().isoformat(),
        }
        
        # Import task storage to get analysis result
        from app.task_storage import get_task
        task = await get_task(task_id)
        
        if not task:
            export_store[export_id] = {
                "status": "failed",
                "message": "Task not found",
                "error": f"Task {task_id} not found"
            }
            return
        
        # Get analysis result from task output_data
        output_data = task.output_data or {}
        analysis_result = output_data.get("report", {})
        
        # For mock, create sample analysis result if not available
        if not analysis_result:
            analysis_result = {
                "executive_summary": "这是一个示例执行摘要",
                "risk_matrix": {
                    "legal_risk": "低",
                    "financial_risk": "中",
                    "operational_risk": "低",
                    "strategic_risk": "低"
                },
                "findings": [
                    {
                        "severity": "medium",
                        "category": "合规性",
                        "description": "劳动合同期限条款需要检查",
                        "suggestion": "建议确认是否符合劳动法规定"
                    }
                ],
                "suggestions": [
                    "建议 1: 检查劳动合同期限条款是否符合劳动法规定",
                    "建议 2: 添加明确的违约责任条款",
                    "建议 3: 完善保密条款细节"
                ]
            }
        
        # Generate PDF
        pdf_content = export_service.export_report(
            analysis_result=analysis_result,
            format="pdf",
            title=f"合同审查报告-{task_id}"
        )
        
        # Save to temporary file
        import os
        
        export_dir = "data/exports"
        os.makedirs(export_dir, exist_ok=True)
        
        file_path = os.path.join(export_dir, f"report-{task_id}.pdf")
        file_size = len(pdf_content)
        
        with open(file_path, 'wb') as f:
            f.write(pdf_content)
        
        # Update store
        export_store[export_id] = {
            "status": "completed",
            "message": "PDF report generated successfully",
            "file_path": file_path,
            "file_name": f"report-{task_id}.pdf",
            "format": "pdf",
            "file_size": file_size,
            "download_url": f"/export/download/{export_id}",
            "created_at": export_store[export_id]["created_at"],
            "updated_at": datetime.now().isoformat(),
        }
        
        # Clean up old exports (keep last 100)
        _cleanup_old_exports(export_dir, 100)
        
        logger.info(f"PDF export completed for task {task_id}, export_id {export_id}, file_size: {file_size} bytes")
        
    except Exception as e:
        logger.error(f"PDF export failed for task {task_id}: {e}", exc_info=True)
        export_store[export_id] = {
            "status": "failed",
            "message": f"PDF generation failed: {str(e)}",
            "error": str(e),
            "created_at": datetime.now().isoformat(),
        }


async def _generate_docx_background(
    export_id: str,
    task_id: str,
    include_charts: bool
):
    """Background task to generate DOCX export"""
    try:
        logger.info(f"Starting DOCX export for task {task_id}, export_id {export_id}")
        
        # Update status to processing
        export_store[export_id] = {
            "status": "processing",
            "message": "Generating DOCX report...",
            "created_at": datetime.now().isoformat(),
        }
        
        # Import task storage to get analysis result
        from app.task_storage import get_task
        task = await get_task(task_id)
        
        if not task:
            export_store[export_id] = {
                "status": "failed",
                "message": "Task not found",
                "error": f"Task {task_id} not found"
            }
            return
        
        # Get analysis result from task output_data
        output_data = task.output_data or {}
        analysis_result = output_data.get("report", {})
        
        # Generate DOCX
        docx_content = export_service.export_report(
            analysis_result=analysis_result,
            format="docx",
            title=f"合同审查报告-{task_id}"
        )
        
        # Save to temporary file
        import os
        
        export_dir = "data/exports"
        os.makedirs(export_dir, exist_ok=True)
        
        file_path = os.path.join(export_dir, f"report-{task_id}.docx")
        file_size = len(docx_content)
        
        with open(file_path, 'wb') as f:
            f.write(docx_content)
        
        # Update store
        export_store[export_id] = {
            "status": "completed",
            "message": "DOCX report generated successfully",
            "file_path": file_path,
            "file_name": f"report-{task_id}.docx",
            "format": "docx",
            "file_size": file_size,
            "download_url": f"/export/download/{export_id}",
            "created_at": export_store[export_id]["created_at"],
            "updated_at": datetime.now().isoformat(),
        }
        
        # Clean up old exports
        _cleanup_old_exports(export_dir, 100)
        
        logger.info(f"DOCX export completed for task {task_id}, export_id {export_id}, file_size: {file_size} bytes")
        
    except Exception as e:
        logger.error(f"DOCX export failed for task {task_id}: {e}", exc_info=True)
        export_store[export_id] = {
            "status": "failed",
            "message": f"DOCX generation failed: {str(e)}",
            "error": str(e),
            "created_at": export_store[export_id]["created_at"],
        }


def _cleanup_old_exports(export_dir: str, keep_count: int):
    """Clean up old export files"""
    try:
        import os
        from pathlib import Path
        
        export_path = Path(export_dir)
        if not export_path.exists():
            return
        
        files = sorted(
            export_path.glob("*.pdf") + export_path.glob("*.docx"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        # Remove old files beyond keep_count
        if len(files) > keep_count:
            for file_to_delete in files[keep_count:]:
                try:
                    file_to_delete.unlink()
                    logger.info(f"Deleted old export file: {file_to_delete.name}")
                except Exception as e:
                    logger.warning(f"Failed to delete old file {file_to_delete.name}: {e}")
        
    except Exception as e:
        logger.error(f"Failed to clean up old exports: {e}", exc_info=True)
