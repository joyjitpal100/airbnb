import os
import uuid
from datetime import datetime, timezone
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Airbnb Booking API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGO_URL = os.environ.get("MONGO_URL")
DB_NAME = os.environ.get("DB_NAME")
client = MongoClient(MONGO_URL)
db = client[DB_NAME]
bookings_collection = db["bookings"]

# Upload directory
UPLOAD_DIR = "/app/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Allowed file types for Aadhaar
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


@app.get("/api/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.post("/api/bookings")
async def create_booking(
    guest_name: str = Form(...),
    guest_phone: str = Form(...),
    check_in: str = Form(...),
    check_out: str = Form(...),
    num_guests: int = Form(...),
    total_price: float = Form(...),
    property_name: str = Form(...),
    aadhaar_file: Optional[UploadFile] = File(None)
):
    # Validate guests
    if num_guests < 1 or num_guests > 4:
        raise HTTPException(status_code=400, detail="Guests must be between 1 and 4")
    
    # Handle Aadhaar upload
    aadhaar_filename = None
    if aadhaar_file:
        # Validate file extension
        file_ext = os.path.splitext(aadhaar_file.filename)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail="Invalid file type. Allowed: JPG, JPEG, PNG, PDF")
        
        # Read and validate file size
        content = await aadhaar_file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large. Maximum size: 5MB")
        
        # Save file with unique name
        aadhaar_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, aadhaar_filename)
        with open(file_path, "wb") as f:
            f.write(content)
    
    # Create booking record
    booking = {
        "booking_id": str(uuid.uuid4())[:8].upper(),
        "guest_name": guest_name,
        "guest_phone": guest_phone,
        "check_in": check_in,
        "check_out": check_out,
        "num_guests": num_guests,
        "total_price": total_price,
        "property_name": property_name,
        "aadhaar_filename": aadhaar_filename,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "confirmed",
        # Retention flag for 7 years compliance
        "retention_until": "2033-01-01"
    }
    
    bookings_collection.insert_one(booking)
    
    # Remove MongoDB _id before returning
    booking.pop("_id", None)
    return {"success": True, "booking": booking}


@app.get("/api/bookings")
def get_all_bookings():
    bookings = list(bookings_collection.find({}, {"_id": 0}).sort("created_at", -1))
    return {"bookings": bookings}


@app.get("/api/bookings/{booking_id}")
def get_booking(booking_id: str):
    booking = bookings_collection.find_one({"booking_id": booking_id}, {"_id": 0})
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking


@app.get("/api/aadhaar/{filename}")
def get_aadhaar_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)


@app.delete("/api/bookings/{booking_id}")
def delete_booking(booking_id: str):
    result = bookings_collection.delete_one({"booking_id": booking_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Booking not found")
    return {"success": True, "message": "Booking deleted"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
