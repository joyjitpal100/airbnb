import { createClient } from '@supabase/supabase-js';
import { S3Client, PutObjectCommand, GetObjectCommand, DeleteObjectCommand } from '@aws-sdk/client-s3';
import { getSignedUrl } from '@aws-sdk/s3-request-presigner';

const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL;
const SUPABASE_ANON_KEY = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
const SUPABASE_SERVICE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;
const R2_ACCOUNT_ID = process.env.R2_ACCOUNT_ID;
const R2_ACCESS_KEY_ID = process.env.R2_ACCESS_KEY_ID;
const R2_SECRET_ACCESS_KEY = process.env.R2_SECRET_ACCESS_KEY;
const R2_BUCKET_NAME = process.env.R2_BUCKET_NAME || 'guest-id-documents';

export const RETENTION_YEARS = 7;
export const ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.pdf'];
export const MAX_FILE_SIZE = 5 * 1024 * 1024;

// Public config (safe to return to frontend)
export const SUPABASE_PUBLIC_URL = SUPABASE_URL || '';
export const SUPABASE_PUBLIC_ANON_KEY = SUPABASE_ANON_KEY || '';

// Server-side Supabase client (uses service role key for DB operations)
export const supabase = SUPABASE_URL && SUPABASE_SERVICE_KEY
  ? createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY)
  : null;

// R2 client (server-side only)
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

export const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization',
  'Access-Control-Allow-Methods': 'GET, POST, PATCH, DELETE, OPTIONS',
};

export const jsonResponse = (data, status = 200) => ({
  statusCode: status,
  headers: { ...corsHeaders, 'Content-Type': 'application/json' },
  body: JSON.stringify(data),
});

export const errorResponse = (message, status = 400) => ({
  statusCode: status,
  headers: { ...corsHeaders, 'Content-Type': 'application/json' },
  body: JSON.stringify({ error: message }),
});

export async function verifyAuth(authHeader) {
  if (!authHeader || !authHeader.startsWith('Bearer ')) return null;
  if (!supabase) return null;
  try {
    const token = authHeader.replace('Bearer ', '');
    const { data: { user }, error } = await supabase.auth.getUser(token);
    return error ? null : user;
  } catch {
    return null;
  }
}

export async function uploadToR2(fileBuffer, key, contentType) {
  if (!r2Client) throw new Error('R2 not configured');
  await r2Client.send(new PutObjectCommand({
    Bucket: R2_BUCKET,
    Key: key,
    Body: fileBuffer,
    ContentType: contentType,
  }));
  return key;
}

export async function getPresignedUrl(key, expiresIn = 3600) {
  if (!r2Client) throw new Error('R2 not configured');
  return await getSignedUrl(r2Client, new GetObjectCommand({
    Bucket: R2_BUCKET,
    Key: key,
  }), { expiresIn });
}

export async function deleteFromR2(key) {
  if (!r2Client) return false;
  try {
    await r2Client.send(new DeleteObjectCommand({ Bucket: R2_BUCKET, Key: key }));
    return true;
  } catch {
    return false;
  }
}

export function calculateRetentionDate(checkOutDate, uploadedAt = new Date()) {
  const baseDate = checkOutDate ? new Date(checkOutDate) : new Date(uploadedAt);
  const retentionDate = new Date(baseDate);
  retentionDate.setFullYear(retentionDate.getFullYear() + RETENTION_YEARS);
  return retentionDate.toISOString().split('T')[0];
}
