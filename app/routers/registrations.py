import io
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from .. import models, schemas, database, auth

router = APIRouter(
    tags=["registrations"],
)

@router.post("/events/{event_id}/register", response_model=schemas.RegistrationResponse)
def register_for_event(
    event_id: int,
    registration: schemas.RegistrationCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    existing_registration = db.query(models.Registration).filter(
        models.Registration.user_id == current_user.id,
        models.Registration.event_id == event_id
    ).first()
    if existing_registration:
        raise HTTPException(status_code=400, detail="Already registered for this event")

    team_id = None
    if registration.team_code:
        team = db.query(models.Team).filter(models.Team.code == registration.team_code, models.Team.event_id == event_id).first()
        if not team:
            # Create a new team if it doesn't exist
            team = models.Team(code=registration.team_code, event_id=event_id)
            db.add(team)
            db.commit()
            db.refresh(team)
        team_id = team.id

    db_registration = models.Registration(
        user_id=current_user.id,
        event_id=event_id,
        team_id=team_id
    )
    db.add(db_registration)
    db.commit()
    db.refresh(db_registration)
    return db_registration

@router.get("/registrations/{registration_id}/qr")
def get_registration_qr(registration_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    registration = db.query(models.Registration).filter(models.Registration.id == registration_id).first()
    if not registration:
        raise HTTPException(status_code=404, detail="Registration not found")
    
    # Check if user is owner or admin
    if registration.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to view this QR code")

    # The QR code data could be a simple URL that admins scan to mark attendance
    qr_data = f"registration_id:{registration.id}"
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    
    return StreamingResponse(buf, media_type="image/png")

@router.get("/registrations/{registration_id}/certificate")
def get_certificate(registration_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    registration = db.query(models.Registration).filter(models.Registration.id == registration_id).first()
    if not registration:
        raise HTTPException(status_code=404, detail="Registration not found")
    
    if registration.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    if not registration.attended:
        raise HTTPException(status_code=400, detail="User has not attended the event yet")

    user = registration.user
    event = registration.event

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    width, height = letter

    # Simple certificate design
    c.setFont("Helvetica-Bold", 36)
    c.drawCentredString(width / 2.0, height - 200, "Certificate of Attendance")
    
    c.setFont("Helvetica", 24)
    c.drawCentredString(width / 2.0, height - 300, f"This is to certify that")
    
    c.setFont("Helvetica-Bold", 30)
    c.drawCentredString(width / 2.0, height - 360, f"{user.username}")
    
    c.setFont("Helvetica", 24)
    c.drawCentredString(width / 2.0, height - 420, f"has successfully attended the event")
    
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(width / 2.0, height - 480, f"{event.title}")
    
    c.setFont("Helvetica", 18)
    date_str = event.date.strftime("%B %d, %Y") if event.date else "Unknown Date"
    c.drawCentredString(width / 2.0, height - 540, f"Date: {date_str}")
    
    c.save()
    buf.seek(0)

    return StreamingResponse(buf, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=certificate_{event.id}.pdf"})
