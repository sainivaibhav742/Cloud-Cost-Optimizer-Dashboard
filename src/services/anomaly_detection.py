from typing import List, Dict, Any
from sqlalchemy.orm import Session
from src.models.cost_model import CloudCost
from datetime import datetime, timedelta

class AnomalyDetector:
    def __init__(self, db: Session):
        self.db = db

    def detect_idle_instances(self) -> List[Dict[str, Any]]:
        """
        Detect EC2 instances with low CPU usage over the last 7 days.
        """
        seven_days_ago = datetime.now().date() - timedelta(days=7)

        # Query for EC2 costs with low usage (assuming usage < 5% indicates idle)
        idle_instances = self.db.query(CloudCost).filter(
            CloudCost.service.like('%EC2%'),
            CloudCost.date >= seven_days_ago,
            CloudCost.usage < 5.0  # Assuming usage is in percentage or normalized
        ).all()

        recommendations = []
        for instance in idle_instances:
            recommendations.append({
                "type": "idle_ec2",
                "service": instance.service,
                "date": instance.date.isoformat(),
                "cost": instance.cost,
                "usage": instance.usage,
                "suggestion": "Stop or resize this idle EC2 instance",
                "potential_savings": instance.cost * 30  # Monthly estimate
            })

        return recommendations

    def detect_underused_rds(self) -> List[Dict[str, Any]]:
        """
        Detect RDS instances with low storage utilization.
        """
        recent_costs = self.db.query(CloudCost).filter(
            CloudCost.service.like('%RDS%'),
            CloudCost.date >= datetime.now().date() - timedelta(days=30)
        ).all()

        recommendations = []
        for cost in recent_costs:
            # Assuming usage < 10% indicates underutilization
            if cost.usage < 10.0:
                recommendations.append({
                    "type": "underused_rds",
                    "service": cost.service,
                    "date": cost.date.isoformat(),
                    "cost": cost.cost,
                    "usage": cost.usage,
                    "suggestion": f"Reduce RDS storage from current to {cost.usage * 0.5:.1f}% utilization",
                    "potential_savings": cost.cost * 0.3  # Estimate 30% savings
                })

        return recommendations

    def detect_cost_spikes(self) -> List[Dict[str, Any]]:
        """
        Detect significant cost increases compared to previous periods.
        """
        thirty_days_ago = datetime.now().date() - timedelta(days=30)
        sixty_days_ago = datetime.now().date() - timedelta(days=60)

        recent_costs = self.db.query(CloudCost).filter(
            CloudCost.date >= thirty_days_ago
        ).all()

        previous_costs = self.db.query(CloudCost).filter(
            CloudCost.date.between(sixty_days_ago, thirty_days_ago)
        ).all()

        # Group by service
        recent_by_service = {}
        previous_by_service = {}

        for cost in recent_costs:
            if cost.service not in recent_by_service:
                recent_by_service[cost.service] = 0
            recent_by_service[cost.service] += cost.cost

        for cost in previous_costs:
            if cost.service not in previous_by_service:
                previous_by_service[cost.service] = 0
            previous_by_service[cost.service] += cost.cost

        recommendations = []
        for service, recent_total in recent_by_service.items():
            previous_total = previous_by_service.get(service, 0)
            if previous_total > 0:
                increase_percent = ((recent_total - previous_total) / previous_total) * 100
                if increase_percent > 20:  # 20% increase threshold
                    recommendations.append({
                        "type": "cost_spike",
                        "service": service,
                        "recent_cost": recent_total,
                        "previous_cost": previous_total,
                        "increase_percent": increase_percent,
                        "suggestion": f"Investigate {service} cost increase of {increase_percent:.1f}%",
                        "potential_savings": 0  # Investigation needed
                    })

        return recommendations

    def get_all_recommendations(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get all types of recommendations.
        """
        return {
            "idle_instances": self.detect_idle_instances(),
            "underused_rds": self.detect_underused_rds(),
            "cost_spikes": self.detect_cost_spikes()
        }
