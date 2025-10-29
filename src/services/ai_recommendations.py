import openai
import os
from typing import List, Dict
from sqlalchemy.orm import Session
from src.models.cost_model import CloudCost

class AIRecommendationService:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if self.api_key:
            openai.api_key = self.api_key

    def generate_ai_recommendations(self, db: Session, user_id: int = None) -> List[Dict]:
        """
        Generate AI-powered cost optimization recommendations using OpenAI
        """
        if not self.api_key:
            return [{"type": "error", "message": "OpenAI API key not configured"}]

        # Get cost data
        costs = db.query(CloudCost).all()

        if not costs:
            return [{"type": "info", "message": "No cost data available for AI analysis"}]

        # Prepare cost summary for AI
        cost_summary = self._prepare_cost_summary(costs)

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a cloud cost optimization expert. Analyze the provided cost data and provide specific, actionable recommendations to reduce cloud spending. Focus on AWS services and common optimization strategies."
                    },
                    {
                        "role": "user",
                        "content": f"Analyze this cloud cost data and provide 3-5 specific recommendations to optimize costs:\n\n{cost_summary}"
                    }
                ],
                max_tokens=500,
                temperature=0.7
            )

            ai_response = response.choices[0].message.content

            # Parse AI response into structured recommendations
            return self._parse_ai_response(ai_response)

        except Exception as e:
            return [{"type": "error", "message": f"AI analysis failed: {str(e)}"}]

    def _prepare_cost_summary(self, costs: List[CloudCost]) -> str:
        """Prepare cost data summary for AI analysis"""
        service_costs = {}
        total_cost = 0

        for cost in costs:
            service = cost.service
            if service not in service_costs:
                service_costs[service] = 0
            service_costs[service] += cost.cost
            total_cost += cost.cost

        summary = f"Total Monthly Cost: ${total_cost:.2f}\n\nService Breakdown:\n"
        for service, cost in sorted(service_costs.items(), key=lambda x: x[1], reverse=True):
            percentage = (cost / total_cost) * 100 if total_cost > 0 else 0
            summary += f"- {service}: ${cost:.2f} ({percentage:.1f}%)\n"

        return summary

    def _parse_ai_response(self, ai_response: str) -> List[Dict]:
        """Parse AI response into structured recommendations"""
        recommendations = []

        # Split response into individual recommendations
        lines = ai_response.split('\n')
        current_rec = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if this is a new recommendation (numbered or bulleted)
            if line.startswith(('1.', '2.', '3.', '4.', '5.', '-', '*')):
                if current_rec:
                    recommendations.append(current_rec)

                current_rec = {
                    "type": "ai_recommendation",
                    "title": line.lstrip('12345.-* ').split(':')[0] if ':' in line else line.lstrip('12345.-* '),
                    "description": line,
                    "potential_savings": "TBD",  # Could be enhanced with more parsing
                    "priority": "medium"
                }
            elif current_rec:
                current_rec["description"] += f" {line}"

        if current_rec:
            recommendations.append(current_rec)

        return recommendations[:5]  # Limit to 5 recommendations
