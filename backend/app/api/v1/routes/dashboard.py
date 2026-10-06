from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from backend.app.db.database import get_db
from backend.app.schemas.dashboard import DashboardResponse
from backend.app.services.dashboard_service import DashboardService
router=APIRouter(prefix='/dashboard',tags=['Dashboard'])
@router.get('/business/{slug}',response_model=DashboardResponse)
def get_business_dashboard(slug:str,days:int|None=Query(None,ge=1,le=365),db:Session=Depends(get_db)):
    try:return DashboardService.get_business_dashboard(db,slug,days)
    except ValueError as e:
        message=str(e); raise HTTPException(status_code=404 if message=='Business not found' else 409,detail=message)
