-- Supabase SQL Schema for Guest ID Vault
-- Run this in your Supabase SQL Editor

-- Create the guest_documents table
CREATE TABLE IF NOT EXISTS guest_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    guest_name TEXT NOT NULL,
    phone TEXT,
    booking_source TEXT DEFAULT 'direct', -- airbnb, direct, makemytrip, other
    property_name TEXT,
    check_in_date DATE,
    check_out_date DATE,
    notes TEXT,
    document_type TEXT, -- aadhaar, passport, driving_license, other
    file_name TEXT,
    file_path TEXT,
    uploaded_at TIMESTAMPTZ DEFAULT NOW(),
    retention_until DATE NOT NULL,
    status TEXT DEFAULT 'active', -- active, eligible_for_deletion, deleted
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for common queries
CREATE INDEX idx_guest_documents_guest_name ON guest_documents(guest_name);
CREATE INDEX idx_guest_documents_phone ON guest_documents(phone);
CREATE INDEX idx_guest_documents_property ON guest_documents(property_name);
CREATE INDEX idx_guest_documents_status ON guest_documents(status);
CREATE INDEX idx_guest_documents_retention ON guest_documents(retention_until);

-- Function to auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for updated_at
CREATE TRIGGER update_guest_documents_updated_at
    BEFORE UPDATE ON guest_documents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Storage bucket setup (run separately or via Supabase Dashboard)
-- Go to Storage > Create new bucket > Name: "guest-id-documents" > Make it private

-- RLS Policies (enable RLS first, then add policies)
-- For now, we use service_role key server-side which bypasses RLS
-- If you add auth later, uncomment and modify these:

-- ALTER TABLE guest_documents ENABLE ROW LEVEL SECURITY;

-- Policy for authenticated admin users (add when auth is set up):
-- CREATE POLICY "Admin full access" ON guest_documents
--     FOR ALL
--     TO authenticated
--     USING (auth.jwt() ->> 'role' = 'admin')
--     WITH CHECK (auth.jwt() ->> 'role' = 'admin');
