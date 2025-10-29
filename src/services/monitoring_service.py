import time
import logging
from typing import Dict, List, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from src.models.database import get_db
from src.models.cost_model import CloudCost

logger = logging.getLogger(__name__)

class MonitoringService:
    def __init__(self):
        self.performance_metrics = {}
        self.cost_savings_log = []

    def log_api_performance(self, endpoint: str, method: str, response_time: float, status_code: int):
        """
        Log API endpoint performance metrics
        """
        if endpoint not in self.performance_metrics:
            self.performance_metrics[endpoint] = {
                'calls': 0,
                'total_time': 0,
                'avg_time': 0,
                'status_codes': {},
                'last_called': None
            }

        metrics = self.performance_metrics[endpoint]
        metrics['calls'] += 1
        metrics['total_time'] += response_time
        metrics['avg_time'] = metrics['total_time'] / metrics['calls']
        metrics['last_called'] = datetime.now()

        if status_code not in metrics['status_codes']:
            metrics['status_codes'][status_code] = 0
        metrics['status_codes'][status_code] += 1

        logger.info(f"API Performance - {method} {endpoint}: {response_time:.3f}s, Status: {status_code}")

    def get_performance_report(self) -> Dict[str, Any]:
        """
        Generate performance report
        """
        return {
            'endpoints': self.performance_metrics,
            'total_calls': sum(m['calls'] for m in self.performance_metrics.values()),
            'generated_at': datetime.now().isoformat()
        }

    def track_cost_savings(self, recommendation_type: str, potential_savings: float, implemented: bool = False):
        """
        Track cost savings from recommendations
        """
        entry = {
            'timestamp': datetime.now(),
            'recommendation_type': recommendation_type,
            'potential_savings': potential_savings,
            'implemented': implemented,
            'actual_savings': potential_savings if implemented else 0
        }

        self.cost_savings_log.append(entry)

        if implemented:
            logger.info(f"Cost Savings Tracked - {recommendation_type}: ${potential_savings:.2f} saved")
        else:
            logger.info(f"Recommendation Generated - {recommendation_type}: Potential savings ${potential_savings:.2f}")

    def calculate_total_savings(self, days: int = 30) -> Dict[str, Any]:
        """
        Calculate total cost savings over the specified period
        """
        cutoff_date = datetime.now() - timedelta(days=days)

        # Filter savings log for the period
        period_savings = [entry for entry in self.cost_savings_log if entry['timestamp'] >= cutoff_date]

        total_potential = sum(entry['potential_savings'] for entry in period_savings)
        total_actual = sum(entry['actual_savings'] for entry in period_savings)
        savings_rate = (total_actual / total_potential * 100) if total_potential > 0 else 0

        # Group by recommendation type
        savings_by_type = {}
        for entry in period_savings:
            rec_type = entry['recommendation_type']
            if rec_type not in savings_by_type:
                savings_by_type[rec_type] = {'potential': 0, 'actual': 0, 'count': 0}
            savings_by_type[rec_type]['potential'] += entry['potential_savings']
            savings_by_type[rec_type]['actual'] += entry['actual_savings']
            savings_by_type[rec_type]['count'] += 1

        return {
            'period_days': days,
            'total_potential_savings': round(total_potential, 2),
            'total_actual_savings': round(total_actual, 2),
            'savings_rate_percent': round(savings_rate, 2),
            'savings_by_type': savings_by_type,
            'total_recommendations': len(period_savings),
            'implemented_recommendations': sum(1 for entry in period_savings if entry['implemented']),
            'generated_at': datetime.now().isoformat()
        }

    def get_system_health(self, db: Session) -> Dict[str, Any]:
        """
        Get system health metrics
        """
        try:
            # Check database connectivity
            cost_count = db.query(CloudCost).count()
            db_healthy = True
        except Exception as e:
            cost_count = 0
            db_healthy = False
            logger.error(f"Database health check failed: {e}")

        # Get recent cost data
        recent_costs = db.query(CloudCost).filter(
            CloudCost.date >= datetime.now().date() - timedelta(days=7)
        ).all()

        total_recent_cost = sum(cost.cost for cost in recent_costs)

        return {
            'database_healthy': db_healthy,
            'total_cost_records': cost_count,
            'recent_costs_7d': round(total_recent_cost, 2),
            'avg_daily_cost_7d': round(total_recent_cost / 7, 2) if recent_costs else 0,
            'performance_metrics': self.get_performance_report(),
            'cost_savings': self.calculate_total_savings(),
            'timestamp': datetime.now().isoformat()
        }

# Global monitoring instance
monitoring = MonitoringService()
