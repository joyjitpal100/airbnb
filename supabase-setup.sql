-- Supabase SQL Schema for Guest ID Vault
-- Run this in your Supabase SQL Editor

-- Create the guest_documents table
CREATE TABLE IF NOT EXISTS guest_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    guest_name TEXT NOT NULL,
    phone TEXT,
    booking_source TEXT DEFAULT 'direct',
    property_name TEXT,
    check_in_date DATE,
    check_out_date DATE,
    notes TEXT,
    document_type TEXT,
    file_name TEXT,
    file_path TEXT,  -- R2 object key (not public URL)
    uploaded_at TIMESTAMPTZ DEFAULT NOW(),
    retention_until DATE NOT NULL,
    status TEXT DEFAULT 'active',
    created_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_guest_documents_guest_name ON guest_documents(guest_name);
CREATE INDEX IF NOT EXISTS idx_guest_documents_phone ON guest_documents(phone);
CREATE INDEX IF NOT EXISTS idx_guest_documents_property ON guest_documents(property_name);
CREATE INDEX IF NOT EXISTS idx_guest_documents_status ON guest_documents(status);
CREATE INDEX IF NOT EXISTS idx_guest_documents_retention ON guest_documents(retention_until);
CREATE INDEX IF NOT EXISTS idx_guest_documents_created_by ON guest_documents(created_by);

-- Auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_guest_documents_updated_at ON guest_documents;
CREATE TRIGGER update_guest_documents_updated_at
    BEFORE UPDATE ON guest_documents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Enable RLS
ALTER TABLE guest_documents ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Only authenticated users can access
CREATE POLICY "Authenticated users can view all" ON guest_documents
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "Authenticated users can insert" ON guest_documents
    FOR INSERT TO authenticated WITH CHECK (true);

CREATE POLICY "Authenticated users can update" ON guest_documents
    FOR UPDATE TO authenticated USING (true);

CREATE POLICY "Authenticated users can delete" ON guest_documents
    FOR DELETE TO authenticated USING (true);

-- Note: File storage is handled by Cloudflare R2, not Supabase Storage
-- R2 bucket "guest-id-documents" should be PRIVATE (no public access)
-- Presigned URLs are generated server-side for secure downloads
