import os
import uuid
from datetime import datetime, timezone
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from pymongo import MongoClient
from dotenv import load_dotenv
import httpx

load_dotenv()

app = FastAPI(title="Airbnb Booking API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MONGO_URL = os.environ.get("MONGO_URL")
DB_NAME = os.environ.get("DB_NAME")
client = MongoClient(MONGO_URL)
db = client[DB_NAME]
bookings_collection = db["bookings"]

UPLOAD_DIR = "/app/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf"}
MAX_FILE_SIZE = 5 * 1024 * 1024

VAULT_DEV_SERVER = "http://localhost:8002"


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


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
    if num_guests < 1 or num_guests > 4:
        raise HTTPException(status_code=400, detail="Guests must be between 1 and 4")

    aadhaar_filename = None
    if aadhaar_file:
        file_ext = os.path.splitext(aadhaar_file.filename)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail="Invalid file type.")
        content = await aadhaar_file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large.")
        aadhaar_filename = f"{uuid.uuid4()}{file_ext}"
        with open(os.path.join(UPLOAD_DIR, aadhaar_filename), "wb") as f:
            f.write(content)

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
        "retention_until": "2033-01-01"
    }

    bookings_collection.insert_one(booking)
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


@app.api_route("/api/vault/{path:path}", methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"])
async def proxy_vault(request: Request, path: str):
    """Proxy vault requests to the Node.js Netlify function dev server on port 8002."""
    try:
        async with httpx.AsyncClient(timeout=60.0) as http_client:
            url = f"{VAULT_DEV_SERVER}/api/vault/{path}"
            headers = {k: v for k, v in request.headers.items() if k.lower() != "host"}
            body = await request.body()

            response = await http_client.request(
                method=request.method,
                url=url,
                headers=headers,
                content=body,
                params=dict(request.query_params),
            )

            excluded = {"content-encoding", "transfer-encoding", "content-length"}
            resp_headers = {k: v for k, v in response.headers.items() if k.lower() not in excluded}

            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=resp_headers,
            )
    except httpx.ConnectError:
        return Response(
            content='{"error": "Vault service unavailable. Ensure the vault dev server is running on port 8002."}',
            status_code=503,
            media_type="application/json",
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
