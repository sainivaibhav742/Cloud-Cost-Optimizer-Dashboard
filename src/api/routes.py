from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from src.models.database import get_db
from src.models.cost_model import CloudCost
from src.services.aws_cost_service import AWSCostService
from src.api.auth_routes import get_current_user
from typing import List
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class CostResponse(BaseModel):
    id: int
    date: str
    service: str
    cost: float
    usage: float
    account_id: str

class CostData(BaseModel):
    date: str
    service: str
    cost: float
    usage: float
    account_id: str

@router.get("/")
def read_root():
    return {"message": "Cloud Cost Optimizer Dashboard API"}

@router.get("/health")
def health_check():
    return {"status": "healthy"}

@router.get("/costs/daily", response_model=List[CostResponse])
def get_daily_costs(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    costs = db.query(CloudCost).all()
    return costs

@router.post("/costs/fetch")
def fetch_costs(current_user = Depends(get_current_user)):
    """
    Fetch cost data from AWS and store in database.
    """
    try:
        service = AWSCostService()
        cost_data = service.get_yesterday_costs()

        if not cost_data:
            raise HTTPException(status_code=500, detail="Failed to fetch cost data from AWS")

        # Store in database
        db = next(get_db())
        for data in cost_data:
            cost_entry = CloudCost(
                date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
                service=data['service'],
                cost=data['cost'],
                usage=data['usage'],
                account_id=data['account_id']
            )
            db.add(cost_entry)
        db.commit()

        return {"message": f"Successfully fetched and stored {len(cost_data)} cost records"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recommendations")
def get_recommendations(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get cost optimization recommendations.
    """
    try:
        from src.services.anomaly_detection import AnomalyDetector

        detector = AnomalyDetector(db)
        recommendations = detector.get_all_recommendations()

        return recommendations

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
