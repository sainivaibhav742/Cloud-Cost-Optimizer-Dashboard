"""
Demo data service for populating database with sample cost data.
Useful for development and demonstration purposes.
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from src.models.cost_model import CloudCost
from src.models.user_model import User
from src.services.auth_service import AuthService
import random
import logging

logger = logging.getLogger(__name__)


class DemoDataService:
    """Service for generating demo cost data."""

    SERVICES = [
        "Amazon EC2", "Amazon S3", "Amazon RDS", "Amazon Lambda",
        "Amazon CloudFront", "Amazon DynamoDB", "Amazon ECS",
        "Amazon EKS", "Amazon ElastiCache", "AWS Data Transfer"
    ]

    @staticmethod
    def create_demo_user(db: Session, username: str = "demo", 
                         email: str = "demo@example.com", 
                         password: str = "demo123") -> User:
        """Create a demo user account."""
        # Check if user already exists
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            logger.info(f"Demo user '{username}' already exists")
            return existing_user

        user = AuthService.create_user(db, username, email, password)
        logger.info(f"Created demo user: {username}")
        return user

    @staticmethod
    def generate_cost_data(db: Session, days: int = 90, account_id: str = "123456789012"):
        """
        Generate demo cost data for the specified number of days.
        
        Args:
            db: Database session
            days: Number of days of historical data to generate
            account_id: AWS account ID for the demo data
        """
        # Check if data already exists
        existing_count = db.query(CloudCost).count()
        if existing_count > 0:
            logger.info(f"Database already has {existing_count} cost records. Skipping demo data generation.")
            return

        logger.info(f"Generating {days} days of demo cost data...")
        
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)

        cost_records = []
        
        for day_offset in range(days):
            current_date = start_date + timedelta(days=day_offset)
            
            # Add some variance and trends
            day_factor = 1 + (day_offset / days) * 0.3  # Gradual increase over time
            day_variance = random.uniform(0.8, 1.2)  # Daily random variance
            
            for service in DemoDataService.SERVICES:
                # Base cost varies by service
                base_cost = DemoDataService._get_base_cost_for_service(service)
                
                # Apply factors
                daily_cost = base_cost * day_factor * day_variance
                
                # Add occasional spikes for cost anomaly detection
                if random.random() < 0.05:  # 5% chance of spike
                    daily_cost *= random.uniform(2, 4)
                
                # Generate usage (normalized to percentage)
                usage = random.uniform(5, 95)
                
                # Some services should have low usage (for idle detection)
                if service == "Amazon EC2" and random.random() < 0.3:
                    usage = random.uniform(0.5, 5)
                
                cost_record = CloudCost(
                    date=current_date,
                    service=service,
                    cost=round(daily_cost, 2),
                    usage=round(usage, 2),
                    account_id=account_id
                )
                cost_records.append(cost_record)
        
        # Bulk insert for efficiency
        db.bulk_save_objects(cost_records)
        db.commit()
        
        logger.info(f"Successfully generated {len(cost_records)} cost records")

    @staticmethod
    def _get_base_cost_for_service(service: str) -> float:
        """Get base daily cost for a service."""
        base_costs = {
            "Amazon EC2": 150.0,
            "Amazon S3": 25.0,
            "Amazon RDS": 80.0,
            "Amazon Lambda": 15.0,
            "Amazon CloudFront": 30.0,
            "Amazon DynamoDB": 20.0,
            "Amazon ECS": 45.0,
            "Amazon EKS": 60.0,
            "Amazon ElastiCache": 35.0,
            "AWS Data Transfer": 40.0
        }
        return base_costs.get(service, 10.0)

    @staticmethod
    def seed_all_demo_data(db: Session):
        """Seed database with all demo data including user and costs."""
        logger.info("Seeding database with demo data...")
        
        # Create demo user
        DemoDataService.create_demo_user(db)
        
        # Generate cost data
        DemoDataService.generate_cost_data(db)
        
        logger.info("Demo data seeding completed successfully")


def seed_demo_data():
    """Standalone function to seed demo data."""
    from src.models.database import SessionLocal
    
    db = SessionLocal()
    try:
        DemoDataService.seed_all_demo_data(db)
    finally:
        db.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seed_demo_data()
