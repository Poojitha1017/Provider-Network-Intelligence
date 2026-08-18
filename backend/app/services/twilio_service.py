import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("uvicorn.error")

class TwilioService:
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.from_phone = os.getenv("TWILIO_PHONE_NUMBER")
        self.client = None

        if self.account_sid and self.auth_token:
            try:
                from twilio.rest import Client
                self.client = Client(self.account_sid, self.auth_token)
                logger.info("Twilio Client initialized successfully.")
            except Exception as e:
                logger.warning(f"Twilio initialization failed: {e}")

    def send_sms(self, to_phone: str, message: str) -> Dict[str, Any]:
        """
        Dispatches an SMS alert via Twilio REST API.
        If Twilio credentials are not configured, returns a realistic simulation response.
        """
        clean_phone = to_phone.strip()
        if not clean_phone.startswith("+"):
            clean_phone = f"+1{clean_phone.lstrip('1')}"

        if self.client and self.from_phone:
            try:
                msg = self.client.messages.create(
                    body=message,
                    from_=self.from_phone,
                    to=clean_phone
                )
                logger.info(f"Twilio SMS sent to {clean_phone}: SID={msg.sid}")
                return {
                    "success": True,
                    "sid": msg.sid,
                    "status": msg.status,
                    "to": clean_phone,
                    "message": "SMS dispatched successfully via Twilio live gateway.",
                    "is_simulated": False
                }
            except Exception as e:
                logger.error(f"Twilio API call failed: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "to": clean_phone,
                    "message": f"Failed to send SMS via Twilio: {e}",
                    "is_simulated": False
                }
        else:
            logger.info(f"[SIMULATED TWILIO SMS] To: {clean_phone} | Message: {message[:60]}...")
            return {
                "success": True,
                "sid": f"SM_SIMULATED_{os.urandom(4).hex().upper()}",
                "status": "delivered",
                "to": clean_phone,
                "message": "SMS dispatched successfully (Simulation Mode - Add TWILIO_ACCOUNT_SID to .env for live SMS).",
                "is_simulated": True
            }

    def make_call(self, to_phone: str, message: str) -> Dict[str, Any]:
        """
        Triggers a voice call via Twilio REST API, speaking the message text.
        If Twilio credentials are not configured, returns a realistic simulation response.
        """
        clean_phone = to_phone.strip()
        if not clean_phone.startswith("+"):
            clean_phone = f"+1{clean_phone.lstrip('1')}"

        if self.client and self.from_phone:
            try:
                twiml_content = f"<Response><Say voice='alice'>{message}</Say></Response>"
                call = self.client.calls.create(
                    to=clean_phone,
                    from_=self.from_phone,
                    twiml=twiml_content
                )
                logger.info(f"Twilio Call initiated to {clean_phone}: SID={call.sid}")
                return {
                    "success": True,
                    "sid": call.sid,
                    "status": call.status,
                    "to": clean_phone,
                    "message": "Voice call initiated successfully via Twilio live gateway.",
                    "is_simulated": False
                }
            except Exception as e:
                logger.error(f"Twilio Call API failed: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "to": clean_phone,
                    "message": f"Failed to initiate call via Twilio: {e}",
                    "is_simulated": False
                }
        else:
            logger.info(f"[SIMULATED TWILIO CALL] To: {clean_phone} | Message: {message[:60]}...")
            return {
                "success": True,
                "sid": f"CA_SIMULATED_{os.urandom(4).hex().upper()}",
                "status": "queued",
                "to": clean_phone,
                "message": "Voice call initiated successfully (Simulation Mode - Add TWILIO_ACCOUNT_SID to .env for live Voice).",
                "is_simulated": True
            }

twilio_service = TwilioService()

