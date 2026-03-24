import Busboy from 'busboy';
import {
  supabase, r2Client, corsHeaders, jsonResponse, errorResponse, verifyAuth,
  uploadToR2, getPresignedUrl, deleteFromR2, calculateRetentionDate,
  ALLOWED_EXTENSIONS, MAX_FILE_SIZE, RETENTION_YEARS, R2_BUCKET,
  SUPABASE_PUBLIC_URL, SUPABASE_PUBLIC_ANON_KEY,
} from './shared.js';

function parseMultipart(event) {
  return new Promise((resolve, reject) => {
    const fields = {};
    let fileData = null;

    const contentType = event.headers['content-type'] || event.headers['Content-Type'];
    if (!contentType || !contentType.includes('multipart/form-data')) {
      if (event.body) {
        try {
          const parsed = JSON.parse(event.isBase64Encoded
            ? Buffer.from(event.body, 'base64').toString()
            : event.body);
          resolve({ fields: parsed, file: null });
        } catch {
          resolve({ fields: {}, file: null });
        }
      } else {
        resolve({ fields: {}, file: null });
      }
      return;
    }

    const busboy = Busboy({ headers: { 'content-type': contentType } });

    busboy.on('field', (name, value) => { fields[name] = value; });

    busboy.on('file', (name, stream, info) => {
      const chunks = [];
      stream.on('data', chunk => chunks.push(chunk));
      stream.on('end', () => {
        fileData = {
          buffer: Buffer.concat(chunks),
          filename: info.filename,
          mimeType: info.mimeType,
        };
      });
    });

    busboy.on('finish', () => resolve({ fields, file: fileData }));
    busboy.on('error', reject);

    const body = event.isBase64Encoded
      ? Buffer.from(event.body, 'base64')
      : Buffer.from(event.body || '');
    busboy.end(body);
  });
}

export async function handler(event) {
  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 204, headers: corsHeaders };
  }

  const path = event.path.replace('/.netlify/functions/vault', '').replace('/api/vault', '');
  const method = event.httpMethod;

  // Public config endpoint (no auth) - returns only public Supabase config
  if (path === '/config' && method === 'GET') {
    return jsonResponse({
      supabase_url: SUPABASE_PUBLIC_URL,
      supabase_anon_key: SUPABASE_PUBLIC_ANON_KEY,
    });
  }

  // Status endpoint (no auth)
  if (path === '/status' && method === 'GET') {
    return jsonResponse({
      configured: !!supabase && !!r2Client,
      supabase_configured: !!supabase,
      r2_configured: !!r2Client,
      retention_years: RETENTION_YEARS,
      storage_bucket: R2_BUCKET,
    });
  }

  // All other endpoints require authentication
  const user = await verifyAuth(event.headers.authorization || event.headers.Authorization);
  if (!user) {
    return errorResponse('Unauthorized. Please sign in.', 401);
  }

  if (!supabase) {
    return errorResponse('Supabase not configured', 503);
  }

  try {
    // GET /guests
    if (path === '/guests' && method === 'GET') {
      const params = event.queryStringParameters || {};
      let query = supabase.table('guest_documents').select('*');

      if (params.search) {
        query = query.or(`guest_name.ilike.%${params.search}%,phone.ilike.%${params.search}%`);
      }
      if (params.property_name) query = query.eq('property_name', params.property_name);
      if (params.booking_source) query = query.eq('booking_source', params.booking_source);
      if (params.status) query = query.eq('status', params.status);

      const limit = Math.min(parseInt(params.limit) || 50, 100);
      const offset = parseInt(params.offset) || 0;

      const { data, error } = await query
        .order('created_at', { ascending: false })
        .range(offset, offset + limit - 1);

      if (error) throw error;

      const today = new Date().toISOString().split('T')[0];
      const records = data.map(r => ({
        ...r,
        status: r.status === 'active' && r.retention_until < today ? 'eligible_for_deletion' : r.status,
      }));

      return jsonResponse({ records, count: records.length });
    }

    // POST /guests
    if (path === '/guests' && method === 'POST') {
      const { fields, file } = await parseMultipart(event);

      if (!fields.guest_name) return errorResponse('Guest name is required');
      if (!fields.check_in_date && !fields.check_out_date) return errorResponse('At least one date required');

      let file_name = null;
      let file_path = null;

      if (file && file.buffer.length > 0) {
        if (!r2Client) return errorResponse('R2 storage not configured', 503);
        const ext = '.' + file.filename.split('.').pop().toLowerCase();
        if (!ALLOWED_EXTENSIONS.includes(ext)) return errorResponse('Invalid file type. Allowed: jpg, jpeg, png, pdf');
        if (file.buffer.length > MAX_FILE_SIZE) return errorResponse('File too large. Max 5MB');

        file_name = file.filename;
        file_path = `documents/${crypto.randomUUID()}${ext}`;
        await uploadToR2(file.buffer, file_path, file.mimeType);
      }

      const now = new Date().toISOString();
      const record = {
        guest_name: fields.guest_name,
        phone: fields.phone || null,
        booking_source: fields.booking_source || 'direct',
        property_name: fields.property_name || null,
        check_in_date: fields.check_in_date || null,
        check_out_date: fields.check_out_date || null,
        notes: fields.notes || null,
        document_type: fields.document_type || null,
        file_name,
        file_path,
        uploaded_at: now,
        retention_until: calculateRetentionDate(fields.check_out_date, now),
        status: 'active',
        created_by: user.id,
      };

      const { data, error } = await supabase.table('guest_documents').insert(record).select().single();
      if (error) throw error;

      return jsonResponse({ success: true, record: data });
    }

    // GET /guests/:id
    const singleMatch = path.match(/^\/guests\/([a-f0-9-]+)$/);
    if (singleMatch && method === 'GET') {
      const { data, error } = await supabase
        .table('guest_documents').select('*').eq('id', singleMatch[1]).single();
      if (error || !data) return errorResponse('Record not found', 404);
      return jsonResponse(data);
    }

    // GET /guests/:id/document-url
    const docUrlMatch = path.match(/^\/guests\/([a-f0-9-]+)\/document-url$/);
    if (docUrlMatch && method === 'GET') {
      if (!r2Client) return errorResponse('R2 not configured', 503);
      const { data, error } = await supabase
        .table('guest_documents').select('file_path').eq('id', docUrlMatch[1]).single();
      if (error || !data?.file_path) return errorResponse('No document found', 404);
      const url = await getPresignedUrl(data.file_path, 3600);
      return jsonResponse({ url });
    }

    // PATCH /guests/:id/soft-delete
    const softDelMatch = path.match(/^\/guests\/([a-f0-9-]+)\/soft-delete$/);
    if (softDelMatch && method === 'PATCH') {
      const { error } = await supabase
        .table('guest_documents')
        .update({ status: 'deleted', updated_at: new Date().toISOString() })
        .eq('id', softDelMatch[1]);
      if (error) throw error;
      return jsonResponse({ success: true, message: 'Record marked as deleted' });
    }

    // DELETE /guests/:id/permanent
    const permDelMatch = path.match(/^\/guests\/([a-f0-9-]+)\/permanent$/);
    if (permDelMatch && method === 'DELETE') {
      const { data: record, error: fetchErr } = await supabase
        .table('guest_documents').select('*').eq('id', permDelMatch[1]).single();
      if (fetchErr || !record) return errorResponse('Record not found', 404);
      if (record.status !== 'deleted') return errorResponse('Must soft-delete first');

      if (record.file_path) await deleteFromR2(record.file_path);
      await supabase.table('guest_documents').delete().eq('id', permDelMatch[1]);
      return jsonResponse({ success: true, message: 'Permanently deleted' });
    }

    // GET /retention-review
    if (path === '/retention-review' && method === 'GET') {
      const today = new Date();
      const todayStr = today.toISOString().split('T')[0];
      const thirtyDays = new Date(today.getTime() + 30 * 86400000).toISOString().split('T')[0];

      const [expiring, eligible, deleted] = await Promise.all([
        supabase.table('guest_documents').select('*')
          .eq('status', 'active').gte('retention_until', todayStr).lte('retention_until', thirtyDays)
          .order('retention_until'),
        supabase.table('guest_documents').select('*')
          .eq('status', 'active').lt('retention_until', todayStr)
          .order('retention_until'),
        supabase.table('guest_documents').select('*')
          .eq('status', 'deleted').order('updated_at', { ascending: false }),
      ]);

      return jsonResponse({
        expiring_soon: expiring.data || [],
        eligible_for_deletion: eligible.data || [],
        soft_deleted: deleted.data || [],
      });
    }

    // GET /properties
    if (path === '/properties' && method === 'GET') {
      const { data } = await supabase.table('guest_documents').select('property_name');
      const properties = [...new Set(data?.filter(r => r.property_name).map(r => r.property_name))].sort();
      return jsonResponse({ properties });
    }

    return errorResponse('Not found', 404);

  } catch (err) {
    console.error('Vault error:', err);
    return errorResponse(err.message || 'Internal error', 500);
  }
}
