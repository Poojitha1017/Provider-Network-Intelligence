from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from app.services.twilio_service import twilio_service

router = APIRouter()

class SendSMSRequest(BaseModel):
    to_phone: str = Field(..., description="Recipient phone number (e.g. +1234567890)")
    message: str = Field(..., description="SMS alert body text")

class AlertRecommendationRequest(BaseModel):
    to_phone: str = Field(..., description="Field agent / manager phone number")
    county_name: str
    specialty: str
    gap_level: str
    recommended_action: str

@router.post("/send-sms", response_model=Dict[str, Any])
def send_sms_route(req: SendSMSRequest):
    """
    Sends a direct SMS alert using Twilio.
    """
    if not req.to_phone or not req.message:
        raise HTTPException(status_code=400, detail="Phone number and message text are required.")
    
    result = twilio_service.send_sms(req.to_phone, req.message)
    return result

@router.post("/alert-recommendation", response_model=Dict[str, Any])
def alert_recommendation_route(req: AlertRecommendationRequest):
    """
    Formats a healthcare shortage alert and dispatches it via Twilio SMS.
    """
    body = (
        f"[ALERT] Healthcare Network Action Required!\n"
        f"Location: {req.county_name}\n"
        f"Specialty: {req.specialty}\n"
        f"Shortage Level: {req.gap_level}\n"
        f"Action: {req.recommended_action}"
    )
    result = twilio_service.send_sms(req.to_phone, body)
    return result

class CallAndSMSRequest(BaseModel):
    to_phone: str = Field(..., description="Recipient phone number (e.g. +1234567890)")
    message: str = Field(..., description="Alert body text for SMS and Voice call")

@router.post("/send-call-and-sms", response_model=Dict[str, Any])
def send_call_and_sms_route(req: CallAndSMSRequest):
    """
    Sends an SMS and initiates a simulated/live Twilio Voice call with the same message text.
    """
    if not req.to_phone or not req.message:
        raise HTTPException(status_code=400, detail="Phone number and message text are required.")
    
    sms_result = twilio_service.send_sms(req.to_phone, req.message)
    call_result = twilio_service.make_call(req.to_phone, req.message)
    
    return {
        "success": sms_result.get("success", False) and call_result.get("success", False),
        "sms": sms_result,
        "call": call_result,
        "message": "Twilio SMS and Voice Call dispatched successfully."
    }

