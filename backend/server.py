import os
import uuid
from datetime import datetime, timezone, timedelta
from dateutil.relativedelta import relativedelta
from typing import Optional, List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pymongo import MongoClient
from dotenv import load_dotenv
from supabase import create_client, Client
import boto3
from botocore.config import Config

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

# Upload directory (for existing bookings)
UPLOAD_DIR = "/app/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Allowed file types
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# ============================================
# SUPABASE CONFIGURATION (Metadata only)
# ============================================
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

# Retention configuration (7 years)
RETENTION_YEARS = 7

# Initialize Supabase client (for metadata storage)
supabase: Optional[Client] = None
if SUPABASE_URL and SUPABASE_SERVICE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    except Exception as e:
        print(f"Warning: Could not initialize Supabase client: {e}")

# ============================================
# CLOUDFLARE R2 CONFIGURATION (File storage)
# ============================================
R2_ACCOUNT_ID = os.environ.get("R2_ACCOUNT_ID")
R2_ACCESS_KEY_ID = os.environ.get("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.environ.get("R2_SECRET_ACCESS_KEY")
R2_BUCKET_NAME = os.environ.get("R2_BUCKET_NAME", "guest-id-documents")
R2_PUBLIC_URL = os.environ.get("R2_PUBLIC_URL", "")

# Initialize R2 client (S3-compatible)
r2_client = None
if R2_ACCOUNT_ID and R2_ACCESS_KEY_ID and R2_SECRET_ACCESS_KEY:
    try:
        r2_client = boto3.client(
            "s3",
            endpoint_url=f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
            aws_access_key_id=R2_ACCESS_KEY_ID,
            aws_secret_access_key=R2_SECRET_ACCESS_KEY,
            config=Config(signature_version="s3v4"),
            region_name="auto"
        )
    except Exception as e:
        print(f"Warning: Could not initialize R2 client: {e}")


def upload_to_r2(file_content: bytes, file_key: str, content_type: str) -> str:
    """Upload file to Cloudflare R2 and return the file path"""
    if not r2_client:
        raise HTTPException(status_code=503, detail="R2 storage not configured")
    
    r2_client.put_object(
        Bucket=R2_BUCKET_NAME,
        Key=file_key,
        Body=file_content,
        ContentType=content_type
    )
    return file_key


def get_r2_presigned_url(file_key: str, expires_in: int = 3600) -> str:
    """Generate a presigned URL for downloading a file from R2"""
    if not r2_client:
        raise HTTPException(status_code=503, detail="R2 storage not configured")
    
    url = r2_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": R2_BUCKET_NAME, "Key": file_key},
        ExpiresIn=expires_in
    )
    return url


def delete_from_r2(file_key: str) -> bool:
    """Delete a file from R2"""
    if not r2_client:
        return False
    try:
        r2_client.delete_object(Bucket=R2_BUCKET_NAME, Key=file_key)
        return True
    except Exception:
        return False


def calculate_retention_date(check_out_date: Optional[str], uploaded_at: datetime) -> str:
    """Calculate retention_until as 7 years from check_out_date or uploaded_at"""
    if check_out_date:
        try:
            base_date = datetime.strptime(check_out_date, "%Y-%m-%d")
        except ValueError:
            base_date = uploaded_at
    else:
        base_date = uploaded_at
    
    retention_date = base_date + relativedelta(years=RETENTION_YEARS)
    return retention_date.strftime("%Y-%m-%d")


# ============================================
# EXISTING BOOKING ENDPOINTS
# ============================================

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "supabase_connected": supabase is not None,
        "r2_connected": r2_client is not None
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
            raise HTTPException(status_code=400, detail="Invalid file type. Allowed: JPG, JPEG, PNG, PDF")
        
        content = await aadhaar_file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large. Maximum size: 5MB")
        
        aadhaar_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, aadhaar_filename)
        with open(file_path, "wb") as f:
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


# ============================================
# GUEST ID VAULT ENDPOINTS
# ============================================

@app.get("/api/vault/status")
def vault_status():
    """Check if Guest ID Vault is properly configured"""
    return {
        "configured": supabase is not None and r2_client is not None,
        "supabase_configured": supabase is not None,
        "r2_configured": r2_client is not None,
        "retention_years": RETENTION_YEARS,
        "storage_bucket": R2_BUCKET_NAME
    }


@app.post("/api/vault/guests")
async def create_guest_record(
    guest_name: str = Form(...),
    phone: str = Form(None),
    booking_source: str = Form("direct"),
    property_name: str = Form(None),
    check_in_date: str = Form(None),
    check_out_date: str = Form(None),
    notes: str = Form(None),
    document_type: str = Form(None),
    document_file: Optional[UploadFile] = File(None)
):
    """Create a new guest record with optional document upload to R2"""
    if not supabase:
        raise HTTPException(status_code=503, detail="Supabase not configured")
    
    if not guest_name:
        raise HTTPException(status_code=400, detail="Guest name is required")
    
    if not check_in_date and not check_out_date:
        raise HTTPException(status_code=400, detail="At least one date (check-in or check-out) is required")
    
    uploaded_at = datetime.now(timezone.utc)
    file_name = None
    file_path = None
    
    # Handle document upload to Cloudflare R2
    if document_file:
        if not r2_client:
            raise HTTPException(status_code=503, detail="R2 storage not configured")
        
        file_ext = os.path.splitext(document_file.filename)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail="Invalid file type. Allowed: jpg, jpeg, png, pdf")
        
        content = await document_file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large. Maximum size: 5MB")
        
        # Upload to Cloudflare R2
        file_name = document_file.filename
        unique_name = f"{uuid.uuid4()}{file_ext}"
        file_path = f"documents/{unique_name}"
        
        # Determine content type
        content_types = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".pdf": "application/pdf"}
        content_type = content_types.get(file_ext, "application/octet-stream")
        
        try:
            upload_to_r2(content, file_path, content_type)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")
    
    # Calculate retention date
    retention_until = calculate_retention_date(check_out_date, uploaded_at)
    
    # Insert record
    record = {
        "guest_name": guest_name,
        "phone": phone,
        "booking_source": booking_source,
        "property_name": property_name,
        "check_in_date": check_in_date,
        "check_out_date": check_out_date,
        "notes": notes,
        "document_type": document_type,
        "file_name": file_name,
        "file_path": file_path,
        "uploaded_at": uploaded_at.isoformat(),
        "retention_until": retention_until,
        "status": "active"
    }
    
    try:
        result = supabase.table("guest_documents").insert(record).execute()
        return {"success": True, "record": result.data[0] if result.data else record}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create record: {str(e)}")


@app.get("/api/vault/guests")
def list_guest_records(
    search: str = Query(None, description="Search by name or phone"),
    property_name: str = Query(None),
    booking_source: str = Query(None),
    status: str = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0)
):
    """List guest records with filters"""
    if not supabase:
        raise HTTPException(status_code=503, detail="Supabase not configured")
    
    try:
        query = supabase.table("guest_documents").select("*")
        
        if search:
            query = query.or_(f"guest_name.ilike.%{search}%,phone.ilike.%{search}%")
        
        if property_name:
            query = query.eq("property_name", property_name)
        
        if booking_source:
            query = query.eq("booking_source", booking_source)
        
        if status:
            query = query.eq("status", status)
        
        result = query.order("created_at", desc=True).range(offset, offset + limit - 1).execute()
        
        # Mark records eligible for deletion
        today = datetime.now().strftime("%Y-%m-%d")
        records = []
        for r in result.data:
            if r["status"] == "active" and r["retention_until"] and r["retention_until"] < today:
                r["status"] = "eligible_for_deletion"
            records.append(r)
        
        return {"records": records, "count": len(records)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch records: {str(e)}")


@app.get("/api/vault/guests/{guest_id}")
def get_guest_record(guest_id: str):
    """Get a single guest record"""
    if not supabase:
        raise HTTPException(status_code=503, detail="Supabase not configured")
    
    try:
        result = supabase.table("guest_documents").select("*").eq("id", guest_id).single().execute()
        return result.data
    except Exception as e:
        raise HTTPException(status_code=404, detail="Record not found")


@app.get("/api/vault/guests/{guest_id}/document-url")
def get_document_url(guest_id: str):
    """Get a signed URL for the document from R2"""
    if not supabase:
        raise HTTPException(status_code=503, detail="Supabase not configured")
    if not r2_client:
        raise HTTPException(status_code=503, detail="R2 storage not configured")
    
    try:
        result = supabase.table("guest_documents").select("file_path").eq("id", guest_id).single().execute()
        
        if not result.data or not result.data.get("file_path"):
            raise HTTPException(status_code=404, detail="No document found")
        
        file_path = result.data["file_path"]
        
        # Create presigned URL from R2 (valid for 1 hour)
        signed_url = get_r2_presigned_url(file_path, 3600)
        return {"url": signed_url}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get document URL: {str(e)}")


@app.patch("/api/vault/guests/{guest_id}/soft-delete")
def soft_delete_guest(guest_id: str):
    """Soft delete a guest record (mark as deleted)"""
    if not supabase:
        raise HTTPException(status_code=503, detail="Supabase not configured")
    
    try:
        result = supabase.table("guest_documents").update({"status": "deleted"}).eq("id", guest_id).execute()
        return {"success": True, "message": "Record marked as deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete record: {str(e)}")


@app.delete("/api/vault/guests/{guest_id}/permanent")
def permanent_delete_guest(guest_id: str):
    """Permanently delete a guest record and its file from R2 (only if already soft-deleted)"""
    if not supabase:
        raise HTTPException(status_code=503, detail="Supabase not configured")
    
    try:
        # Check if already soft-deleted
        record = supabase.table("guest_documents").select("*").eq("id", guest_id).single().execute()
        
        if not record.data:
            raise HTTPException(status_code=404, detail="Record not found")
        
        if record.data.get("status") != "deleted":
            raise HTTPException(status_code=400, detail="Record must be soft-deleted first")
        
        # Delete file from R2 storage
        if record.data.get("file_path"):
            delete_from_r2(record.data["file_path"])
        
        # Delete record from Supabase
        supabase.table("guest_documents").delete().eq("id", guest_id).execute()
        return {"success": True, "message": "Record permanently deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete: {str(e)}")


@app.get("/api/vault/retention-review")
def retention_review():
    """Get records nearing expiry or eligible for deletion"""
    if not supabase:
        raise HTTPException(status_code=503, detail="Supabase not configured")
    
    try:
        today = datetime.now()
        thirty_days_later = (today + timedelta(days=30)).strftime("%Y-%m-%d")
        today_str = today.strftime("%Y-%m-%d")
        
        # Records expiring in next 30 days
        expiring_soon = supabase.table("guest_documents").select("*")\
            .eq("status", "active")\
            .gte("retention_until", today_str)\
            .lte("retention_until", thirty_days_later)\
            .order("retention_until")\
            .execute()
        
        # Records already eligible for deletion
        eligible = supabase.table("guest_documents").select("*")\
            .eq("status", "active")\
            .lt("retention_until", today_str)\
            .order("retention_until")\
            .execute()
        
        # Soft-deleted records
        deleted = supabase.table("guest_documents").select("*")\
            .eq("status", "deleted")\
            .order("updated_at", desc=True)\
            .execute()
        
        return {
            "expiring_soon": expiring_soon.data,
            "eligible_for_deletion": eligible.data,
            "soft_deleted": deleted.data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch: {str(e)}")


@app.get("/api/vault/properties")
def list_properties():
    """Get unique property names for filter dropdown"""
    if not supabase:
        raise HTTPException(status_code=503, detail="Supabase not configured")
    
    try:
        result = supabase.table("guest_documents").select("property_name").execute()
        properties = list(set([r["property_name"] for r in result.data if r.get("property_name")]))
        return {"properties": sorted(properties)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
