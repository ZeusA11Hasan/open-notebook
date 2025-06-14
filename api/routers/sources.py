import asyncio
from typing import List, Optional
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form
from loguru import logger

from api.models import SourceCreate, SourceUpdate, SourceResponse, SourceListResponse, AssetModel
from open_notebook.domain.notebook import Source, Notebook, Asset
from open_notebook.domain.transformation import Transformation
from open_notebook.exceptions import DatabaseOperationError, InvalidInputError
from open_notebook.graphs.source import source_graph

router = APIRouter()


@router.get("/sources", response_model=List[SourceListResponse])
async def get_sources(notebook_id: Optional[str] = Query(None, description="Filter by notebook ID")):
    """Get all sources with optional notebook filtering."""
    try:
        if notebook_id:
            # Get sources for a specific notebook
            notebook = Notebook.get(notebook_id)
            if not notebook:
                raise HTTPException(status_code=404, detail="Notebook not found")
            sources = notebook.sources
        else:
            # Get all sources
            sources = Source.get_all(order_by="updated desc")
        
        return [
            SourceListResponse(
                id=source.id,
                title=source.title,
                topics=source.topics or [],
                asset=AssetModel(
                    file_path=source.asset.file_path if source.asset else None,
                    url=source.asset.url if source.asset else None
                ) if source.asset else None,
                embedded_chunks=source.embedded_chunks,
                insights_count=len(source.insights),
                created=str(source.created),
                updated=str(source.updated),
            )
            for source in sources
        ]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching sources: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching sources: {str(e)}")


@router.post("/sources", response_model=SourceResponse)
async def create_source(source_data: SourceCreate):
    """Create a new source."""
    try:
        # Verify notebook exists
        notebook = Notebook.get(source_data.notebook_id)
        if not notebook:
            raise HTTPException(status_code=404, detail="Notebook not found")
        
        # Prepare content_state for source_graph
        content_state = {}
        
        if source_data.type == "link":
            if not source_data.url:
                raise HTTPException(status_code=400, detail="URL is required for link type")
            content_state["url"] = source_data.url
        elif source_data.type == "upload":
            if not source_data.file_path:
                raise HTTPException(status_code=400, detail="File path is required for upload type")
            content_state["file_path"] = source_data.file_path
            content_state["delete_source"] = source_data.delete_source
        elif source_data.type == "text":
            if not source_data.content:
                raise HTTPException(status_code=400, detail="Content is required for text type")
            content_state["content"] = source_data.content
        else:
            raise HTTPException(status_code=400, detail="Invalid source type. Must be link, upload, or text")
        
        # Get transformations to apply
        transformations = []
        if source_data.transformations:
            for trans_id in source_data.transformations:
                transformation = Transformation.get(trans_id)
                if not transformation:
                    raise HTTPException(status_code=404, detail=f"Transformation {trans_id} not found")
                transformations.append(transformation)
        
        # Process source using the source_graph
        result = await source_graph.ainvoke({
            "content_state": content_state,
            "notebook_id": source_data.notebook_id,
            "apply_transformations": transformations,
            "embed": source_data.embed,
        })
        
        source = result["source"]
        
        return SourceResponse(
            id=source.id,
            title=source.title,
            topics=source.topics or [],
            asset=AssetModel(
                file_path=source.asset.file_path if source.asset else None,
                url=source.asset.url if source.asset else None
            ) if source.asset else None,
            full_text=source.full_text,
            embedded_chunks=source.embedded_chunks,
            created=str(source.created),
            updated=str(source.updated),
        )
    except HTTPException:
        raise
    except InvalidInputError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating source: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating source: {str(e)}")


@router.get("/sources/{source_id}", response_model=SourceResponse)
async def get_source(source_id: str):
    """Get a specific source by ID."""
    try:
        source = Source.get(source_id)
        if not source:
            raise HTTPException(status_code=404, detail="Source not found")
        
        return SourceResponse(
            id=source.id,
            title=source.title,
            topics=source.topics or [],
            asset=AssetModel(
                file_path=source.asset.file_path if source.asset else None,
                url=source.asset.url if source.asset else None
            ) if source.asset else None,
            full_text=source.full_text,
            embedded_chunks=source.embedded_chunks,
            created=str(source.created),
            updated=str(source.updated),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching source {source_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching source: {str(e)}")


@router.put("/sources/{source_id}", response_model=SourceResponse)
async def update_source(source_id: str, source_update: SourceUpdate):
    """Update a source."""
    try:
        source = Source.get(source_id)
        if not source:
            raise HTTPException(status_code=404, detail="Source not found")
        
        # Update only provided fields
        if source_update.title is not None:
            source.title = source_update.title
        if source_update.topics is not None:
            source.topics = source_update.topics
        
        source.save()
        
        return SourceResponse(
            id=source.id,
            title=source.title,
            topics=source.topics or [],
            asset=AssetModel(
                file_path=source.asset.file_path if source.asset else None,
                url=source.asset.url if source.asset else None
            ) if source.asset else None,
            full_text=source.full_text,
            embedded_chunks=source.embedded_chunks,
            created=str(source.created),
            updated=str(source.updated),
        )
    except HTTPException:
        raise
    except InvalidInputError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating source {source_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating source: {str(e)}")


@router.delete("/sources/{source_id}")
async def delete_source(source_id: str):
    """Delete a source."""
    try:
        source = Source.get(source_id)
        if not source:
            raise HTTPException(status_code=404, detail="Source not found")
        
        source.delete()
        
        return {"message": "Source deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting source {source_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting source: {str(e)}")