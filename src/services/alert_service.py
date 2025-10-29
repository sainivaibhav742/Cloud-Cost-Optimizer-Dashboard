import os
import logging
from typing import List, Dict, Any
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests

logger = logging.getLogger(__name__)

class AlertService:
    def __init__(self):
        self.email_enabled = bool(os.getenv('SMTP_SERVER'))
        self.slack_enabled = bool(os.getenv('SLACK_WEBHOOK_URL'))

    def send_email_alert(self, subject: str, body: str, recipients: List[str] = None):
        """
        Send email alert for anomalies.
        """
        if not self.email_enabled:
            logger.warning("Email alerts not configured")
            return

        if not recipients:
            recipients = [os.getenv('ALERT_EMAIL', '')]

        try:
            msg = MIMEMultipart()
            msg['From'] = os.getenv('SMTP_FROM', 'cost-optimizer@yourdomain.com')
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'html'))

            server = smtplib.SMTP(os.getenv('SMTP_SERVER'), int(os.getenv('SMTP_PORT', 587)))
            server.starttls()
            server.login(os.getenv('SMTP_USERNAME'), os.getenv('SMTP_PASSWORD'))
            server.sendmail(msg['From'], recipients, msg.as_string())
            server.quit()

            logger.info(f"Email alert sent to {recipients}")

        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")

    def send_slack_alert(self, message: str, channel: str = None):
        """
        Send Slack alert for anomalies.
        """
        if not self.slack_enabled:
            logger.warning("Slack alerts not configured")
            return

        try:
            webhook_url = os.getenv('SLACK_WEBHOOK_URL')
            payload = {
                "text": message,
                "channel": channel or os.getenv('SLACK_CHANNEL', '#cost-alerts')
            }

            response = requests.post(webhook_url, json=payload)
            if response.status_code == 200:
                logger.info("Slack alert sent successfully")
            else:
                logger.error(f"Failed to send Slack alert: {response.text}")

        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")

    def format_anomaly_alert(self, recommendations: Dict[str, List[Dict[str, Any]]]) -> str:
        """
        Format anomaly recommendations into alert message.
        """
        total_issues = sum(len(recs) for recs in recommendations.values())

        if total_issues == 0:
            return "✅ No cost anomalies detected today."

        message = f"🚨 Cost Optimization Alert: {total_issues} issues found\n\n"

        for category, recs in recommendations.items():
            if recs:
                message += f"**{category.replace('_', ' ').title()}:**\n"
                for rec in recs[:5]:  # Limit to top 5 per category
                    message += f"• {rec.get('suggestion', 'Check service')}\n"
                    if 'potential_savings' in rec and rec['potential_savings'] > 0:
                        message += f"  💰 Potential savings: ${rec['potential_savings']:.2f}\n"
                message += "\n"

        message += "📊 Check the dashboard for full details."
        return message

    def send_anomaly_alerts(self, recommendations: Dict[str, List[Dict[str, Any]]]):
        """
        Send alerts for detected anomalies.
        """
        message = self.format_anomaly_alert(recommendations)

        # Send email alert
        if self.email_enabled:
            self.send_email_alert(
                subject="Cloud Cost Optimization Alert",
                body=message.replace('\n', '<br>')
            )

        # Send Slack alert
        if self.slack_enabled:
            self.send_slack_alert(message)

    def send_cost_spike_alert(self, service: str, increase_percent: float, recent_cost: float, previous_cost: float):
        """
        Send alert for significant cost spikes.
        """
        message = f"⚠️ Cost Spike Alert\n\n"
        message += f"Service: {service}\n"
        message += f"Cost increase: {increase_percent:.1f}%\n"
        message += f"Recent cost: ${recent_cost:.2f}\n"
        message += f"Previous cost: ${previous_cost:.2f}\n\n"
        message += "Investigate immediately!"

        if self.email_enabled:
            self.send_email_alert(
                subject=f"Cost Spike Alert: {service}",
                body=message.replace('\n', '<br>')
            )

        if self.slack_enabled:
            self.send_slack_alert(message)

    def send_daily_cost_report(self, daily_cost: float, recommendations: List[Dict], alert_config: Dict = None):
        """
        Send daily cost report with recommendations
        """
        message = self._format_daily_report(daily_cost, recommendations)

        # Send email alerts
        if self.email_enabled:
            self.send_email_alert(
                subject=f"Daily Cloud Cost Report - ${daily_cost:.2f}",
                body=message.replace('\n', '<br>')
            )

        # Send Slack alerts
        if self.slack_enabled:
            slack_message = f"💰 Daily Cost Report: ${daily_cost:.2f}\n"
            if recommendations:
                slack_message += "Top recommendations:\n"
                for rec in recommendations[:3]:
                    slack_message += f"• {rec.get('suggestion', rec.get('description', 'Check service'))}\n"
            self.send_slack_alert(slack_message)

    def _format_daily_report(self, daily_cost: float, recommendations: List[Dict]) -> str:
        """
        Format daily cost report message
        """
        message = f"💰 Daily Cloud Cost Report\n\n"
        message += f"Today's Total Cost: ${daily_cost:.2f}\n\n"

        if recommendations:
            message += "📋 Top Recommendations:\n"
            for rec in recommendations[:5]:  # Top 5 recommendations
                message += f"• {rec.get('suggestion', rec.get('description', 'Recommendation'))}\n"
                if 'potential_savings' in rec and rec['potential_savings'] > 0:
                    message += f"  💰 Potential savings: ${rec['potential_savings']:.2f}\n"
            message += "\n"

        message += "Keep optimizing your cloud costs! ☁️"
        return message
