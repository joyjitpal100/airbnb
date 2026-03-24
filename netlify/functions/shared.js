// Shared utilities for Netlify Functions
import { createClient } from '@supabase/supabase-js';
import { S3Client, PutObjectCommand, GetObjectCommand, DeleteObjectCommand } from '@aws-sdk/client-s3';
import { getSignedUrl } from '@aws-sdk/s3-request-presigner';

// Environment variables (set in Netlify Dashboard)
const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_SERVICE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;
const R2_ACCOUNT_ID = process.env.R2_ACCOUNT_ID;
const R2_ACCESS_KEY_ID = process.env.R2_ACCESS_KEY_ID;
const R2_SECRET_ACCESS_KEY = process.env.R2_SECRET_ACCESS_KEY;
const R2_BUCKET_NAME = process.env.R2_BUCKET_NAME || 'guest-id-documents';

// Retention years
export const RETENTION_YEARS = 7;

// Allowed file types
export const ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.pdf'];
export const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB

// Initialize Supabase client (service role for server-side)
export const supabase = SUPABASE_URL && SUPABASE_SERVICE_KEY 
  ? createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY)
  : null;

// Initialize R2 client
export const r2Client = R2_ACCOUNT_ID && R2_ACCESS_KEY_ID && R2_SECRET_ACCESS_KEY
  ? new S3Client({
      region: 'auto',
      endpoint: `https://${R2_ACCOUNT_ID}.r2.cloudflarestorage.com`,
      credentials: {
        accessKeyId: R2_ACCESS_KEY_ID,
        secretAccessKey: R2_SECRET_ACCESS_KEY,
      },
    })
  : null;

export const R2_BUCKET = R2_BUCKET_NAME;

// CORS headers
export const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization',
  'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
};

// JSON response helper
export const jsonResponse = (data, status = 200) => ({
  statusCode: status,
  headers: { ...corsHeaders, 'Content-Type': 'application/json' },
  body: JSON.stringify(data),
});

// Error response helper
export const errorResponse = (message, status = 400) => ({
  statusCode: status,
  headers: { ...corsHeaders, 'Content-Type': 'application/json' },
  body: JSON.stringify({ error: message }),
});

// Verify Supabase Auth token
export async function verifyAuth(authHeader) {
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return null;
  }
  
  const token = authHeader.replace('Bearer ', '');
  
  if (!supabase) {
    return null;
  }
  
  try {
    const { data: { user }, error } = await supabase.auth.getUser(token);
    if (error || !user) {
      return null;
    }
    return user;
  } catch (e) {
    return null;
  }
}

// Upload file to R2 (private, no public URL)
export async function uploadToR2(fileBuffer, key, contentType) {
  if (!r2Client) {
    throw new Error('R2 not configured');
  }
  
  await r2Client.send(new PutObjectCommand({
    Bucket: R2_BUCKET,
    Key: key,
    Body: fileBuffer,
    ContentType: contentType,
  }));
  
  return key;
}

// Get presigned URL for private download (expires in 1 hour)
export async function getPresignedUrl(key, expiresIn = 3600) {
  if (!r2Client) {
    throw new Error('R2 not configured');
  }
  
  const command = new GetObjectCommand({
    Bucket: R2_BUCKET,
    Key: key,
  });
  
  return await getSignedUrl(r2Client, command, { expiresIn });
}

// Delete file from R2
export async function deleteFromR2(key) {
  if (!r2Client) {
    return false;
  }
  
  try {
    await r2Client.send(new DeleteObjectCommand({
      Bucket: R2_BUCKET,
      Key: key,
    }));
    return true;
  } catch (e) {
    return false;
  }
}

// Calculate retention date (7 years from check_out or upload)
export function calculateRetentionDate(checkOutDate, uploadedAt = new Date()) {
  const baseDate = checkOutDate ? new Date(checkOutDate) : new Date(uploadedAt);
  const retentionDate = new Date(baseDate);
  retentionDate.setFullYear(retentionDate.getFullYear() + RETENTION_YEARS);
  return retentionDate.toISOString().split('T')[0];
}
