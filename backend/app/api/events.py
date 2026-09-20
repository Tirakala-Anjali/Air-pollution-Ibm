"""
GET /api/events          – list all events for a session
GET /api/events/{id}     – single event detail with full explanation
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.pollution_event import PollutionEvent
from app.schemas.pollution_event import PollutionEventOut

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/events", response_model=List[PollutionEventOut])
def list_events(
    session_id: str = Query(...),
    severity:   Optional[str] = Query(None, description="Filter by severity label"),
    db: Session = Depends(get_db),
):
    q = db.query(PollutionEvent).filter(PollutionEvent.session_id == session_id)
    if severity:
        q = q.filter(PollutionEvent.severity == severity.upper())
    events = q.order_by(PollutionEvent.start_time).all()
    return events


@router.get("/events/{event_id}", response_model=PollutionEventOut)
def get_event(
    event_id:   int,
    session_id: str = Query(...),
    db: Session = Depends(get_db),
):
    event = (
        db.query(PollutionEvent)
        .filter(
            PollutionEvent.id         == event_id,
            PollutionEvent.session_id == session_id,
        )
        .first()
    )
    if not event:
        raise HTTPException(status_code=404, detail=f"Event {event_id} not found.")
    return event
