# MXYZ AI v0.1

Fondasi web app AI privat dengan UI chat, backend FastAPI, autentikasi HTTP Basic, dan adapter cloud AI opsional yang kompatibel dengan format OpenAI Chat Completions.

## Status v0.1

- UI web responsif bertema hitam-ungu.
- Akses privat dengan HTTP Basic Auth.
- Endpoint health dan chat.
- Mode demo jika provider belum dikonfigurasi.
- Integrasi cloud opsional melalui endpoint OpenAI-compatible.
- Kredensial provider hanya berada di backend.

Belum termasuk: model lokal, memori persisten/database, unggah file, vision, sandbox eksekusi kode, multi-user, dan TLS/reverse proxy otomatis.

## Jalankan lokal

1. Pasang Python 3.11+.
2. Salin `.env.example` menjadi `.env`.
3. Ubah `MXYZ_PASSWORD` menjadi password panjang dan unik.
4. Instal dependensi:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

   Windows PowerShell:

   ```powershell
   py -m venv .venv
   .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

5. Jalankan:

   ```bash
   uvicorn app.main:app --host 127.0.0.1 --port 8000
   ```

6. Buka `http://127.0.0.1:8000`. Browser akan meminta username dan password.

## Aktifkan Cloud AI

Isi `.env` menggunakan URL dasar provider OpenAI-compatible, API key, dan nama model:

```env
AI_BASE_URL=https://provider.example/v1
AI_API_KEY=YOUR_SECRET_KEY
AI_MODEL=model-name
```

Restart aplikasi setelah mengubah `.env`. Jangan pernah menaruh API key di frontend atau mengunggah `.env` ke Git.

## Deploy VPS dengan Docker

1. Salin folder proyek ke VPS.
2. Buat `.env` berdasarkan `.env.example`; gunakan password kuat.
3. Jalankan `docker compose up -d --build`.
4. Service hanya bind ke `127.0.0.1:8000`. Pasang reverse proxy Nginx/Caddy di depan dan aktifkan HTTPS.
5. Batasi firewall VPS agar hanya port SSH dan HTTPS yang terbuka. Jangan membuka port 8000 ke internet.

HTTP Basic Auth harus selalu digunakan melalui HTTPS saat diakses dari jaringan publik.

## Catatan keamanan

- Jangan gunakan password contoh di server.
- Simpan `.env` dengan permission terbatas dan backup yang aman.
- Tambahkan rate limiting dan monitoring sebelum penggunaan publik.
- v0.1 tidak mengeksekusi kode kiriman pengguna.
- Jangan menjalankan kode tak tepercaya di proses backend.
- Mode demo bukan model AI; jawaban AI aktif setelah provider dikonfigurasi.
