from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.request import schemas
from app.request import crud
from app.user import get_current_user
from app.db import db_helper
from app.request.models import UserRequest
import pickle

router = APIRouter()


@router.post("/create", response_model=schemas.RequestOut)
async def create_user_request(
        req_in: schemas.RequestCreate,
        db: AsyncSession = Depends(db_helper.scoped_session_dependency),
        current_user=Depends(get_current_user)
):
    """
    Endpoint for creating a new R-tree request.
    """
    db_request = await crud.create_request(db, user_id=current_user.id, req_in=req_in)
    return db_request


@router.delete("/{request_id}")
async def delete_request(
        request_id: int,
        db: AsyncSession = Depends(db_helper.scoped_session_dependency),
        current_user=Depends(get_current_user)
):
    """
    Endpoint for deleting a specific R-tree request.
    """
    try:
        result = await crud.delete_request_crud(db, current_user.id, request_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/history", response_model=list[schemas.RequestOut])
async def get_request_history(
        db: AsyncSession = Depends(db_helper.scoped_session_dependency),
        current_user=Depends(get_current_user)
):
    """
    Endpoint to retrieve the list of R-tree requests for the current user.
    """
    requests = await crud.get_requests_by_user(db, user_id=current_user.id)
    return requests


@router.get("/{request_id}", response_model=schemas.RequestOutFull)
async def get_request_detail(
        request_id: int,
        db: AsyncSession = Depends(db_helper.scoped_session_dependency),
        current_user=Depends(get_current_user)
):
    """
    Endpoint to get detailed information about a specific R-tree request,
    including 2D visualization if applicable.
    """
    try:
        detail = await crud.get_request_detail_crud(db, current_user.id, request_id)
        return detail
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{request_id}/download")
async def download_request(
        request_id: int,
        db: AsyncSession = Depends(db_helper.scoped_session_dependency),
        current_user=Depends(get_current_user)
):
    """
    Endpoint for downloading the serialized R-tree file.
    """
    db_req = await db.get(UserRequest, request_id)
    if not db_req or db_req.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Request not found")
    if not db_req.r_tree_data:
        raise HTTPException(status_code=404, detail="No tree data available")
    import io
    from fastapi.responses import StreamingResponse
    file_like = io.BytesIO(db_req.r_tree_data)
    headers = {
        "Content-Disposition": f"attachment; filename=r_tree_{db_req.id}.pkl"
    }
    return StreamingResponse(file_like, media_type="application/octet-stream", headers=headers)


@router.post("/import", response_model=schemas.RequestOut)
async def import_tree(
        file: UploadFile = File(...),
        db: AsyncSession = Depends(db_helper.scoped_session_dependency),
        current_user=Depends(get_current_user)
):
    """
    Endpoint for importing an R-tree from a file.
    """
    file_data = await file.read()
    try:
        pickle.loads(file_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid tree file")
    db_request = await crud.import_request(db, user_id=current_user.id, file_data=file_data)
    return db_request


@router.post("/{request_id}/range_query")
async def range_query_endpoint(
        request_id: int,
        payload: dict,
        db: AsyncSession = Depends(db_helper.scoped_session_dependency),
        current_user=Depends(get_current_user)
):
    """
    Endpoint to process a range query on a specific R-tree request.
    """
    try:
        result = await crud.range_query_request(db, current_user.id, request_id, payload)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{request_id}/knn_query")
async def knn_query_endpoint(
        request_id: int,
        payload: dict,
        db: AsyncSession = Depends(db_helper.scoped_session_dependency),
        current_user=Depends(get_current_user)
):
    """
    Endpoint to process a k-NN query on a specific R-tree request.
    """
    try:
        result = await crud.knn_query_request(db, current_user.id, request_id, payload)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
