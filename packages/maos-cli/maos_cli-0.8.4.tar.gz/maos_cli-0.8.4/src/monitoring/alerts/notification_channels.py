"""
Notification channels for MAOS alert manager.
"""

import asyncio
import json
import smtplib
from abc import ABC, abstractmethod
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional, Any
from uuid import uuid4

import aiohttp

from ...maos.utils.logging_config import MAOSLogger
from .alert_manager import Alert


class NotificationChannel(ABC):
    """Abstract base class for notification channels."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        """Initialize notification channel."""
        self.name = name
        self.config = config
        self.logger = MAOSLogger(f"notification_{name}", str(uuid4()))
    
    @abstractmethod
    async def send_alert(self, alert: Alert, action: str) -> bool:
        """
        Send alert notification.
        
        Args:
            alert: Alert to send
            action: Action type (fired, resolved, acknowledged)
            
        Returns:
            True if sent successfully
        """
        pass
    
    def format_alert_message(self, alert: Alert, action: str) -> Dict[str, str]:
        """Format alert message for notifications."""
        # Color coding for different severities
        severity_colors = {
            "critical": "🔴",
            "high": "🟠", 
            "medium": "🟡",
            "low": "🟢"
        }
        
        # Action emojis
        action_emojis = {
            "fired": "🚨",
            "resolved": "✅",
            "acknowledged": "👍"
        }
        
        emoji = severity_colors.get(alert.severity.value, "⚪")
        action_emoji = action_emojis.get(action, "ℹ️")
        
        title = f"{action_emoji} Alert {action.title()}: {alert.name}"
        
        message = f"""
{emoji} **Alert {action.title()}**

**Name:** {alert.name}
**Severity:** {alert.severity.value.upper()}
**Component:** {alert.component}
**Description:** {alert.description}

**Details:**
- Metric: {alert.metric_name}
- Current Value: {alert.metric_value}
- Threshold: {alert.threshold}
- Condition: {alert.condition}
- Created: {alert.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}

**Alert ID:** {alert.id}
        """.strip()
        
        return {
            "title": title,
            "message": message,
            "severity": alert.severity.value,
            "component": alert.component,
            "action": action
        }


class EmailNotificationChannel(NotificationChannel):
    """Email notification channel."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize email channel.
        
        Config should contain:
        - smtp_server: SMTP server hostname
        - smtp_port: SMTP port (default 587)
        - username: SMTP username
        - password: SMTP password
        - from_email: From email address
        - to_emails: List of recipient emails
        - use_tls: Whether to use TLS (default True)
        """
        super().__init__("email", config)
        
        self.smtp_server = config["smtp_server"]
        self.smtp_port = config.get("smtp_port", 587)
        self.username = config["username"]
        self.password = config["password"]
        self.from_email = config["from_email"]
        self.to_emails = config["to_emails"]
        self.use_tls = config.get("use_tls", True)
    
    async def send_alert(self, alert: Alert, action: str) -> bool:
        """Send alert via email."""
        try:
            formatted = self.format_alert_message(alert, action)
            
            # Create message
            msg = MIMEMultipart()
            msg["From"] = self.from_email
            msg["To"] = ", ".join(self.to_emails)
            msg["Subject"] = f"[MAOS] {formatted['title']}"
            
            # Convert markdown-style formatting to plain text
            body = formatted["message"].replace("**", "").replace("*", "")
            msg.attach(MIMEText(body, "plain"))
            
            # Send email in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._send_email, msg)
            
            self.logger.logger.info(f"Email notification sent for alert {alert.id}")
            return True
            
        except Exception as e:
            self.logger.log_error(e, {
                "operation": "send_email_notification",
                "alert_id": alert.id
            })
            return False
    
    def _send_email(self, msg: MIMEMultipart) -> None:
        """Send email synchronously."""
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            if self.use_tls:
                server.starttls()
            server.login(self.username, self.password)
            server.send_message(msg)


class SlackNotificationChannel(NotificationChannel):
    """Slack notification channel."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Slack channel.
        
        Config should contain:
        - webhook_url: Slack webhook URL
        - channel: Slack channel (optional, overrides webhook default)
        - username: Bot username (optional)
        """
        super().__init__("slack", config)
        
        self.webhook_url = config["webhook_url"]
        self.channel = config.get("channel")
        self.username = config.get("username", "MAOS Alert Bot")
    
    async def send_alert(self, alert: Alert, action: str) -> bool:
        """Send alert to Slack."""
        try:
            formatted = self.format_alert_message(alert, action)
            
            # Color coding for Slack
            color_map = {
                "critical": "danger",
                "high": "warning",
                "medium": "warning", 
                "low": "good"
            }
            
            color = color_map.get(alert.severity.value, "warning")
            
            # Create Slack payload
            payload = {
                "username": self.username,
                "attachments": [
                    {
                        "color": color,
                        "title": formatted["title"],
                        "text": formatted["message"],
                        "fields": [
                            {
                                "title": "Component",
                                "value": alert.component,
                                "short": True
                            },
                            {
                                "title": "Severity", 
                                "value": alert.severity.value.upper(),
                                "short": True
                            },
                            {
                                "title": "Metric",
                                "value": f"{alert.metric_name}: {alert.metric_value}",
                                "short": True
                            },
                            {
                                "title": "Threshold",
                                "value": f"{alert.condition} {alert.threshold}",
                                "short": True
                            }
                        ],
                        "timestamp": int(alert.created_at.timestamp())
                    }
                ]
            }
            
            if self.channel:
                payload["channel"] = self.channel
            
            # Send to Slack
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        self.logger.logger.info(f"Slack notification sent for alert {alert.id}")
                        return True
                    else:
                        self.logger.logger.error(f"Slack notification failed: {response.status}")
                        return False
            
        except Exception as e:
            self.logger.log_error(e, {
                "operation": "send_slack_notification",
                "alert_id": alert.id
            })
            return False


class WebhookNotificationChannel(NotificationChannel):
    """Generic webhook notification channel."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize webhook channel.
        
        Config should contain:
        - url: Webhook URL
        - method: HTTP method (default POST)
        - headers: Additional headers (optional)
        - timeout: Request timeout in seconds (default 30)
        """
        super().__init__("webhook", config)
        
        self.url = config["url"]
        self.method = config.get("method", "POST").upper()
        self.headers = config.get("headers", {})
        self.timeout = config.get("timeout", 30)
    
    async def send_alert(self, alert: Alert, action: str) -> bool:
        """Send alert via webhook."""
        try:
            formatted = self.format_alert_message(alert, action)
            
            # Create webhook payload
            payload = {
                "alert": alert.to_dict(),
                "action": action,
                "formatted": formatted,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Send webhook
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.request(
                    self.method,
                    self.url,
                    json=payload,
                    headers=self.headers
                ) as response:
                    if 200 <= response.status < 300:
                        self.logger.logger.info(f"Webhook notification sent for alert {alert.id}")
                        return True
                    else:
                        self.logger.logger.error(
                            f"Webhook notification failed: {response.status}",
                            extra={"response_text": await response.text()}
                        )
                        return False
            
        except Exception as e:
            self.logger.log_error(e, {
                "operation": "send_webhook_notification",
                "alert_id": alert.id
            })
            return False


class PagerDutyNotificationChannel(NotificationChannel):
    """PagerDuty notification channel."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize PagerDuty channel.
        
        Config should contain:
        - integration_key: PagerDuty integration key
        - severity_mapping: Optional mapping of MAOS severities to PagerDuty severities
        """
        super().__init__("pagerduty", config)
        
        self.integration_key = config["integration_key"]
        self.severity_mapping = config.get("severity_mapping", {
            "critical": "critical",
            "high": "error",
            "medium": "warning",
            "low": "info"
        })
        self.api_url = "https://events.pagerduty.com/v2/enqueue"
    
    async def send_alert(self, alert: Alert, action: str) -> bool:
        """Send alert to PagerDuty."""
        try:
            formatted = self.format_alert_message(alert, action)
            
            # Map MAOS actions to PagerDuty event actions
            if action == "fired":
                event_action = "trigger"
            elif action == "resolved":
                event_action = "resolve"
            else:
                return True  # Skip acknowledged events
            
            # Create PagerDuty payload
            payload = {
                "routing_key": self.integration_key,
                "event_action": event_action,
                "dedup_key": f"maos-alert-{alert.id}",
                "payload": {
                    "summary": formatted["title"],
                    "source": "MAOS",
                    "severity": self.severity_mapping.get(alert.severity.value, "warning"),
                    "component": alert.component,
                    "custom_details": {
                        "alert_id": alert.id,
                        "metric_name": alert.metric_name,
                        "metric_value": alert.metric_value,
                        "threshold": alert.threshold,
                        "condition": alert.condition,
                        "description": alert.description,
                        "labels": alert.labels,
                        "annotations": alert.annotations
                    }
                }
            }
            
            # Send to PagerDuty
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 202:
                        self.logger.logger.info(f"PagerDuty notification sent for alert {alert.id}")
                        return True
                    else:
                        response_text = await response.text()
                        self.logger.logger.error(
                            f"PagerDuty notification failed: {response.status}",
                            extra={"response_text": response_text}
                        )
                        return False
            
        except Exception as e:
            self.logger.log_error(e, {
                "operation": "send_pagerduty_notification",
                "alert_id": alert.id
            })
            return False