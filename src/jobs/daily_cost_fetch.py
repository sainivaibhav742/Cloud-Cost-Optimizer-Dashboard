import os
from datetime import datetime
from src.services.aws_cost_service import AWSCostService
from src.models.database import get_db
from src.models.cost_model import CloudCost

def fetch_and_store_daily_costs():
    """
    Job to fetch daily cost data from AWS and store in database.
    """
    print(f"[{datetime.now()}] Starting daily cost fetch job...")

    try:
        # Initialize AWS Cost Service
        cost_service = AWSCostService()

        # Fetch yesterday's costs
        cost_data = cost_service.get_yesterday_costs()

        if not cost_data:
            print("No cost data fetched from AWS")
            return

        # Store in database
        db = next(get_db())
        stored_count = 0

        for data in cost_data:
            # Check if record already exists to avoid duplicates
            existing = db.query(CloudCost).filter(
                CloudCost.date == datetime.strptime(data['date'], '%Y-%m-%d').date(),
                CloudCost.service == data['service'],
                CloudCost.account_id == data['account_id']
            ).first()

            if not existing:
                cost_entry = CloudCost(
                    date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
                    service=data['service'],
                    cost=data['cost'],
                    usage=data['usage'],
                    account_id=data['account_id']
                )
                db.add(cost_entry)
                stored_count += 1

        db.commit()
        print(f"Successfully stored {stored_count} new cost records")

    except Exception as e:
        print(f"Error in daily cost fetch job: {e}")
        raise

if __name__ == "__main__":
    fetch_and_store_daily_costs()
