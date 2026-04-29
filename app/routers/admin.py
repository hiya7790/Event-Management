import io
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import pandas as pd

from .. import models, schemas, database, auth

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(auth.get_current_admin_user)]
)

@router.get("/registrations", response_model=List[schemas.RegistrationDetailResponse])
def get_all_registrations(
    skip: int = 0, 
    limit: int = 100, 
    event_id: Optional[int] = None,
    attended: Optional[bool] = None,
    db: Session = Depends(database.get_db)
):
    query = db.query(models.Registration)
    if event_id is not None:
        query = query.filter(models.Registration.event_id == event_id)
    if attended is not None:
        query = query.filter(models.Registration.attended == attended)
        
    registrations = query.offset(skip).limit(limit).all()
    return registrations

@router.post("/registrations/{registration_id}/attend", response_model=schemas.RegistrationResponse)
def mark_attendance(registration_id: int, db: Session = Depends(database.get_db)):
    registration = db.query(models.Registration).filter(models.Registration.id == registration_id).first()
    if not registration:
        raise HTTPException(status_code=404, detail="Registration not found")
    
    registration.attended = True
    db.commit()
    db.refresh(registration)
    return registration

@router.get("/export/{event_id}")
def export_event_data(event_id: int, format: str = "csv", db: Session = Depends(database.get_db)):
    """
    Export event registrations to CSV or Excel.
    format: 'csv' or 'excel'
    """
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
        
    registrations = db.query(models.Registration).filter(models.Registration.event_id == event_id).all()
    
    data = []
    for reg in registrations:
        data.append({
            "Registration ID": reg.id,
            "User ID": reg.user.id,
            "Username": reg.user.username,
            "Email": reg.user.email,
            "Team Code": reg.team.code if reg.team else "N/A",
            "Attended": reg.attended,
            "Registration Date": reg.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })
        
    df = pd.DataFrame(data)
    
    buf = io.BytesIO()
    if format.lower() == "excel":
        with pd.ExcelWriter(buf, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        buf.seek(0)
        return StreamingResponse(
            buf, 
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
            headers={"Content-Disposition": f"attachment; filename=event_{event_id}_registrations.xlsx"}
        )
    else:
        # Default to CSV
        csv_data = df.to_csv(index=False)
        buf.write(csv_data.encode("utf-8"))
        buf.seek(0)
        return StreamingResponse(
            buf, 
            media_type="text/csv", 
            headers={"Content-Disposition": f"attachment; filename=event_{event_id}_registrations.csv"}
        )
