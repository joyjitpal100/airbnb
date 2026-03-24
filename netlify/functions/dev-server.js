/**
 * Dev server that wraps the Netlify vault function for local testing.
 * This file is NOT deployed to Netlify - it's for the preview environment only.
 * It loads env vars from /app/backend/.env, then serves the vault handler via HTTP.
 */
import http from 'http';
import { readFileSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const envPath = resolve(__dirname, '../../backend/.env');

try {
  const envContent = readFileSync(envPath, 'utf-8');
  envContent.split('\n').forEach(line => {
    const trimmed = line.trim();
    if (trimmed && !trimmed.startsWith('#')) {
      const eqIndex = trimmed.indexOf('=');
      if (eqIndex > 0) {
        const key = trimmed.substring(0, eqIndex);
        const value = trimmed.substring(eqIndex + 1);
        if (!process.env[key]) {
          process.env[key] = value;
        }
      }
    }
  });
} catch (e) {
  console.warn('Could not load .env file:', e.message);
}

const { handler } = await import('./vault.js');

const PORT = 8002;

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://localhost:${PORT}`);

  const chunks = [];
  req.on('data', chunk => chunks.push(chunk));

  req.on('end', async () => {
    const body = Buffer.concat(chunks);

    const event = {
      httpMethod: req.method,
      path: url.pathname,
      headers: req.headers,
      queryStringParameters: Object.fromEntries(url.searchParams),
      body: body.length > 0 ? body.toString('base64') : null,
      isBase64Encoded: body.length > 0,
    };

    try {
      const response = await handler(event);
      const headers = response.headers || {};
      for (const [key, value] of Object.entries(headers)) {
        res.setHeader(key, value);
      }
      res.writeHead(response.statusCode);
      res.end(response.body);
    } catch (err) {
      console.error('Dev server error:', err);
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: err.message }));
    }
  });
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`Vault dev server running on http://localhost:${PORT}`);
});
