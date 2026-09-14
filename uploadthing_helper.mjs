import { UTApi } from 'uploadthing/server';
import fs from 'fs';

// Retrieve UPLOADTHING_TOKEN from environment
let token = process.env.UPLOADTHING_TOKEN || '';
token = token.trim().replace(/^['"]|['"]$/g, '');

if (!token) {
  process.stdout.write(JSON.stringify({ ok: false, error: 'UPLOADTHING_TOKEN is not configured in .env' }));
  process.exit(1);
}

const utapi = new UTApi({ token });

async function upload() {
  const filePath = process.argv[2];
  const fileName = process.argv[3] || 'file.bin';
  const fileType = process.argv[4] || 'application/octet-stream';

  if (!filePath || !fs.existsSync(filePath)) {
    process.stdout.write(JSON.stringify({ ok: false, error: `Temporary file not found: ${filePath}` }));
    process.exit(1);
  }

  const fileBuffer = fs.readFileSync(filePath);
  const file = new File([fileBuffer], fileName, { type: fileType });

  const result = await utapi.uploadFiles(file);

  if (result.error) {
    process.stdout.write(JSON.stringify({ ok: false, error: result.error.message || String(result.error) }));
    process.exit(1);
  }

  if (!result.data) {
    process.stdout.write(JSON.stringify({ ok: false, error: 'UploadThing returned no data' }));
    process.exit(1);
  }

  const publicUrl = result.data.ufsUrl || result.data.url;
  process.stdout.write(JSON.stringify({
    ok: true,
    url: publicUrl,
    key: result.data.key,
    name: result.data.name,
    size: result.data.size
  }));
}

upload().catch(err => {
  process.stdout.write(JSON.stringify({ ok: false, error: err.message || String(err) }));
  process.exit(1);
});
