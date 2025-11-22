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
    return [{"id": c.id, "date": str(c.date), "service": c.service, "cost": c.cost, "usage": c.usage, "account_id": c.account_id} for c in costs]

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

@router.post("/budget/simulate")
def simulate_budget(budget_amount: float, months: int = 12, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Simulate budget impact over time based on current spending patterns
    """
    # Get user's cost data
    costs = db.query(CloudCost).all()

    if not costs:
        return {"error": "No cost data available for simulation"}

    # Calculate average monthly spend
    monthly_spends = {}
    for cost in costs:
        month_key = cost.date.strftime("%Y-%m")
        if month_key not in monthly_spends:
            monthly_spends[month_key] = 0
        monthly_spends[month_key] += cost.cost

    avg_monthly = sum(monthly_spends.values()) / len(monthly_spends) if monthly_spends else 0

    # Simulate budget over months
    simulation = []
    remaining_budget = budget_amount

    for month in range(1, months + 1):
        monthly_cost = avg_monthly  # Could add trend analysis here
        remaining_budget -= monthly_cost

        simulation.append({
            "month": month,
            "projected_cost": round(monthly_cost, 2),
            "remaining_budget": round(max(0, remaining_budget), 2),
            "budget_exceeded": remaining_budget < 0
        })

        if remaining_budget <= 0:
            break

    return {
        "budget_amount": budget_amount,
        "average_monthly_spend": round(avg_monthly, 2),
        "simulation": simulation,
        "months_until_depletion": len(simulation) if simulation and simulation[-1]["remaining_budget"] <= 0 else None
    }

@router.get("/ai-recommendations")
def get_ai_recommendations(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get AI-powered cost optimization recommendations using OpenAI
    """
    try:
        from src.services.ai_recommendations import AIRecommendationService

        ai_service = AIRecommendationService()
        recommendations = ai_service.generate_ai_recommendations(db)

        return {"recommendations": recommendations}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/monitoring/health")
def get_system_health(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get system health and performance metrics
    """
    try:
        from src.services.monitoring_service import monitoring

        health_data = monitoring.get_system_health(db)
        return health_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/monitoring/performance")
def get_performance_metrics(current_user = Depends(get_current_user)):
    """
    Get API performance metrics
    """
    try:
        from src.services.monitoring_service import monitoring

        return monitoring.get_performance_report()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/monitoring/savings")
def get_cost_savings_report(days: int = 30, current_user = Depends(get_current_user)):
    """
    Get cost savings report for the specified period
    """
    try:
        from src.services.monitoring_service import monitoring

        return monitoring.calculate_total_savings(days)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/demo/seed")
def seed_demo_data(db: Session = Depends(get_db)):
    """
    Seed database with demo data for development/testing.
    WARNING: Only use in development environments!
    """
    import os
    
    # Only allow seeding if explicitly enabled and in development
    environment = os.getenv("ENVIRONMENT", "").lower()
    enable_demo = os.getenv("ENABLE_DEMO_MODE", "false").lower() == "true"
    
    if environment == "production" or not enable_demo:
        raise HTTPException(
            status_code=403, 
            detail="Demo data seeding only allowed when ENABLE_DEMO_MODE=true and ENVIRONMENT=development"
        )
    
    try:
        from src.services.demo_data_service import DemoDataService
        
        DemoDataService.seed_all_demo_data(db)
        
        return {
            "message": "Demo data seeded successfully",
            "demo_user": {"username": "demo", "password": "demo123"}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/costs/summary")
def get_cost_summary(days: int = 30, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get cost summary statistics for the specified period
    """
    try:
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now().date() - timedelta(days=days)
        costs = db.query(CloudCost).filter(CloudCost.date >= cutoff_date).all()
        
        if not costs:
            return {
                "total_cost": 0,
                "daily_average": 0,
                "service_breakdown": {},
                "period_days": days
            }
        
        # Calculate statistics
        total_cost = sum(cost.cost for cost in costs)
        service_breakdown = {}
        
        for cost in costs:
            if cost.service not in service_breakdown:
                service_breakdown[cost.service] = 0
            service_breakdown[cost.service] += cost.cost
        
        # Sort by cost descending
        service_breakdown = dict(sorted(service_breakdown.items(), key=lambda x: x[1], reverse=True))
        
        return {
            "total_cost": round(total_cost, 2),
            "daily_average": round(total_cost / days, 2),
            "service_breakdown": {k: round(v, 2) for k, v in service_breakdown.items()},
            "period_days": days,
            "total_records": len(costs)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
