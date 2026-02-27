"""
Alerts router.
POST   /api/alerts
GET    /api/alerts
DELETE /api/alerts/{id}
"""
import logging

from fastapi import APIRouter, HTTPException

from models.schemas import AlertCreateRequest, Alert
from database import db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.post("")
async def create_alert(req: AlertCreateRequest):
    alert_id = await db.create_alert(
        name=req.name,
        asset_a=req.asset_a.model_dump(),
        asset_b=req.asset_b.model_dump(),
        condition=req.condition,
        threshold=req.threshold,
        notify_via=req.notify_via,
    )
    return {"id": alert_id, "message": "Alert created"}


@router.get("")
async def list_alerts():
    alerts = await db.get_alerts()
    return {"alerts": alerts}


@router.delete("/{alert_id}")
async def delete_alert(alert_id: int):
    await db.delete_alert(alert_id)
    return {"message": "Alert deleted"}
