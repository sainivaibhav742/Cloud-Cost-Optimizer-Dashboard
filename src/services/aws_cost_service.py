import boto3
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
from botocore.exceptions import ClientError

class AWSCostService:
    def __init__(self):
        self.client = boto3.client(
            'ce',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name='us-east-1'  # Default region for Cost Explorer
        )

    def get_cost_and_usage(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Fetch cost and usage data from AWS Cost Explorer.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            List of cost data dictionaries
        """
        try:
            response = self.client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date,
                    'End': end_date
                },
                Granularity='DAILY',
                Metrics=['UnblendedCost', 'UsageQuantity'],
                GroupBy=[
                    {
                        'Type': 'DIMENSION',
                        'Key': 'SERVICE'
                    }
                ]
            )

            cost_data = []
            for result in response['ResultsByTime']:
                date = result['TimePeriod']['Start']
                for group in result['Groups']:
                    service = group['Keys'][0]
                    cost = float(group['Metrics']['UnblendedCost']['Amount'])
                    usage = float(group['Metrics']['UsageQuantity']['Amount']) if 'UsageQuantity' in group['Metrics'] else 0.0

                    cost_data.append({
                        'date': date,
                        'service': service,
                        'cost': cost,
                        'usage': usage,
                        'account_id': os.getenv('AWS_ACCOUNT_ID', 'default')
                    })

            return cost_data

        except ClientError as e:
            print(f"Error fetching AWS cost data: {e}")
            return []

    def get_yesterday_costs(self) -> List[Dict[str, Any]]:
        """
        Get cost data for yesterday.
        """
        yesterday = datetime.now() - timedelta(days=1)
        start_date = yesterday.strftime('%Y-%m-%d')
        end_date = (yesterday + timedelta(days=1)).strftime('%Y-%m-%d')

        return self.get_cost_and_usage(start_date, end_date)
